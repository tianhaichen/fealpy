import sys
import numpy as np 
from scipy.sparse.linalg import spsolve
import matplotlib.pyplot as plt

from fealpy.pde.linear_elasticity_model import CantileverBeam2d
from fealpy.mesh.simple_mesh_generator import rectangledomainmesh
from fealpy.functionspace import LagrangeFiniteElementSpace
from fealpy.boundarycondition import BoundaryCondition


pde = CantileverBeam2d()
mu = pde.mu
lam = pde.lam
mesh = pde.init_mesh(n=2)

space = LagrangeFiniteElementSpace(mesh, p=1)
uh = space.function(dim=2)
A = space.linear_elasticity_matrix(mu, lam)
F = space.source_vector(pde.source, dim=2)
bc = BoundaryCondition(space, dirichlet=pde.dirichlet,  neuman=pde.neuman)
bc.apply_neuman_bc(b)
A, F = bc.apppy_dirichlet_bc(A, F, uh, 
    is_dirichlet_boundary=pde.is_dirichlet_boundary)

x = space


fig = plt.figure()
axes = fig.gca()
mesh.add_plot(axes)
plt.show()