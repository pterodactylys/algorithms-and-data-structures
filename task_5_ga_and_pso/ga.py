from dataclasses import dataclass

import numpy as np


@dataclass
class GAConfig:
    n_dim: int = 2
    x_min: float = -10.0
    x_max: float = 10.0

    pop_size: int = 1000
    generations: int = 200
    tournament_k: int = 2
    mutation_probability: float = 0.25
    mutation_sigma: float = 0.25
    crossover_probability: float = 0.8

    elitism: bool = True
    elite_count: int = 1


def objective(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    return 0.5 * np.sum(arr**4 - 16.0 * arr**2 + 5.0 * arr, axis=-1)


def selection(pop: np.ndarray, fit: np.ndarray, k: int, random_generator: np.random.Generator) -> np.ndarray:
    idx = random_generator.integers(0, len(pop), size=k)
    best = idx[np.argmin(fit[idx])]
    return pop[best].copy()


def arithmetic_crossover(p1: np.ndarray, p2: np.ndarray, random_gen: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    alpha = random_gen.uniform()
    c1 = p1 * alpha + p2 * (1 - alpha)
    c2 = p2 * alpha + p1 * (1 - alpha)
    return c1, c2


def mutation(
    child: np.ndarray,
    mutation_prob: float,
    sigma: float,
    x_min: float,
    x_max: float,
    rng: np.random.Generator,
) -> np.ndarray:
    mask = rng.random(child.shape) < mutation_prob
    noise = rng.normal(0.0, sigma, size=child.shape)
    child = child + mask * noise
    return np.clip(child, x_min, x_max)


def run_ga(cfg: GAConfig, random_generator: np.random.Generator) -> dict:
    pop = random_generator.uniform(cfg.x_min, cfg.x_max, size=(cfg.pop_size, cfg.n_dim))

    best_fit_history = []
    mean_fit_history = []
    best_x_history = []
    population_history = [pop.copy()]

    for _ in range(cfg.generations):
        fit = objective(pop)

        best_idx = np.argmin(fit)
        elite = pop[best_idx].copy()
        elite_fit = fit[best_idx]

        best_fit_history.append(elite_fit)
        mean_fit_history.append(np.mean(fit))
        best_x_history.append(elite.copy())

        new_pop = []
        if cfg.elitism:
            elite_count = int(np.clip(cfg.elite_count, 0, cfg.pop_size))
            if elite_count > 0:
                elite_indices = np.argsort(fit)[:elite_count]
                elites = pop[elite_indices].copy()
                new_pop.extend(elites)

        while len(new_pop) < cfg.pop_size:
            p1 = selection(pop, fit, cfg.tournament_k, random_generator)
            p2 = selection(pop, fit, cfg.tournament_k, random_generator)

            if random_generator.random() < cfg.crossover_probability:
                c1, c2 = arithmetic_crossover(p1, p2, random_generator)
            else:
                c1, c2 = p1.copy(), p2.copy()

            c1 = mutation(c1, cfg.mutation_probability, cfg.mutation_sigma, cfg.x_min, cfg.x_max, random_generator)
            c2 = mutation(c2, cfg.mutation_probability, cfg.mutation_sigma, cfg.x_min, cfg.x_max, random_generator)

            new_pop.append(c1)
            if len(new_pop) < cfg.pop_size:
                new_pop.append(c2)

        pop = np.array(new_pop, dtype=float)
        population_history.append(pop.copy())

    final_fit = objective(pop)
    best_idx = np.argmin(final_fit)

    return {
        "best_x": pop[best_idx].copy(),
        "best_fit": float(final_fit[best_idx]),
        "best_fit_history": np.array(best_fit_history),
        "mean_fit_history": np.array(mean_fit_history),
        "best_x_history": np.array(best_x_history),
        "population_history": np.array(population_history),
    }
