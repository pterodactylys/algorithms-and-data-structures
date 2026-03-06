from dataclasses import dataclass
import numpy as np


@dataclass
class PSOConfig:
    n_dim: int = 2
    x_min: float = -10.0
    x_max: float = 10.0

    swarm_size: int = 100
    iterations: int = 200
    w: float = 0.7
    c1: float = 1.5
    c2: float = 1.5
    vmax_ratio: float = 0.2


def run_pso(cfg: PSOConfig, random_generator: np.random.Generator):
    pass
