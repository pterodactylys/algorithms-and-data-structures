import matplotlib.pyplot as plt
import numpy as np

class Config:
    n_dim: int = 2
    x_min: float = -5.0
    x_max: float = 5.0
    seed: int = 100

    ga_pop_size: int = 100
    ga_generations: int = 250
    ga_tournament_k: int = 5
    ga_mutation_probability: float = 0.2
    ga_crossover_probability: float = 0.7


def function(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    return 0.5 * np.sum(arr**4 - 16.0 * arr**2 + 5.0 * arr, axis=-1)

def selection(pop, fit, k, random_generator):
    idx = random_generator.integers(0, len(pop), size=k)
    best = idx[np.argmin(fit[idx])]
    return pop[best].copy()

def arithmetic_crossover(p1, p2, randon_gen):
    alpha = randon_gen.uniform()
    return p1 * alpha + p2 * (1 - alpha)

def mutation(ind, prob, sigma, x_min, x_max, random_generator):
    mutant = ind.copy()
    mask = random_generator.uniform(size = len(ind)) < prob
    noise = random_generator.noise(0, sigma, size=len(ind))
    mutant[mask] += noise[mask]
    return np.clip(mutant, x_min, x_max)

def run_ga(cfg, random_genertor):
    pop = random_generator.uniform(cfg.x_min, cfg.x_max, size=(cfg.ga_pop_size, cfg.n_dim))

    best_fit_history = []
    mean_fit_history = []
    best_x_history = []

    for q in range(cfg.ga_generations):
        fit = function(pop)

        best_idx = np.argmin(fit)
        elite = pop[best_idx].copy()
        elite_fit = fit[best_idx]

        best_fit_history.append(elite_fit)
        mean_fit_history.append(np.mean(fit))
        best_x_history.append(elite.copy())

        new_pop = []
        # if elitism:
        
        while len(new_pop) < cfg.ga_pop_size:
            p1 = selection(pop, fit, cfg.ga_tournament_k, random_generator)
            p2 = selection(pop, fit, cfg.ga_tournament_k, random_generator)
            
            

def main():
    random_generator = np.random.default_rng(cfg.seed)