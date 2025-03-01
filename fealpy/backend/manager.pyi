
from typing import (
    Union, Optional, Any, Callable, Sequence, Iterable, Tuple, List, Dict,
    Literal, TypeGuard, overload, TypeVar
)

from .base import BackendProxy, Size, Number
from .base import TensorLike as _DT

Axes = Union[int, Tuple[Optional[int], ...], None]
_FT = TypeVar('_FT', bound=Callable)
VJP_Fn = Callable[[_DT], Tuple[_DT, ...]]

"""
This class serves as an interface for the computation backend.
All methods in this class are static methods by default,
unless explicitly annotated otherwise.
"""


class SparseModule():
    pass


class RandomModule():
    def seed(self, seed: int, /) -> None: ...
    def rand(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...
    def randint(self, low: int, high: Optional[int] = None, shape: Optional[Size] = None, *,
                dtype=None, device=None) -> _DT: ...
    def randn(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...


class LinalgModule():
    def cholesky(self, x: _DT, /, *, upper: bool = False) -> _DT: ...
    def cross(self, x1: _DT, x2: _DT, /, *, axis: int = -1) -> _DT: ...
    def det(self, x: _DT, /) -> _DT: ...
    def diagonal(self, x: _DT, /, *, offset: int = 0) -> _DT: ...
    def eigh(self, x: _DT, /) -> Tuple[_DT, _DT]: ...
    def eigvalsh(self, x: _DT, /) -> _DT: ...
    def inv(self, x: _DT, /) -> _DT: ...
    def matmul(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def matrix_norm(self, x: _DT, /, *, keepdims: bool = False,
                    ord: Union[int, float, Literal['fro', 'nuc']] = 'fro') -> _DT: ...
    def matrix_power(self, x: _DT, n: Number, /) -> _DT: ...
    def matrix_rank(self, x: _DT, /, *, rtol=None) -> _DT: ...
    def matrix_transpose(self, x: _DT, /) -> _DT: ...
    def outer(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def pinv(self, x: _DT, /, *, rtol=None) -> _DT: ...
    def qr(self, x: _DT, /, *, mode='reduced') -> _DT: ...
    def slogdet(self, x: _DT, /) -> _DT: ...
    def solve(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def svd(self, x: _DT, /, *, full_matrices: bool = True) -> Tuple[_DT, _DT, _DT]: ...
    def svdvals(self, x: _DT, /) -> _DT: ...
    def tensordot(self, x1: _DT, x2: _DT, /, *, axes: Union[int, Tuple[Sequence[int], Sequence[int]]] = 2) -> _DT: ...
    def trace(self, x: _DT, /, *, offset=0, dtype=None) -> _DT: ...
    def vecdot(self, x1: _DT, x2: _DT, /, *, axis: Axes = None) -> _DT: ...
    def vector_norm(self, x: _DT, /, *, axis: Optional[int] = None, keepdims: bool = False,
                    ord: Union[int, float, Literal['inf', '-inf', 'fro']] = 2) -> _DT: ...


class BackendManager():
    backend_name: Literal['numpy', 'pytorch', 'jax', 'mindspore', 'paddle', 'taichi', 'cupy']
    def __init__(self, *, default_backend: Optional[str]=None): ... # instance method
    def set_backend(self, name: str) -> None: ... # instance method
    def load_backend(self, name: str) -> None: ... # instance method
    def get_current_backend(self) -> BackendProxy: ... # instance method

    ### constants ###

    pi: float
    e: float
    nan: float
    inf: float
    newaxis: Any
    dtype: type
    device: type
    bool: Any
    uint8: Any
    uint16: Any
    uint32: Any
    uint64: Any
    int8: Any
    int16: Any
    int32: Any
    int64: Any
    float16: Any
    float32: Any
    float64: Any
    complex64: Any
    complex128: Any

    ### Backend tools ###
    def is_tensor(self, obj: Any, /) -> TypeGuard[_DT]: ...
    def context(self, tensor: _DT, /) -> Dict[str, Any]: ...
    def set_default_device(self, device: Any) -> None: ...
    def device_type(self, tensor_like: _DT, /) -> Literal['cpu', 'cuda', 'tpu', 'mps', 'vulkan', 'rocm', 'xla', 'hip', 'metal']: ...
    def device_index(self, tensor_like: _DT, /) -> int: ...
    def get_device(self, tensor_like: _DT, /) -> Any: ...
    def device_put(self, tensor: _DT, /, device: Optional[str] = None) -> _DT: ...
    def to_numpy(self, tensor_like: _DT, /) -> Any: ...
    def from_numpy(self, ndarray: Any, /) -> _DT: ...
    def tolist(self, tensor: _DT, /) -> List[Number]: ...

    ### Compiler ###
    @overload
    def compile(self, fun: Callable, /, *,
                fullgraph: bool=False, dynamic: Optional[bool]=None,
                backend: str='inductor', mode: str='default',
                options: Optional[Dict[str, Any]]=None, disable=False) -> Callable: ...
    @overload
    def compile(self, fun: Callable, /, *,
                static_argnums: Union[int, Sequence[int], None]=None,
                static_argnames: Union[str, Iterable[str], None]=None,
                donate_argnums: Union[int, Sequence[int], None]=None,
                donate_argnames: Union[str, Iterable[str], None]=None,
                keep_unused: bool=False,
                device=None, backend: Optional[str]=None, inline: bool=False,
                abstracted_axes=None) -> Callable: ...

    ### Creation Functions ###
    # python array API standard v2023.12
    @overload
    def arange(self, stop: Number, /, step: Number=1, *, dtype=None, device=None) -> _DT: ...
    @overload
    def arange(self, start: Number, /, stop: Number, step: Number=1, *, dtype=None, device=None) -> _DT: ...
    def asarray(self, obj, /, *, dtype=None, device=None, copy=None) -> _DT: ...
    def empty(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...
    def empty_like(self, x: _DT, /, *, dtype=None, device=None) -> _DT: ...
    def eye(self, n_rows: int, n_cols: Optional[int]=None, /, *, k: int=0, dtype=None, device=None) -> _DT: ...
    def from_dlpack(x: Any, /) -> _DT: ...
    def full(self, shape: Size, fill_value: Number, /, *, dtype=None, device=None) -> _DT: ...
    def full_like(self, x: _DT, fill_value: Number, /, *, dtype=None, device=None) -> _DT: ...
    def linspace(self, start: Number, stop: Number, /, num: int, *, dtype=None, device=None, endpoint=True) -> _DT: ... 
    def meshgrid(self, *arrays: _DT, indexing='xy') -> Tuple[_DT, ...]: ...
    def ones(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...
    def ones_like(self, x: _DT, /, *, dtype=None, device=None) -> _DT: ...
    def tril(self, x: _DT, /, *, k: int=0) -> _DT: ...
    def triu(self, x: _DT, /, *, k: int=0) -> _DT: ...
    def zeros(self, shape: Size, /, *, dtype=None, device=None) -> _DT: ...
    def zeros_like(self, x: _DT, /, *, dtype=None, device=None) -> _DT: ...

    # non-standard
    def array(self, object, /, *, dtype=None, device=None, **kwargs) -> _DT: ...
    def tensor(self, data, /, *, dtype=None, device=None, **kwargs) -> _DT: ...

    ### Data Type Functions ###
    # python array API standard v2023.12
    def astype(self, x: _DT, dtype, /, *, copy=True, device=None) -> _DT: ...
    def can_cast(self, from_, to, /) -> _DT: ... # TODO
    def finfo(self, dtype, /) -> Any: ...
    def iinfo(self, dtype, /) -> Any: ...
    def isdtype(self, dtype, king) -> bool: ...
    def result_type(self, *arrays_and_dtypes) -> Any: ...

    ### Element-wise Functions ###
    # python array API standard v2023.12
    def abs(self, x: _DT, /) -> _DT: ...
    def acos(self, x: _DT, /) -> _DT: ...
    def acosh(self, x: _DT, /) -> _DT: ...
    def add(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def asin(self, x: _DT, /) -> _DT: ...
    def asinh(self, x: _DT, /) -> _DT: ...
    def atan(self, x: _DT, /) -> _DT: ...
    def atan2(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def atanh(self, x: _DT, /) -> _DT: ...
    def bitwise_and(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_left_shift(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_invert(self, x: _DT, /) -> _DT: ...
    def bitwise_or(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_right_shift(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def bitwise_xor(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def ceil(self, x: _DT, /) -> _DT: ...
    def clip(self, x: _DT, x_min: _DT, x_max: _DT, /) -> _DT: ...
    def conj(self, x: _DT, /) -> _DT: ...
    def copysign(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def cos(self, x: _DT, /) -> _DT: ...
    def cosh(self, x: _DT, /) -> _DT: ...
    def divide(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def exp(self, x: _DT, /) -> _DT: ...
    def expm1(self, x: _DT, /) -> _DT: ...
    def floor(self, x: _DT, /) -> _DT: ...
    def floor_divide(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def greater(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def greater_equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def hypot(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def imag(self, x: _DT, /) -> _DT: ...
    def isfinite(self, x: _DT, /) -> _DT: ...
    def isinf(self, x: _DT, /) -> _DT: ...
    def isnan(self, x: _DT, /) -> _DT: ...
    def less(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def less_equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def log(self, x: _DT, /) -> _DT: ...
    def log1p(self, x: _DT, /) -> _DT: ...
    def log2(self, x: _DT, /) -> _DT: ...
    def log10(self, x: _DT, /) -> _DT: ...
    def logaddexp(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def logical_and(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def logical_not(self, x: _DT, /) -> _DT: ...
    def logical_or(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def logical_xor(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def maximum(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def minimum(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def multiply(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def negative(self, x: _DT, /) -> _DT: ...
    def not_equal(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def positive(self, x: _DT, /) -> _DT: ...
    def pow(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def real(self, x: _DT, /) -> _DT: ...
    def remainder(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def round(self, x: _DT, /) -> _DT: ...
    def sign(self, x: _DT, /) -> _DT: ...
    def sin(self, x: _DT, /) -> _DT: ...
    def sinh(self, x: _DT, /) -> _DT: ...
    def square(self, x: _DT, /) -> _DT: ...
    def sqrt(self, x: _DT, /) -> _DT: ...
    def subtract(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def tan(self, x: _DT, /) -> _DT: ...
    def tanh(self, x: _DT, /) -> _DT: ...
    def trunc(self, x: _DT, /) -> _DT: ...

    # non-standard
    def arcsin(self, x: _DT, /) -> _DT: ...
    def arccos(self, x: _DT, /) -> _DT: ...
    def arctan(self, x: _DT, /) -> _DT: ...
    def arctan2(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def arcsinh(self, x: _DT, /) -> _DT: ...
    def arccosh(self, x: _DT, /) -> _DT: ...
    def arctanh(self, x: _DT, /) -> _DT: ...

    ### Indexing functions ###
    # python array API standard v2023.12
    def take(self, x: _DT, indices: _DT, /, *, axis: Optional[int]=None) -> _DT: ...

    ### Linear Algebra Functions ###
    # python array API standard v2023.12
    def matmul(self, x1: _DT, x2: _DT, /) -> _DT: ...
    def matrix_transpose(x: _DT, /) -> _DT: ...
    def tensordot(self, x1: _DT, x2: _DT, /, *, axes: Union[int, Tuple[Sequence[int], Sequence[int]]] = 2) -> _DT: ...
    def vecdot(self, x1: _DT, x2: _DT, /, *, axis: int=-1) -> _DT: ...

    # non-standard
    def cross(self, x1: _DT, x2: _DT, /, *, axis: Optional[int]=None) -> _DT: ...
    def dot(self, x1: _DT, x2: _DT, /, *, axis=-1) -> _DT: ...
    def einsum(self, subscripts: str, /, *operands: _DT, **kwargs) -> _DT: ...
    def trace(self, x: _DT, /, *, offset: int = 0, axis1=0, axis2=1) -> _DT: ...

    ### Manipulation Functions ###
    # python array API standard v2023.12
    def broadcast_arrays(self, *arrays: _DT) -> List[_DT]: ...
    def broadcast_to(self, x: _DT, /, shape: Size) -> _DT: ...
    def concat(self, arrays: Union[Tuple[_DT, ...], List[_DT]], /, *, axis=0) -> _DT: ...
    def expand_dims(self, x: _DT, /, *, axis: int = 0) -> _DT: ...
    def flip(self, x: _DT, /, axis: Optional[Union[int, Tuple[int, ...]]]=None) -> _DT: ...
    def moveaxis(self, x: _DT, source: Union[int, Tuple[int, ...]], destination: Union[int, Tuple[int, ...]], /) -> _DT: ...
    def permute_dims(self, x: _DT, /, axes: Tuple[int, ...]) -> _DT: ...
    def repeat(self, x: _DT, repeats: int, /, *, axis: Optional[int]=None) -> _DT: ...
    def reshape(self, x: _DT, /, shape: Size, *, copy=None) -> _DT: ...
    def roll(self, x: _DT, /, shift: Union[int, Tuple[int, ...]], *, axis: Optional[Union[int, Tuple[int, ...]]]=None) -> _DT: ...
    def squeeze(self, x: _DT, /, axis: Union[int, Tuple[int, ...]]) -> _DT: ...
    def stack(self, arrays: Union[Tuple[_DT, ...], List[_DT]], *, axis=0) -> _DT: ...
    def tile(self, x: _DT, repetitions: Tuple[int, ...], /) -> _DT: ...
    def unstack(self, x: _DT, /, *, axis: int = 0) -> Tuple[_DT, ...]: ...

    # non-standard
    def insert(self, x: _DT, obj, values, /, *, axis: Optional[int] = None) -> _DT: ...
    def split(self, x: _DT, indices_or_sections, /, *, axis: int = 0) -> Tuple[_DT, ...]: ...
    def swapaxes(self, a: _DT, axis1: int, axis2: int, /) -> _DT: ...

    ### Searching Functions ###
    # python array API standard v2023.12
    def argmax(self, x: _DT, /, *, axis=None, keepdims=False) -> _DT: ...
    def argmin(self, x: _DT, /, *, axis=None, keepdims=False) -> _DT: ...
    def nonzero(self, x: _DT, /) -> Tuple[_DT, ...]: ...
    def searchsorted(self, x1: _DT, x2: _DT, /, *, side: Literal["left", "right"]="left", sorter: Optional[_DT]=None) -> _DT: ...
    def where(self, condition: _DT, x1: _DT, x2: _DT, /) -> _DT: ...

    # non-standard
    def bincount(self, x: _DT, /, *, weights=None, minlength=0) -> _DT: ...
    def isin(self, element: _DT, test_elements: _DT, /, *, assume_unique=False, invert=False) -> _DT: ...

    ### Set Functions ###
    # python array API standard v2023.12
    def unique_all(self, x: _DT, /) -> Tuple[_DT, _DT, _DT, _DT]: ...

    # non-standard
    def unique(self, ar: _DT, return_index=False, return_inverse=False, return_counts=False, axis=0, **kwargs): ...

    ###Sorting Functions ###
    # python array API standard v2023.12
    def argsort(self, x: _DT, /, *, axis: int=-1, descending: bool=False, stable: bool=True) -> _DT: ...
    def sort(self, x: _DT, /, *, axis: int=-1, descending: bool=False, stable: bool=True) -> _DT: ...
    # non-standard
    def lexsort(self, keys: Tuple[_DT, ...], /, *, axis: int = -1) -> _DT: ...

    ### Statistical Functions ###
    # python array API standard v2023.12
    def cumulative_sum(x: _DT, /, *, axis: Optional[int] = None, dtype=None, include_initial: bool = False) -> _DT: ...
    def max(self, x: _DT, /, *, axis=None, keepdims=False) -> _DT: ...
    def mean(self, x: _DT, /, *, axis=None, keepdims: bool=False) -> _DT: ...
    def min(self, x: _DT, /, *, axis=None, keepdims=False) -> _DT: ...
    def prod(self, x: _DT, /, *, axis=None, dtype=None, keepdims=False) -> _DT: ...
    def std(self, x: _DT, /, *, axis=None, correction: Number=0., keepdims: bool=False) -> _DT: ...
    def sum(self, x: _DT, /, *, axis=None, dtype=None, keepdims=False) -> _DT: ...
    def var(self, x: _DT, /, *, axis=None, correction: Number=0., keepdims: bool=False) -> _DT: ...

    # non-standard
    def cumsum(self, x: _DT, /, *, axis: Optional[int]=None) -> _DT: ...
    def cumprod(self, x: _DT, /, *, axis: Optional[int]=None) -> _DT: ...

    ### Utility Functions ###
    # python array API standard v2023.12
    def all(self, x: _DT, /, *, axis=None, keepdims: bool=False) -> _DT: ...
    def any(self, x: _DT, /, *, axis=None, keepdims: bool=False) -> _DT: ...

    # non-standard
    def allclose(self, x1: _DT, x2: _DT, *, rtol=1e-05, atol=1e-08, equal_nan=False) -> bool: ...
    def copy(self, x: _DT, /) -> _DT: ...
    def size(self, x: _DT, /, *, axis: Optional[int]=None) -> int: ...

    ### Sparse Functions ###

    ### Function Transforms ###
    # non-standard
    def apply_along_axis(self, func1d, axis: int, arr: _DT, *args, **kwds) -> _DT: ...
    def vmap(self, func: _FT, /, in_axes: Axes = 0, out_axes: Axes = 0, *args, **kwds) -> _FT: ...
    def grad(self, func: _FT, /, argnums: Union[int, Tuple[int, ...]] = 0, has_aux=False) -> _FT: ...
    def jvp(self, func: _FT, /, primals: _DT, tangents: _DT, has_aux=False) -> Union[Tuple[_DT, _DT], Tuple[_DT, _DT, Any]]: ...
    def vjp(self, func: _FT, /, primals: _DT, has_aux=False) -> Union[Tuple[_DT, VJP_Fn], Tuple[_DT, VJP_Fn, Any]]: ...
    def jacfwd(self, func: _FT, /, argnums: Union[int, Tuple[int, ...]] = 0, has_aux=False, *args, **kwds) -> Union[_FT, Tuple[_FT, Any]]: ...
    def jacrev(self, func: _FT, /, argnums: Union[int, Tuple[int, ...]] = 0, has_aux=False, *args, **kwds) -> Union[_FT, Tuple[_FT, Any]]: ...
    def hessian(self, func: _FT, /, argnums: Union[int, Tuple[int, ...]] = 0, has_aux=False, *args, **kwds) -> Union[_FT, Tuple[_FT, Any]]: ...

    ### Other Functions ###
    def set_at(self, x: _DT, indices: _DT, src: Union[_DT, Number, bool], /) -> _DT: ...
    def add_at(self, x: _DT, indices: _DT, src: Union[_DT, Number], /) -> _DT: ...
    def index_add(self, x: _DT, index: _DT, src: Union[_DT, Number], /, *, axis: int=0, alpha: Number=1) -> _DT: ...
    def scatter(self, x: _DT, index: _DT, src: _DT, /, *, axis: int=0) -> _DT: ...
    def scatter_add(self, x: _DT, index: _DT, src: _DT, /, *, axis: int=0) -> _DT: ...
    def query_point(self, x: _DT, y: _DT, h: _DT, box_size: _DT, mask_self=True, periodic=[True, True, True]): ...

    ### FEALPy functionals ###
    def multi_index_matrix(self, p: int, dim: int, *, dtype=None) -> _DT: ...
    def edge_length(self, edge: _DT, node: _DT, *, out=None) -> _DT: ...
    def edge_normal(self, edge: _DT, node: _DT, unit=False, *, out=None) -> _DT: ...
    def edge_tangent(self, edge: _DT, node: _DT, unit=False, *, out=None) -> _DT: ...
    def tensorprod(self, *tensors: _DT) -> _DT: ...
    def bc_to_points(self, bcs: Union[_DT, Tuple[_DT, ...]], node: _DT, entity: _DT) -> _DT: ...
    def barycenter(self, entity: _DT, node: _DT, loc: Optional[_DT]=None) -> _DT: ...
    def simplex_measure(self, entity: _DT, node: _DT) -> _DT: ...
    def simplex_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def simplex_grad_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def simplex_hess_shape_function(self, bc: _DT, p: int, mi: Optional[_DT]=None) -> _DT: ...
    def tensor_measure(self, entity: _DT, node: _DT) -> _DT: ...

    def interval_grad_lambda(self, line: _DT, node: _DT) -> _DT: ...
    def triangle_area_3d(self, tri: _DT, node: _DT) -> _DT: ...
    def triangle_grad_lambda_2d(self, tri: _DT, node: _DT) -> _DT: ...
    def triangle_grad_lambda_3d(self, tri: _DT, node: _DT) -> _DT: ...
    def quadrangle_grad_lambda_2d(self, quad: _DT, node: _DT) -> _DT: ...
    def tetrahedron_grad_lambda_3d(self, tet: _DT, node: _DT, local_face: _DT) -> _DT: ...
