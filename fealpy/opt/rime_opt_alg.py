from ..backend import backend_manager as bm 
from ..typing import TensorLike, Index, _S
from .. import logger
from .optimizer_base import Optimizer

"""
Marine Predators Algorithm

Reference:
~~~~~~~~~~
Hang Su, Dong Zhao, Ali Asghar Heidari, Lei Liu, Xiaoqin Zhang, Majdi Mafarja, Huiling Chen. 
RIME: A physics-based optimization. 
Neurocomputing, 2023, 532: 183-214.

"""
class RimeOptAlg(Optimizer):
    def __init__(self, option) -> None:
        super().__init__(option)


    def run(self, w=5):
        options = self.options
        x = options["x0"]
        N = options["NP"]
        fit = self.fun(x)
        MaxIT = options["MaxIters"]
        dim = options["ndim"]
        lb, ub = options["domain"]
        gbest_index = bm.argmin(fit)
        self.gbest = x[gbest_index]
        self.gbest_f = fit[gbest_index]
        self.curve = bm.zeros((MaxIT,))
        self.D_pl = bm.zeros((MaxIT,))
        self.D_pt = bm.zeros((MaxIT,))
        self.Div = bm.zeros((1, MaxIT))
        for it in range(0, MaxIT):
            self.Div[0, it] = bm.sum(bm.sum(bm.abs(bm.mean(x, axis=0) - x))/N)
            # exploration percentage and exploitation percentage
            self.D_pl[it], self.D_pt[it] = self.D_pl_pt(self.Div[0, it])
            RimeFactor = (bm.random.rand(N, 1) - 0.5) * 2 * bm.cos(bm.array(bm.pi * it / (MaxIT / 10))) * (1 - bm.round(bm.array(it * w / MaxIT)) / w) # Parameters of Eq.(3),(4),(5)
            E = (it / MaxIT) ** 0.5 # Eq.(6)
            normalized_rime_rates = fit / (bm.linalg.norm(fit) + 1e-10) # Parameters of Eq.(7) 
            r1 = bm.random.rand(N, 1)
            x_new = ((r1 < E) * (self.gbest + RimeFactor * ((ub - lb) * bm.random.rand(N, 1) + lb)) + # Eq.(3)
                     (r1 >= E) * x)
            r2 = bm.random.rand(N, dim)
            x_new = ((r2 < normalized_rime_rates[:, None]) * (self.gbest)+ 
                     (r2 >= normalized_rime_rates[:, None]) * x_new)
            x_new = x_new + (lb - x_new) * (x_new < lb) + (ub - x_new) * (x_new > ub)
            fit_new = self.fun(x_new)
            mask = fit_new < fit 
            x, fit = bm.where(mask[:, None], x_new, x), bm.where(mask, fit_new, fit)
            self.update_gbest(x, fit)
            self.curve[it] = self.gbest_f