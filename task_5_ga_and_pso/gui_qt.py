from __future__ import annotations

import numpy as np

from ga import GAConfig, objective, run_ga
from pso import PSOConfig, run_pso
from visualisation import animate_particles_movement, plot_ga_pso_convergence


def launch_gui() -> None:
    try:
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import (
            QApplication,
            QCheckBox,
            QDoubleSpinBox,
            QFormLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QSizePolicy,
            QSpinBox,
            QTextEdit,
            QVBoxLayout,
            QWidget,
        )
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "Qt GUI requires PySide6. Install it with: pip install PySide6"
        ) from exc

    class MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("GA + PSO Control Panel")
            self.resize(1200, 860)
            self.setMinimumSize(1050, 740)

            self.ga_res: dict | None = None
            self.pso_res: dict | None = None
            self.ga_cfg: GAConfig | None = None
            self.pso_cfg: PSOConfig | None = None

            central = QWidget(self)
            self.setCentralWidget(central)
            root = QVBoxLayout(central)
            root.setContentsMargins(12, 12, 12, 12)
            root.setSpacing(10)

            common_box = self._common_group()
            ga_box = self._ga_group()
            pso_box = self._pso_group()
            viz_box = self._viz_group()
            self._configure_group_box(common_box)
            self._configure_group_box(ga_box)
            self._configure_group_box(pso_box)
            self._configure_group_box(viz_box)

            top_row = QHBoxLayout()
            top_row.setSpacing(10)

            left_col = QVBoxLayout()
            left_col.setSpacing(10)
            left_col.addWidget(common_box, stretch=1)
            left_col.addWidget(viz_box, stretch=1)

            right_col = QVBoxLayout()
            right_col.setSpacing(10)
            right_col.addWidget(ga_box, stretch=1)
            right_col.addWidget(pso_box, stretch=1)

            top_row.addLayout(left_col, stretch=1)
            top_row.addLayout(right_col, stretch=1)

            root.addLayout(top_row, stretch=2)

            root.addLayout(self._actions_row())

            self.output = QTextEdit(self)
            self.output.setReadOnly(True)
            self.output.setPlaceholderText("Run algorithms to see output...")
            self.output.setMinimumHeight(220)
            root.addWidget(QLabel("Output:"))
            root.addWidget(self.output, stretch=3)

        def _configure_group_box(self, box: QGroupBox) -> None:
            box.setMinimumHeight(180)
            box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        def _common_group(self) -> QGroupBox:
            box = QGroupBox("Common")
            form = QFormLayout(box)

            self.seed = QSpinBox()
            self.seed.setRange(0, 10_000_000)
            self.seed.setValue(50)

            self.n_dim = QSpinBox()
            self.n_dim.setRange(1, 50)
            self.n_dim.setValue(2)

            self.x_min = QDoubleSpinBox()
            self.x_min.setDecimals(3)
            self.x_min.setRange(-1_000.0, 1_000.0)
            self.x_min.setValue(-10.0)

            self.x_max = QDoubleSpinBox()
            self.x_max.setDecimals(3)
            self.x_max.setRange(-1_000.0, 1_000.0)
            self.x_max.setValue(10.0)

            form.addRow("seed", self.seed)
            form.addRow("n_dim", self.n_dim)
            form.addRow("x_min", self.x_min)
            form.addRow("x_max", self.x_max)
            return box

        def _ga_group(self) -> QGroupBox:
            box = QGroupBox("Genetic Algorithm")
            form = QFormLayout(box)

            self.ga_pop_size = QSpinBox()
            self.ga_pop_size.setRange(2, 200_000)
            self.ga_pop_size.setValue(1000)

            self.ga_generations = QSpinBox()
            self.ga_generations.setRange(1, 100_000)
            self.ga_generations.setValue(200)

            self.ga_tournament_k = QSpinBox()
            self.ga_tournament_k.setRange(1, 1000)
            self.ga_tournament_k.setValue(2)

            self.ga_mutation_probability = QDoubleSpinBox()
            self.ga_mutation_probability.setRange(0.0, 1.0)
            self.ga_mutation_probability.setSingleStep(0.01)
            self.ga_mutation_probability.setValue(0.25)

            self.ga_mutation_sigma = QDoubleSpinBox()
            self.ga_mutation_sigma.setRange(0.0, 100.0)
            self.ga_mutation_sigma.setSingleStep(0.01)
            self.ga_mutation_sigma.setValue(0.25)

            self.ga_crossover_probability = QDoubleSpinBox()
            self.ga_crossover_probability.setRange(0.0, 1.0)
            self.ga_crossover_probability.setSingleStep(0.01)
            self.ga_crossover_probability.setValue(0.8)

            self.ga_elitism = QCheckBox()
            self.ga_elitism.setChecked(True)

            self.ga_elite_count = QSpinBox()
            self.ga_elite_count.setRange(0, 10_000)
            self.ga_elite_count.setValue(1)

            form.addRow("pop_size", self.ga_pop_size)
            form.addRow("generations", self.ga_generations)
            form.addRow("tournament_k", self.ga_tournament_k)
            form.addRow("mutation_probability", self.ga_mutation_probability)
            form.addRow("mutation_sigma", self.ga_mutation_sigma)
            form.addRow("crossover_probability", self.ga_crossover_probability)
            form.addRow("elitism", self.ga_elitism)
            form.addRow("elite_count", self.ga_elite_count)
            return box

        def _pso_group(self) -> QGroupBox:
            box = QGroupBox("Particle Swarm Optimization")
            form = QFormLayout(box)

            self.pso_swarm_size = QSpinBox()
            self.pso_swarm_size.setRange(2, 200_000)
            self.pso_swarm_size.setValue(120)

            self.pso_iterations = QSpinBox()
            self.pso_iterations.setRange(1, 100_000)
            self.pso_iterations.setValue(200)

            self.pso_w = QDoubleSpinBox()
            self.pso_w.setRange(0.0, 5.0)
            self.pso_w.setSingleStep(0.01)
            self.pso_w.setValue(0.72)

            self.pso_c1 = QDoubleSpinBox()
            self.pso_c1.setRange(0.0, 10.0)
            self.pso_c1.setSingleStep(0.01)
            self.pso_c1.setValue(1.49)

            self.pso_c2 = QDoubleSpinBox()
            self.pso_c2.setRange(0.0, 10.0)
            self.pso_c2.setSingleStep(0.01)
            self.pso_c2.setValue(1.49)

            self.pso_vmax_ratio = QDoubleSpinBox()
            self.pso_vmax_ratio.setRange(0.0, 5.0)
            self.pso_vmax_ratio.setSingleStep(0.01)
            self.pso_vmax_ratio.setValue(0.2)

            self.pso_velocity_clamping = QCheckBox()
            self.pso_velocity_clamping.setChecked(True)

            form.addRow("swarm_size", self.pso_swarm_size)
            form.addRow("iterations", self.pso_iterations)
            form.addRow("w", self.pso_w)
            form.addRow("c1", self.pso_c1)
            form.addRow("c2", self.pso_c2)
            form.addRow("vmax_ratio", self.pso_vmax_ratio)
            form.addRow("velocity_clamping", self.pso_velocity_clamping)
            return box

        def _viz_group(self) -> QGroupBox:
            box = QGroupBox("Visualization")
            form = QFormLayout(box)

            self.viz_max_particles = QSpinBox()
            self.viz_max_particles.setRange(1, 10_000)
            self.viz_max_particles.setValue(120)

            self.viz_interval_ms = QSpinBox()
            self.viz_interval_ms.setRange(10, 5_000)
            self.viz_interval_ms.setValue(70)

            form.addRow("max_particles", self.viz_max_particles)
            form.addRow("interval_ms", self.viz_interval_ms)
            return box

        def _actions_row(self) -> QHBoxLayout:
            row = QHBoxLayout()

            run_btn = QPushButton("Run GA + PSO")
            run_btn.clicked.connect(self.run_algorithms)

            conv_btn = QPushButton("Show Convergence")
            conv_btn.clicked.connect(self.show_convergence)

            anim_btn = QPushButton("Show Animation")
            anim_btn.clicked.connect(self.show_animation)

            row.addWidget(run_btn)
            row.addWidget(conv_btn)
            row.addWidget(anim_btn)
            row.addStretch(1)
            return row

        def _read_configs(self) -> tuple[GAConfig, PSOConfig, int]:
            x_min = float(self.x_min.value())
            x_max = float(self.x_max.value())
            if x_min >= x_max:
                raise ValueError("x_min must be less than x_max")

            n_dim = int(self.n_dim.value())
            seed = int(self.seed.value())

            ga_cfg = GAConfig(
                n_dim=n_dim,
                x_min=x_min,
                x_max=x_max,
                pop_size=int(self.ga_pop_size.value()),
                generations=int(self.ga_generations.value()),
                tournament_k=int(self.ga_tournament_k.value()),
                mutation_probability=float(self.ga_mutation_probability.value()),
                mutation_sigma=float(self.ga_mutation_sigma.value()),
                crossover_probability=float(self.ga_crossover_probability.value()),
                elitism=bool(self.ga_elitism.isChecked()),
                elite_count=int(self.ga_elite_count.value()),
            )

            pso_cfg = PSOConfig(
                n_dim=n_dim,
                x_min=x_min,
                x_max=x_max,
                swarm_size=int(self.pso_swarm_size.value()),
                iterations=int(self.pso_iterations.value()),
                w=float(self.pso_w.value()),
                c1=float(self.pso_c1.value()),
                c2=float(self.pso_c2.value()),
                vmax_ratio=float(self.pso_vmax_ratio.value()),
                velocity_clamping=bool(self.pso_velocity_clamping.isChecked()),
            )
            return ga_cfg, pso_cfg, seed

        def run_algorithms(self) -> None:
            try:
                ga_cfg, pso_cfg, seed = self._read_configs()
                QApplication.setOverrideCursor(Qt.WaitCursor)

                rng = np.random.default_rng(seed)
                ga_res = run_ga(ga_cfg, rng)
                pso_res = run_pso(pso_cfg, rng)

                self.ga_cfg = ga_cfg
                self.pso_cfg = pso_cfg
                self.ga_res = ga_res
                self.pso_res = pso_res

                x_reference = np.full(ga_cfg.n_dim, -2.903534)
                f_reference = float(objective(x_reference))

                text = []
                text.append("Genetic algorithm:")
                text.append(f"best x: {ga_res['best_x']}")
                text.append(f"best fit: {ga_res['best_fit']}")
                text.append(f"accuracy: {abs(ga_res['best_fit'] - f_reference)}")
                text.append("")
                text.append("Particle swarm optimization:")
                text.append(f"best x: {pso_res['best_x']}")
                text.append(f"best fit: {pso_res['best_fit']}")
                text.append(f"accuracy: {abs(pso_res['best_fit'] - f_reference)}")

                self.output.setPlainText("\n".join(text))

            except Exception as exc:
                QMessageBox.critical(self, "Error", str(exc))
            finally:
                QApplication.restoreOverrideCursor()

        def _ensure_results(self) -> bool:
            if self.ga_res is None or self.pso_res is None:
                QMessageBox.information(self, "Info", "Run algorithms first.")
                return False
            return True

        def show_convergence(self) -> None:
            if not self._ensure_results():
                return
            plot_ga_pso_convergence(self.ga_res, self.pso_res)

        def show_animation(self) -> None:
            if not self._ensure_results():
                return
            assert self.ga_cfg is not None
            if self.ga_cfg.n_dim != 2:
                QMessageBox.warning(self, "Unsupported", "Animation works only for n_dim = 2.")
                return
            animate_particles_movement(
                self.ga_res,
                self.pso_res,
                x_min=self.ga_cfg.x_min,
                x_max=self.ga_cfg.x_max,
                max_particles=int(self.viz_max_particles.value()),
                interval_ms=int(self.viz_interval_ms.value()),
            )

    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
