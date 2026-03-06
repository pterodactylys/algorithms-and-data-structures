import matplotlib.pyplot as plt
import numpy as np


def plot_ga_convergence(ga_result: dict) -> None:
    history = np.asarray(ga_result["best_fit_history"], dtype=float)
    plt.figure(figsize=(8, 4))
    plt.plot(history, label="GA best fitness", linewidth=2)
    plt.xlabel("Generation")
    plt.ylabel("Best fitness")
    plt.title("Genetic Algorithm convergence")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_ga_pso_convergence(ga_result: dict, pso_result: dict) -> None:
    ga_history = np.asarray(ga_result["best_fit_history"], dtype=float)
    pso_history = np.asarray(pso_result["best_fit_history"], dtype=float)

    plt.figure(figsize=(9, 4.5))
    plt.plot(ga_history, label="GA best fitness", linewidth=2)
    plt.plot(pso_history, label="PSO best fitness", linewidth=2)
    plt.xlabel("Iteration")
    plt.ylabel("Best fitness")
    plt.title("GA vs PSO convergence")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
