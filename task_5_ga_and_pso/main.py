import argparse
import time

from ga import GAConfig, objective, run_ga
from pso import PSOConfig, run_pso
from visualisation import animate_particles_movement, plot_ga_pso_convergence

import numpy as np


def run_cli(seed: int = 50, runs: int = 1, seed_step: int = 1):
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
    ga_fits = []
    pso_fits = []
    ga_times = []
    pso_times = []

    pso_cfg = PSOConfig(
        n_dim=cfg.n_dim,
        x_min=cfg.x_min,
        x_max=cfg.x_max,
        swarm_size=120,
        iterations=200,
        w=0.8,
        c1=1.5,
        c2=1.5,
        vmax_ratio=0.2,
        velocity_clamping=True,
    )

    ga_res = None
    pso_res = None

    for run_idx in range(runs):
        run_seed = seed + run_idx * seed_step
        random_generator = np.random.default_rng(run_seed)

        ga_t0 = time.perf_counter()
        ga_res = run_ga(cfg, random_generator)
        ga_time_s = time.perf_counter() - ga_t0

        pso_t0 = time.perf_counter()
        pso_res = run_pso(pso_cfg, random_generator)
        pso_time_s = time.perf_counter() - pso_t0

        ga_fits.append(float(ga_res["best_fit"]))
        pso_fits.append(float(pso_res["best_fit"]))
        ga_times.append(float(ga_time_s))
        pso_times.append(float(pso_time_s))

    assert ga_res is not None and pso_res is not None

    x_reference = np.full(cfg.n_dim, -2.903534)
    f_reference = float(objective(x_reference))
    ga_deltas = np.abs(np.asarray(ga_fits) - f_reference)
    pso_deltas = np.abs(np.asarray(pso_fits) - f_reference)

    print(f"Runs: {runs} | seed_start={seed} | seed_step={seed_step}")
    print()
    print("Genetic algorithm: ")
    print("last run best x:", ga_res["best_x"])
    print("last run best fit:", ga_res["best_fit"])
    print("last run |fit - f_ref|:", round(float(ga_deltas[-1]), 12))
    print("last run time (s):", round(ga_times[-1], 6))
    print("best delta over runs:", round(float(np.min(ga_deltas)), 12))
    print("worst delta over runs:", round(float(np.max(ga_deltas)), 12))
    print("mean delta over runs:", round(float(np.mean(ga_deltas)), 12))
    print("std delta over runs:", round(float(np.std(ga_deltas)), 12))
    print("mean time (s):", round(float(np.mean(ga_times)), 6))

    print()
    print("Particle swarm optimization:")
    print("last run best x:", pso_res["best_x"])
    print("last run best fit:", pso_res["best_fit"])
    print("last run |fit - f_ref|:", round(float(pso_deltas[-1]), 12))
    print("last run time (s):", round(pso_times[-1], 6))
    print("best delta over runs:", round(float(np.min(pso_deltas)), 12))
    print("worst delta over runs:", round(float(np.max(pso_deltas)), 12))
    print("mean delta over runs:", round(float(np.mean(pso_deltas)), 12))
    print("std delta over runs:", round(float(np.std(pso_deltas)), 12))
    print("mean time (s):", round(float(np.mean(pso_times)), 6))

    if runs > 1:
        print()
        print("Per-run summary:")
        for run_idx in range(runs):
            run_seed = seed + run_idx * seed_step
            print(
                f"run {run_idx + 1}, seed={run_seed}: "
                f"GA delta={ga_deltas[run_idx]:.12f}, PSO delta={pso_deltas[run_idx]:.12f}, "
                f"GA t={ga_times[run_idx]:.6f}s, PSO t={pso_times[run_idx]:.6f}s"
            )

    plot_ga_pso_convergence(ga_res, pso_res)
    animate_particles_movement(ga_res, pso_res, x_min=cfg.x_min, x_max=cfg.x_max, max_particles=120, interval_ms=70)


def main():
    parser = argparse.ArgumentParser(description="GA + PSO runner")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (without Qt GUI)")
    parser.add_argument("--seed", type=int, default=50, help="Start seed")
    parser.add_argument("--runs", type=int, default=1, help="Number of consecutive runs")
    parser.add_argument("--seed-step", type=int, default=1, help="Seed increment between runs")
    args = parser.parse_args()

    if args.cli:
        run_cli(seed=args.seed, runs=max(1, args.runs), seed_step=max(1, args.seed_step))
        return

    try:
        from gui_qt import launch_gui
    except Exception as exc:
        print("Qt GUI is unavailable:", exc)
        print("Starting CLI mode. Use --cli to force CLI explicitly.")
        run_cli(seed=args.seed, runs=max(1, args.runs), seed_step=max(1, args.seed_step))
        return

    launch_gui()

if __name__ == "__main__":
    main()