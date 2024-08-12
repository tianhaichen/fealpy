
from typing import Optional, Union, overload, List, Tuple
from math import prod

from ..backend import TensorLike, Number, Size
from ..backend import backend_manager as bm
from .sparse_tensor import SparseTensor
from .utils import (
    _flatten_indices,
    check_shape_match, check_spshape_match
)
from ._spspmm import spspmm_coo
from ._spmm import spmm_coo


class COOTensor(SparseTensor):
    def __init__(self, indices: TensorLike, values: Optional[TensorLike],
                 spshape: Optional[Size]=None, *,
                 is_coalesced: Optional[bool]=None):
        """
        Initialize COO format sparse tensor.

        Parameters:
            indices (Tensor): indices of non-zero elements, shaped (D, N).
                Where D is the number of sparse dimension, and N is the number
                of non-zeros (nnz).
            values (Tensor | None): non-zero elements, shaped (..., N).
            spshape (Size | None, optional): shape in the sparse dimensions.
        """
        self._indices = indices
        self._values = values
        self.is_coalesced = is_coalesced

        if spshape is None:
            self._spshape = (bm.max(indices, axis=1) + 1,)
        else:
            self._spshape = tuple(spshape)

        self._check(indices, values, spshape)

    def _check(self, indices: TensorLike, values: Optional[TensorLike], spshape: Size):
        if not isinstance(indices, TensorLike):
            raise TypeError(f"indices must be a Tensor, but got {type(indices)}")
        if indices.ndim != 2:
            raise ValueError(f"indices must be a 2D tensor, but got {indices.ndim}D")

        # total ndim should be equal to sparse_ndim + dense_dim
        if len(spshape) != indices.shape[0]:
            raise ValueError(f"size must have length {indices.shape[0]}, "
                             f"but got {len(spshape)}")

        if isinstance(values, TensorLike):
            if values.ndim < 1:
                raise ValueError(f"values must be at least 1D, but got {values.ndim}D")

            # The last dim of values must match the last dim of indices.
            if values.shape[-1] != indices.shape[1]:
                raise ValueError(f"values must have the same size as indices ({indices.shape[1]}) "
                                 "in the last dimension (number of non-zero elements), "
                                 f"but got {values.shape[-1]}")
        elif values is None:
            pass
        else:
            raise TypeError(f"values must be a Tensor or None, but got {type(values)}")

    def __repr__(self) -> str:
        return f"COOTensor(indices={self._indices}, values={self._values}, shape={self.shape})"

    @property
    def itype(self): return self._indices.dtype

    @property
    def nnz(self): return self._indices.shape[1]

    @property
    def nonzero_slice(self) -> Tuple[Union[slice, TensorLike]]:
        slicing = [self._indices[i] for i in range(self.sparse_ndim)]
        return (slice(None),) * self.dense_ndim + tuple(slicing)

    def indices(self) -> TensorLike:
        """Return the indices of the non-zero elements."""
        return self._indices

    def values(self) -> Optional[TensorLike]:
        """Return the non-zero elements."""
        return self._values

    def to_dense(self, *, fill_value: Number=1.0, **kwargs) -> TensorLike:
        """Convert the COO tensor to a dense tensor and return as a new object.

        Parameters:
            fill_value (int | float, optional): The value to fill the dense tensor with
                when `self.values()` is None.

        Returns:
            Tensor: dense tensor.
        """
        if not self.is_coalesced:
            raise ValueError("indices must be coalesced before calling to_dense()")

        context = self.values_context()
        context.update(kwargs)
        dense_tensor = bm.zeros(self.shape, **context)

        if self._values is None:
            dense_tensor[self.nonzero_slice] = fill_value
        else:
            dense_tensor[self.nonzero_slice] = self._values

        return dense_tensor

    toarray = to_dense

    def coalesce(self, accumulate: bool=True) -> 'COOTensor':
        """Merge duplicate indices and return as a new COOTensor object.
        Returns self if the indices are already coalesced.

        Parameters:
            accumulate (bool, optional): Whether to count the occurrences of indices\
            as new values when `self.values` is None. Defaults to True.

        Returns:
            COOTensor: coalesced COO tensor.
        """
        if self.is_coalesced:
            return self

        unique_indices, inverse_indices = bm.unique(
            self._indices, return_inverse=True, axis=1
        )

        if self._values is not None:
            value_shape = self.dense_shape + (unique_indices.shape[-1], )
            new_values = bm.zeros(value_shape, **self.values_context())
            new_values = bm.index_add_(new_values, -1, inverse_indices, self._values)

            return COOTensor(
                unique_indices, new_values, self.sparse_shape, is_coalesced=True
            )

        else:
            if accumulate:
                kwargs = bm.context(self._indices)
                ones = bm.ones((self.nnz, ), **kwargs)
                new_values = bm.zeros((unique_indices.shape[-1], ), **kwargs)
                new_values = bm.index_add_(new_values, -1, inverse_indices, ones)
            else:
                new_values = None

            return COOTensor(
                unique_indices, new_values, self.sparse_shape, is_coalesced=True
            )

    @overload
    def reshape(self, shape: Size, /) -> 'COOTensor': ...
    @overload
    def reshape(self, *shape: int) -> 'COOTensor': ...
    def reshape(self, *shape) -> 'COOTensor':
        pass

    def ravel(self):
        """Return a view with flatten indices on sparse dimensions.

        Returns:
            COOTensor: A flatten COO tensor, shaped (*dense_shape, nnz).
        """
        spshape = self.sparse_shape
        new_indices = _flatten_indices(self._indices, spshape)
        return COOTensor(new_indices, self._values, (prod(spshape),))

    def flatten(self):
        """Return a copy with flatten indices on sparse dimensions.

        Returns:
            COOTensor: A flatten COO tensor, shaped (*dense_shape, nnz).
        """
        spshape = self.sparse_shape
        new_indices = _flatten_indices(self._indices, spshape)
        if self._values is None:
            values = None
        else:
            values = bm.copy(self._values)
        return COOTensor(new_indices, values, (prod(spshape),))

    def copy(self):
        return COOTensor(bm.copy(self._indices), bm.copy(self._values), self.sparse_shape)

    def neg(self) -> 'COOTensor':
        """Negation of the COO tensor. Returns self if values is None."""
        if self._values is None:
            return self
        else:
            return COOTensor(self._indices, -self._values, self.sparse_shape)

    @overload
    def add(self, other: Union[Number, 'COOTensor'], alpha: Number=1) -> 'COOTensor': ...
    @overload
    def add(self, other: TensorLike, alpha: Number=1) -> TensorLike: ...
    def add(self, other: Union[Number, 'COOTensor', TensorLike], alpha: Number=1) -> Union['COOTensor', TensorLike]:
        """Adds another tensor or scalar to this COOTensor, with an optional scaling factor.

        Parameters:
            other (Number | COOTensor | Tensor): The tensor or scalar to be added.\n
            alpha (float, optional): The scaling factor for the other tensor. Defaults to 1.0.

        Raises:
            TypeError: If the type of `other` is not supported for addition.\n
            ValueError: If the shapes of `self` and `other` are not compatible.\n
            ValueError: If one has value and another does not.

        Returns:
            out (COOTensor | Tensor): A new COOTensor if `other` is a COOTensor,\
            or a Tensor if `other` is a dense tensor.
        """
        if isinstance(other, COOTensor):
            check_shape_match(self.shape, other.shape)
            check_spshape_match(self.sparse_shape, other.sparse_shape)
            new_indices = bm.concat((self._indices, other._indices), axis=1)
            if self._values is None:
                if other._values is None:
                    new_values = None
                else:
                    raise ValueError("self has no value while other does")
            else:
                if other._values is None:
                    raise ValueError("self has value while other does not")
                new_values = bm.concat((self._values, other._values*alpha), axis=-1)
            return COOTensor(new_indices, new_values, self.sparse_shape)

        elif isinstance(other, TensorLike):
            check_shape_match(self.shape, other.shape)
            output = other * alpha
            if self._values is None:
                output[self.nonzero_slice] += 1.
            else:
                output[self.nonzero_slice] += self._values
            return output

        elif isinstance(other, (int, float)):
            new_values = self._values + alpha * other
            return COOTensor(bm.copy(self._indices), new_values, self.sparse_shape)

        else:
            raise TypeError(f"Unsupported type {type(other).__name__} in addition")

    def mul(self, other: Union[Number, 'COOTensor', TensorLike]) -> 'COOTensor': # TODO: finish this
        """Element-wise multiplication.
        The result COO tensor will share the same indices with
        the original if `other` is a number or a dense tensor.
        """
        if isinstance(other, COOTensor):
            pass

        elif isinstance(other, TensorLike):
            check_shape_match(self.shape, other.shape)
            new_values = bm.copy(other[self.nonzero_slice])
            if self._values is not None:
                bm.multiply(self._values, new_values, out=new_values)
            return COOTensor(self._indices, new_values, self.sparse_shape)

        elif isinstance(other, (int, float)):
            if self._values is None:
                raise ValueError("Cannot multiply COOTensor without value with scalar")
            new_values = self._values * other
            return COOTensor(self._indices, new_values, self.sparse_shape)

        else:
            raise TypeError(f"Unsupported type {type(other).__name__} in multiplication")

    def div(self, other: Union[Number, TensorLike]) -> 'COOTensor':
        """Element-wise division.
        The result COO tensor will share the same indices with
        the original if `other` is a number or a dense tensor.
        """
        if self._values is None:
                raise ValueError("Cannot divide COOTensor without value")

        if isinstance(other, TensorLike):
            check_shape_match(self.shape, other.shape)
            new_values = bm.copy(other[self.nonzero_slice])
            bm.divide(self._values, new_values, out=new_values)
            return COOTensor(self._indices, new_values, self.sparse_shape)

        elif isinstance(other, (int, float)):
            new_values = self._values / other
            return COOTensor(self._indices, new_values, self.sparse_shape)

        else:
            raise TypeError(f"Unsupported type {type(other).__name__} in division")

    def pow(self, other: Union[TensorLike, Number]) -> 'COOTensor':
        """Element-wise power of COOTensor.
        The result COO tensor will share the same indices with
        the original if `other` is a number or a dense tensor.
        """
        if self._values is None:
            raise ValueError("Cannot power COOTensor without value with tensor")

        if isinstance(other, TensorLike):
            check_shape_match(self.shape, other.shape)
            new_values = bm.power(self._values, other[self.nonzero_slice])
            return COOTensor(self._indices, new_values, self.sparse_shape)

        elif isinstance(other, (int, float)):
            new_values = self._values ** other
            return COOTensor(self._indices, new_values, self.sparse_shape)

        else:
            raise TypeError(f'Unsupported type {type(other).__name__} in power')

    def inner(self, other: TensorLike, dims: List[int]) -> 'COOTensor':
        pass

    @overload
    def matmul(self, other: 'COOTensor') -> 'COOTensor': ...
    @overload
    def matmul(self, other: TensorLike) -> TensorLike: ...
    def matmul(self, other: Union['COOTensor', TensorLike]):
        """Matrix-multiply this COOTensor with another tensor.

        Parameters:
            other (COOTensor | Tensor): A 1-D tensor for matrix-vector multiply,
                or a 2-D tensor for matrix-matrix multiply.
                Batched matrix-matrix multiply is available for dimensions
                (*B, M, K) and (*B, K, N). *B means any number of batch dimensions.

        Raises:
            TypeError: If the type of `other` is not supported for matmul.

        Returns:
            out (COOTensor | Tensor): A new COOTensor if `other` is a COOTensor,\
            or a Tensor if `other` is a dense tensor.
        """
        if isinstance(other, COOTensor):
            if (self.values() is None) or (other.values() is None):
                raise ValueError("Matrix multiplication between COOTensor without "
                                 "value is not implemented now")
            indices, values, spshape = spspmm_coo(
                self.indices(), self.values(), self.sparse_shape,
                other.indices(), other.values(), other.sparse_shape,
            )
            return COOTensor(indices, values, spshape).coalesce()

        elif isinstance(other, TensorLike):
            if self.values() is None:
                raise ValueError()
            return spmm_coo(self.indices(), self.values(), self.sparse_shape, other)

        else:
            raise TypeError(f"Unsupported type {type(other).__name__} in matmul")
