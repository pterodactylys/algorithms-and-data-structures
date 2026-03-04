import matplotlib.pyplot as plt
import numpy as np

class Config:
    n_dim: int = 2
    x_min: float = -10.0
    x_max: float = 10.0
    seed: int = 50

    ga_pop_size: int = 1000
    ga_generations: int = 200
    ga_tournament_k: int = 2
    ga_mutation_probability: float = 0.25
    ga_mutation_sigma: float = 0.25
    ga_crossover_probability: float = 0.8


def function(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    return 0.5 * np.sum(arr**4 - 16.0 * arr**2 + 5.0 * arr, axis=-1)

def selection(pop, fit, k, random_generator):
    idx = random_generator.integers(0, len(pop), size=k)
    best = idx[np.argmin(fit[idx])]
    return pop[best].copy()

def arithmetic_crossover(p1, p2, random_gen):
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

def run_ga(cfg, random_generator):
    pop = random_generator.uniform(cfg.x_min, cfg.x_max, size=(cfg.ga_pop_size, cfg.n_dim))

    best_fit_history = []
    mean_fit_history = []
    best_x_history = []

    for q in range(cfg.ga_generations):
        fit = function(pop)

        best_idx = np.argmin(fit)
        elite = pop[best_idx].copy()
        elite_fit = fit[best_idx]
        # print(elite_fit)

        best_fit_history.append(elite_fit)
        mean_fit_history.append(np.mean(fit))
        best_x_history.append(elite.copy())

        new_pop = []
        # if elitism:
        
        while len(new_pop) < cfg.ga_pop_size:
            p1 = selection(pop, fit, cfg.ga_tournament_k, random_generator)
            p2 = selection(pop, fit, cfg.ga_tournament_k, random_generator)
            
            if random_generator.random() < cfg.ga_crossover_probability:
                c1, c2 = arithmetic_crossover(p1, p2, random_generator)
            else:
                c1, c2 = p1.copy(), p2.copy()

            c1 = mutation(c1, cfg.ga_mutation_probability, cfg.ga_mutation_sigma, cfg.x_min, cfg.x_max, random_generator)
            c2 = mutation(c2, cfg.ga_mutation_probability, cfg.ga_mutation_sigma, cfg.x_min, cfg.x_max, random_generator)
            
            new_pop.append(c1)
            if len(new_pop) < cfg.ga_pop_size:
                new_pop.append(c2)
            
        pop = np.array(new_pop, dtype=float)

    final_fit = function(pop)
    best_idx = np.argmin(final_fit)

    return {
        "best_x": pop[best_idx].copy(),
        "best_fit": float(final_fit[best_idx]),
        "best_fit_history": np.array(best_fit_history),
        "mean_fit_history": np.array(mean_fit_history),
        "best_x_history": np.array(best_x_history),
    }

def main():
    cfg = Config()
    random_generator = np.random.default_rng(cfg.seed)
    
    ga_res = run_ga(cfg, random_generator)

    x_reference = np.full(cfg.n_dim, -2.903534)
    f_refetrence = float(function(x_reference))

    print("Genetic algorithm: ")
    print("best x:", ga_res["best_x"])
    print("best fit:", ga_res["best_fit"])
    print("accuracy: ", abs(ga_res["best_fit"] - f_refetrence))

if __name__ == "__main__":
    main()