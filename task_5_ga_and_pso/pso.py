from dataclasses import dataclass
from ga import objective

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
    velocity_clamping: bool = True


def run_pso(cfg: PSOConfig, random_generator: np.random.Generator):
    swarm_size = cfg.swarm_size
    n_dim = cfg.n_dim

    x = random_generator.uniform(cfg.x_min, cfg.x_max, size=(swarm_size, n_dim))
    vmax = cfg.vmax_ratio * (cfg.x_max - cfg.x_min)
    v = random_generator.uniform(-vmax, vmax, size=(swarm_size, n_dim))

    pbest_x = x.copy()
    pbest_fit = objective(pbest_x)

    gbest_index = int(np.argmin(pbest_fit))
    gbest_x = pbest_x[gbest_index].copy()
    gbest_fit = float(pbest_fit[gbest_index])

    best_fit_history = [gbest_fit]
    best_x_history = [gbest_x.copy()]
    mean_fit_history = [float(np.mean(pbest_fit))]
    swarm_history = [x.copy()]

    for q in range(cfg.iterations):
        r1 = random_generator.random(size=(swarm_size, n_dim))
        r2 = random_generator.random(size=(swarm_size, n_dim))

        v = (
            cfg.w * v
            + cfg.c1 * r1 * (pbest_x - x)
            + cfg.c2 * r2 * (gbest_x - x)
        )

        if cfg.velocity_clamping:
            v = np.clip(v, -vmax, vmax)

        x = x + v
        x = np.clip(x, cfg.x_min, cfg.x_max)

        current_fit = objective(x)

        improved = current_fit < pbest_fit
        pbest_x[improved] = x[improved]
        pbest_fit[improved] = current_fit[improved]

        gbest_index = int(np.argmin(pbest_fit))
        if float(pbest_fit[gbest_index]) < gbest_fit:
            gbest_fit = float(pbest_fit[gbest_index])
            gbest_x = pbest_x[gbest_index].copy()

        best_fit_history.append(gbest_fit)
        best_x_history.append(gbest_x.copy())
        mean_fit_history.append(float(np.mean(current_fit)))
        swarm_history.append(x.copy())

    return {
        "best_x": gbest_x,
        "best_fit": gbest_fit,
        "best_fit_history": np.asarray(best_fit_history),
        "mean_fit_history": np.asarray(mean_fit_history),
        "best_x_history": np.asarray(best_x_history),
        "swarm_history": np.asarray(swarm_history),
    }
