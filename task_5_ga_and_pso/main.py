import numpy as np
from ga import GAConfig, objective, run_ga
from visualisation import plot_ga_convergence

def main():
    seed = 50
    cfg = GAConfig(
        n_dim=2,
        x_min=-10.0,
        x_max=10.0,
        pop_size=1000,
        generations=200,
        tournament_k=2,
        mutation_probability=0.25,
        mutation_sigma=0.25,
        crossover_probability=0.8,
        elitism=True,
        elite_count=1,
    )
    random_generator = np.random.default_rng(seed)
    
    ga_res = run_ga(cfg, random_generator)

    x_reference = np.full(cfg.n_dim, -2.903534)
    f_reference = float(objective(x_reference))

    print("Genetic algorithm: ")
    print("best x:", ga_res["best_x"])
    print("best fit:", ga_res["best_fit"])
    print("accuracy: ", abs(ga_res["best_fit"] - f_reference))

    plot_ga_convergence(ga_res)

if __name__ == "__main__":
    main()