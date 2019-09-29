import numpy as np
import matplotlib.pyplot as plt

from fealpy.pde.poisson_2d import CosCosData
from fealpy.functionspace import ConformingVirtualElementSpace2d, ScaledMonomialSpace2d
p = 2

pde = CosCosData()
quadtree = pde.init_mesh(n=3, meshtype='quadtree')
options = quadtree.adaptive_options(method='numrefine', maxsize=1, HB=True)

pmesh = quadtree.to_pmesh()

space0 = ConformingVirtualElementSpace2d(pmesh, p=p)
uh0 = space0.interpolation(pde.solution)
sh0 = space0.project_to_smspace(uh0)
error = space0.integralalg.L2_error(pde.solution, sh0.value)
print(error)

axes0 = plt.subplot(1, 2, 1)
pmesh.add_plot(axes0)
pmesh.find_cell(axes0, showindex=True)

NC = pmesh.number_of_cells()
eta = np.ones(NC, dtype=np.int)

quadtree.adaptive(eta, options)
pmesh = quadtree.to_pmesh()

space1 = ConformingVirtualElementSpace2d(pmesh, p=p)
smspace1 = space1.smspace
print(options['HB'])
sh1 = smspace1.interpolation(sh0, options['HB'])

error = space1.integralalg.L2_error(pde.solution, sh1.value)
print(error)


axes1 = plt.subplot(1, 2, 2)
pmesh.add_plot(axes1)
pmesh.find_cell(axes1, showindex=True)
plt.show()



