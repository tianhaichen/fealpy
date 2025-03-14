
import pytest
import numpy as np
from fealpy.backend import backend_manager as bm
from fealpy.mesh.triangle_mesh import TriangleMesh
from fealpy.solver import GAMGSolver 
from fealpy.functionspace import LagrangeFESpace
from fealpy.fem import (
        BilinearForm, ScalarDiffusionIntegrator,LinearForm,DirichletBC
    )
from fealpy.sparse import csr_matrix
from fealpy.solver import spsolve
from gamg_solver_data import * 



class TestGAMGSolverInterfaces:
    # @pytest.mark.parametrize("backend", ['numpy'])
    # @pytest.mark.parametrize("data", init_data)
    # def test_init(self, data, backend):
    #     bm.set_backend(backend)
    #     solver = GAMGSolver(**data) 
    #     assert solver is not None
    #     assert solver.maxit == data['maxit']
    def assemble_data(self,data,test_data):
        A_0 = test_data['A']
        A = [A_0]
        P = []
        R =[]
        L = [A_0.tril()]
        U = [A_0.triu()]
        D = [L[-1]+U[-1]-A_0]
        nx = test_data['nx']
        ny = test_data['ny']
        NN = bm.ceil(bm.log2(A[-1].shape[0])/2-4)
        NL = max(min( int(NN), 8), 2) # 估计粗化的层数
        for l in range(NL):
            nx,ny = nx//2,ny//2
            mesh = TriangleMesh.from_box(domain,nx,ny)
            IM = mesh.uniform_refine(n=1,returnim=True)
            P.append(IM[-1])
            for m in P:
                s = m.sum(axis=1)
                # m.T/s[None, :]
                # m = m.div(s)
                R.append(m.T)
            print(R[-1]._crow.shape[0]-1)
            print(R[-1]._spshape[0])
            print(R[-1].shape)
            print(A[l].shape)
            mt = R[-1].matmul(A[l])
            A.append(mt.matmul(P[-1]))
            L.append(A[-1].tril())
            U.append(A[-1].triu()) 
            D.append(L[-1]+U[-1]-A[-1])
            if A[-1].shape[0] < data['csize']:
               break
        return A,P,R,L,U,D

    @pytest.mark.parametrize("backend", ['numpy'])
    @pytest.mark.parametrize("data", init_data)
    @pytest.mark.parametrize("test_data",test_data)
    def test_vcycle(self,data,test_data, backend):
        bm.set_backend(backend)
        solver = GAMGSolver(**data) 
        A,P,R,L,U,D = self.assemble_data(data,test_data)
        solver.setup(A=A,P=P,R=R,L=L,U=U,D=D)
        f = test_data['f']
        phi = solver.vcycle(f)
        e = phi - test_data['sol']
        err = bm.sqrt(test_data['hx']*test_data['hy']*bm.sum(e**2))
        res = A[0].matmul(phi) - f
        res = bm.sqrt(bm.sum(res**2))
        res_0 = bm.array(test_data['f'])
        res_0 = bm.sqrt(bm.sum(res_0**2))
        print('err:',err)
        print('res:',res)
        assert solver is not None


    @pytest.mark.parametrize("backend", ['numpy'])
    @pytest.mark.parametrize("data", init_data)
    @pytest.mark.parametrize("test_data",test_data)
    def test_fcycle(self,data,test_data, backend):
        bm.set_backend(backend)
        solver = GAMGSolver(**data) 
        A,P,R,L,U,D = self.assemble_data(data,test_data)
        solver.setup(A=A,P=P,R=R)
        f = test_data['f']
        phi = solver.fcycle(f)
        e = phi - test_data['sol']
        err = bm.sqrt(test_data['hx']*test_data['hy']*bm.sum(e**2))

        res = A[0].matmul(phi) - f
        res = bm.sqrt(bm.sum(res**2))
        res_0 = bm.array(test_data['f'])
        res_0 = bm.sqrt(bm.sum(res_0**2))
        print('err:',err)
        print('res:',res)
        assert solver is not None


    @pytest.mark.parametrize("backend", ['numpy'])
    @pytest.mark.parametrize("data", init_data)
    @pytest.mark.parametrize("test_data",test_data)
    def test_wcycle(self,data,test_data, backend):
        bm.set_backend(backend)
        solver = GAMGSolver(**data) 
        A,P,R = self.assemble_data(data,test_data)
        solver.setup(A=A,P=P,R=R)
        f = test_data['f']
        phi = solver.wcycle(f)
        e = phi - test_data['sol']
        err = bm.sqrt(test_data['hx']*test_data['hy']*bm.sum(e**2))

        res = A[0].matmul(phi) - f
        res = bm.sqrt(bm.sum(res**2))
        res_0 = bm.array(test_data['f'])
        res_0 = bm.sqrt(bm.sum(res_0**2))
        print('err:',err)
        print('res:',res)
        assert solver is not None


if __name__ == "__main__":
    # pytest.main(["./test_gamg_solver.py",'-k' ,"test_vcycle"])
    test = TestGAMGSolverInterfaces()
# , 'test_fcycle', 'test_wcycle'
    [getattr(test, func)(init_data[0], data, "numpy") for func in 
     ['test_vcycle'] for data in test_data]