import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


_ANIMATION_HOLD = []


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


def _objective_2d_grid(x_min: float, x_max: float, y_min: float, y_max: float, points: int = 200):
    xs = np.linspace(x_min, x_max, points)
    ys = np.linspace(y_min, y_max, points)
    xg, yg = np.meshgrid(xs, ys)
    zg = 0.5 * ((xg**4 - 16 * xg**2 + 5 * xg) + (yg**4 - 16 * yg**2 + 5 * yg))
    return xg, yg, zg


def animate_particles_movement(
    ga_result: dict,
    pso_result: dict,
    x_min: float,
    x_max: float,
    max_particles: int = 120,
    interval_ms: int = 60,
) -> FuncAnimation:
    ga_history = np.asarray(ga_result.get("population_history"))
    pso_history = np.asarray(pso_result.get("swarm_history"))

    if ga_history.ndim != 3 or ga_history.shape[-1] != 2:
        raise ValueError("GA animation works only for n_dim=2 and requires population_history")
    if pso_history.ndim != 3 or pso_history.shape[-1] != 2:
        raise ValueError("PSO animation works only for n_dim=2 and requires swarm_history")

    xg, yg, zg = _objective_2d_grid(x_min, x_max, x_min, x_max, points=200)

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.8), sharex=True, sharey=True)
    for ax in axes:
        contour = ax.contourf(xg, yg, zg, levels=30, cmap="viridis", alpha=0.85)
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(x_min, x_max)
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        ax.grid(alpha=0.2)
    fig.colorbar(contour, ax=axes.ravel().tolist(), shrink=0.88, label="f(x1, x2)")

    ga_particles = ga_history.shape[1]
    pso_particles = pso_history.shape[1]
    ga_count = min(max_particles, ga_particles)
    pso_count = min(max_particles, pso_particles)

    ga_idx = np.linspace(0, ga_particles - 1, ga_count, dtype=int)
    pso_idx = np.linspace(0, pso_particles - 1, pso_count, dtype=int)

    ga_scatter = axes[0].scatter([], [], s=14, c="#f97316", alpha=0.9, edgecolors="none")
    pso_scatter = axes[1].scatter([], [], s=14, c="#38bdf8", alpha=0.9, edgecolors="none")

    axes[0].set_title(f"GA particles ({ga_count}/{ga_particles})")
    axes[1].set_title(f"PSO particles ({pso_count}/{pso_particles})")

    total_frames = int(max(ga_history.shape[0], pso_history.shape[0]))
    state = {
        "paused": False,
        "interval_ms": max(10, int(interval_ms)),
        "frame": 0,
        "direction": 1,
    }

    def _frame_to_index(frame: int, steps: int) -> int:
        if total_frames <= 1 or steps <= 1:
            return 0
        return int(round(frame * (steps - 1) / (total_frames - 1)))

    def _title(frame: int) -> str:
        status = "paused" if state["paused"] else "running"
        direction = "forward" if state["direction"] > 0 else "backward"
        return (
            f"Movement animation — frame {frame + 1}/{total_frames} | "
            f"{status}, {direction} | interval={state['interval_ms']} ms "
            f"(space: pause/resume, +/-: speed, ←/→: step, r: reverse, q: close)"
        )

    def _draw_current_frame():
        frame = state["frame"]
        ga_step = _frame_to_index(frame, ga_history.shape[0])
        pso_step = _frame_to_index(frame, pso_history.shape[0])

        ga_points = ga_history[ga_step, ga_idx, :]
        pso_points = pso_history[pso_step, pso_idx, :]

        ga_scatter.set_offsets(ga_points)
        pso_scatter.set_offsets(pso_points)

        fig.suptitle(_title(frame), fontsize=11)
        return ga_scatter, pso_scatter

    def update(_):
        artists = _draw_current_frame()
        if not state["paused"]:
            state["frame"] = (state["frame"] + state["direction"]) % total_frames
        return artists

    def on_key(event):
        key = (event.key or "").lower()
        if key == " ":
            if state["paused"]:
                animation.event_source.start()
            else:
                animation.event_source.stop()
            state["paused"] = not state["paused"]
            fig.canvas.draw_idle()
        elif key in {"+", "="}:
            state["interval_ms"] = max(10, state["interval_ms"] - 10)
            animation.event_source.interval = state["interval_ms"]
            fig.canvas.draw_idle()
        elif key in {"-", "_"}:
            state["interval_ms"] = min(1000, state["interval_ms"] + 10)
            animation.event_source.interval = state["interval_ms"]
            fig.canvas.draw_idle()
        elif key == "left":
            if not state["paused"]:
                animation.event_source.stop()
                state["paused"] = True
            state["frame"] = (state["frame"] - 1) % total_frames
            _draw_current_frame()
            fig.canvas.draw_idle()
        elif key == "right":
            if not state["paused"]:
                animation.event_source.stop()
                state["paused"] = True
            state["frame"] = (state["frame"] + 1) % total_frames
            _draw_current_frame()
            fig.canvas.draw_idle()
        elif key == "r":
            state["direction"] *= -1
            fig.canvas.draw_idle()
        elif key == "q":
            plt.close(fig)

    animation = FuncAnimation(
        fig,
        update,
        frames=total_frames,
        interval=state["interval_ms"],
        blit=False,
        repeat=True,
    )
    fig.canvas.mpl_connect("key_press_event", on_key)
    _ANIMATION_HOLD.append(animation)

    plt.tight_layout()
    plt.show()
    return animation
