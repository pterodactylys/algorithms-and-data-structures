import numpy as np
import matplotlib.pyplot as plt

class Config:
    n_dim: int = 2
    x_min: float = -5.0
    x_max: float = 5.0
    seed: int = 100

    ga_pop_size: int = 100
    ga_generations: int = 50
    ga_tournament_k: int = 3
    ga_crossover_prob: float = 0.9
    ga_mutation_prob: float = 0.2
    ga_mutation_sigma: float = 0.25
    ga_elitism: bool = True
    ga_snapshot_interval: int = 5

    pso_swarm_size: int = 60
    pso_iterations: int = 250
    pso_w: float = 0.72
    pso_c1: float = 1.49
    pso_c2: float = 1.49
    pso_vmax_ratio: float = 0.2


def function(x: np.ndarray) -> np.ndarray:
    arr = np.asarray(x, dtype=float)
    return 0.5 * np.sum(arr**4 - 16.0 * arr**2 + 5.0 * arr, axis=-1)


def tournament_selection(pop, fitness, k, rng):
    indices = rng.integers(0, len(pop), size=k)
    best_idx = indices[np.argmin(fitness[indices])]
    return pop[best_idx].copy()


def arithmetic_crossover(p1, p2, rng):
    alpha = rng.uniform()
    return alpha * p1 + (1 - alpha) * p2


def gauss_mutation(individual, prob, sigma, x_min, x_max, rng):
    mutant = individual.copy()
    mask = rng.uniform(size=len(individual)) < prob
    noise = rng.normal(0, sigma, size=len(individual))
    mutant[mask] += noise[mask]
    return np.clip(mutant, x_min, x_max)


def run_ga(cfg: Config, rng: np.random.Generator):
    pop = rng.uniform(cfg.x_min, cfg.x_max, size=(cfg.ga_pop_size, cfg.n_dim))
    fitness = function(pop)

    best_idx = np.argmin(fitness)
    best_solution = pop[best_idx].copy()
    best_fitness = fitness[best_idx]

    history = [best_fitness]
    positions_history = [best_solution.copy()]

    snapshots = []
    snapshot_generations = []

    if cfg.ga_snapshot_interval > 0:
        snapshots.append(pop.copy())
        snapshot_generations.append(0)

    for gen in range(cfg.ga_generations):
        new_pop = []
        while len(new_pop) < cfg.ga_pop_size:
            p1 = tournament_selection(pop, fitness, cfg.ga_tournament_k, rng)
            p2 = tournament_selection(pop, fitness, cfg.ga_tournament_k, rng)

            if rng.uniform() < cfg.ga_crossover_prob:
                child = arithmetic_crossover(p1, p2, rng)
            else:
                child = p1.copy()

            child = gauss_mutation(child, cfg.ga_mutation_prob,
                                   cfg.ga_mutation_sigma,
                                   cfg.x_min, cfg.x_max, rng)
            new_pop.append(child)

        pop = np.array(new_pop)
        fitness = function(pop)

        gen_best_idx = np.argmin(fitness)
        gen_best_fitness = fitness[gen_best_idx]
        history.append(gen_best_fitness)

        if gen_best_fitness < best_fitness:
            best_fitness = gen_best_fitness
            best_solution = pop[gen_best_idx].copy()

        positions_history.append(pop[gen_best_idx].copy())

        if cfg.ga_snapshot_interval > 0 and (gen + 1) % cfg.ga_snapshot_interval == 0:
            snapshots.append(pop.copy())
            snapshot_generations.append(gen + 1)

    return best_solution, best_fitness, history, positions_history, snapshots, snapshot_generations


def plot_population_snapshots(cfg, snapshots, generations, func):
    if cfg.n_dim != 2:
        print("Визуализация популяции доступна только для n_dim=2")
        return

    n_snapshots = len(snapshots)
    if n_snapshots == 0:
        return

    # Определим размер сетки
    cols = min(3, n_snapshots)
    rows = (n_snapshots + cols - 1) // cols

    # Создадим общую сетку для контура
    x = np.linspace(cfg.x_min, cfg.x_max, 200)
    y = np.linspace(cfg.x_min, cfg.x_max, 200)
    X, Y = np.meshgrid(x, y)
    Z = func(np.dstack((X, Y)))

    plt.figure(figsize=(5*cols, 4*rows))

    for i, (pop, gen) in enumerate(zip(snapshots, generations)):
        plt.subplot(rows, cols, i+1)
        plt.contour(X, Y, Z, levels=50, cmap='viridis', alpha=0.6, linewidths=0.5)
        plt.scatter(pop[:, 0], pop[:, 1], c='red', s=1, alpha=0.5, marker='.')
        plt.title(f'Поколение {gen}')
        plt.xlabel('x1')
        plt.ylabel('x2')
        plt.xlim(cfg.x_min, cfg.x_max)
        plt.ylim(cfg.x_min, cfg.x_max)
        plt.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()


def main():
    cfg = Config()
    rng = np.random.default_rng(cfg.seed)

    best_sol, best_val, history, positions_hist, snapshots, snapshot_gens = run_ga(cfg, rng)

    print(f"Лучшее решение: {best_sol}")
    print(f"Значение функции: {best_val:.6f}")

    # График сходимости и траектория лучшей особи
    plt.figure(figsize=(10, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history)
    plt.xlabel('Поколение')
    plt.ylabel('Лучшее значение f(x)')
    plt.title('Сходимость ГА')
    plt.grid()

    if cfg.n_dim == 2:
        plt.subplot(1, 2, 2)
        x = np.linspace(cfg.x_min, cfg.x_max, 200)
        y = np.linspace(cfg.x_min, cfg.x_max, 200)
        X, Y = np.meshgrid(x, y)
        Z = function(np.dstack((X, Y)))
        plt.contour(X, Y, Z, levels=50, cmap='viridis', alpha=0.5)
        positions = np.array(positions_hist)
        plt.plot(positions[:, 0], positions[:, 1], 'r.-', markersize=3, linewidth=0.8)
        plt.plot(positions[0, 0], positions[0, 1], 'go', markersize=6)
        plt.plot(positions[-1, 0], positions[-1, 1], 'bo', markersize=6)
        plt.xlabel('x1')
        plt.ylabel('x2')
        plt.title('Траектория лучшей особи')
        plt.grid(True)

    plt.tight_layout()
    plt.show()

    # Визуализация снимков популяции
    if len(snapshots) > 0:
        plot_population_snapshots(cfg, snapshots, snapshot_gens, function)

    # Проверка с известным минимумом
    true_min_point = np.full(cfg.n_dim, -2.903534)
    true_min_value = -39.166165 * cfg.n_dim
    print(f"Эталонный минимум: {true_min_value:.6f} в точке {true_min_point}")
    print(f"Ошибка: {abs(best_val - true_min_value):.2e}")


if __name__ == "__main__":
    main()