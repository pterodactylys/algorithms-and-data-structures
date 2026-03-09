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

    # Gray-code mode params
    gray_bits_per_dim: int = 20


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


def _int_to_gray(value: int) -> int:
    return value ^ (value >> 1)


def _gray_to_int(gray: int) -> int:
    value = gray
    shift = 1
    while (gray >> shift) > 0:
        value ^= gray >> shift
        shift += 1
    return value


def _int_to_bits(value: int, bits_per_dim: int) -> np.ndarray:
    bits = np.zeros(bits_per_dim, dtype=np.uint8)
    for bit in range(bits_per_dim):
        shift = bits_per_dim - 1 - bit
        bits[bit] = (value >> shift) & 1
    return bits


def _bits_to_int(bits: np.ndarray) -> int:
    value = 0
    for bit in bits:
        value = (value << 1) | int(bit)
    return value


def _encode_real_vector_to_gray_bits(x: np.ndarray, x_min: float, x_max: float, bits_per_dim: int) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    levels = (1 << bits_per_dim) - 1
    if levels <= 0:
        raise ValueError("gray_bits_per_dim must be >= 1")

    scaled = np.clip((x - x_min) / (x_max - x_min), 0.0, 1.0)
    ints = np.rint(scaled * levels).astype(int)

    encoded = np.zeros((x.shape[0], bits_per_dim), dtype=np.uint8)
    for dim in range(x.shape[0]):
        gray = _int_to_gray(int(ints[dim]))
        encoded[dim] = _int_to_bits(gray, bits_per_dim)
    return encoded


def _decode_gray_bits_to_real_vector(bits: np.ndarray, x_min: float, x_max: float, bits_per_dim: int) -> np.ndarray:
    bits = np.asarray(bits, dtype=np.uint8)
    levels = (1 << bits_per_dim) - 1
    decoded = np.zeros(bits.shape[0], dtype=float)

    for dim in range(bits.shape[0]):
        gray = _bits_to_int(bits[dim])
        value_int = _gray_to_int(gray)
        decoded[dim] = x_min + (value_int / levels) * (x_max - x_min)
    return decoded


def _decode_population_gray(pop_bits: np.ndarray, x_min: float, x_max: float, bits_per_dim: int) -> np.ndarray:
    pop_size, n_dim, _ = pop_bits.shape
    pop_real = np.zeros((pop_size, n_dim), dtype=float)
    for i in range(pop_size):
        pop_real[i] = _decode_gray_bits_to_real_vector(pop_bits[i], x_min, x_max, bits_per_dim)
    return pop_real


def _selection_index(fit: np.ndarray, k: int, random_generator: np.random.Generator) -> int:
    idx = random_generator.integers(0, len(fit), size=k)
    return int(idx[np.argmin(fit[idx])])


def _gray_crossover(
    p1_bits: np.ndarray,
    p2_bits: np.ndarray,
    crossover_probability: float,
    random_generator: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    c1 = p1_bits.copy()
    c2 = p2_bits.copy()

    if random_generator.random() >= crossover_probability:
        return c1, c2

    n_dim, bits_per_dim = p1_bits.shape
    for dim in range(n_dim):
        if bits_per_dim < 2:
            continue
        point = int(random_generator.integers(1, bits_per_dim))
        c1[dim, point:] = p2_bits[dim, point:]
        c2[dim, point:] = p1_bits[dim, point:]
    return c1, c2


def _gray_mutation(child_bits: np.ndarray, mutation_probability: float, random_generator: np.random.Generator) -> np.ndarray:
    mask = random_generator.random(child_bits.shape) < mutation_probability
    child_bits[mask] = 1 - child_bits[mask]
    return child_bits


def run_ga_gray(cfg: GAConfig, random_generator: np.random.Generator) -> dict:
    bits_per_dim = int(cfg.gray_bits_per_dim)
    if bits_per_dim < 1:
        raise ValueError("gray_bits_per_dim must be >= 1")

    # Инициализация реальной популяции и кодирование в Gray bits
    pop_real = random_generator.uniform(cfg.x_min, cfg.x_max, size=(cfg.pop_size, cfg.n_dim))
    pop_bits = np.zeros((cfg.pop_size, cfg.n_dim, bits_per_dim), dtype=np.uint8)
    for i in range(cfg.pop_size):
        pop_bits[i] = _encode_real_vector_to_gray_bits(pop_real[i], cfg.x_min, cfg.x_max, bits_per_dim)

    best_fit_history = []
    mean_fit_history = []
    best_x_history = []
    population_history = [pop_real.copy()]

    for _ in range(cfg.generations):
        pop_real = _decode_population_gray(pop_bits, cfg.x_min, cfg.x_max, bits_per_dim)
        fit = objective(pop_real)

        best_idx = int(np.argmin(fit))
        best_fit = float(fit[best_idx])
        best_x = pop_real[best_idx].copy()

        best_fit_history.append(best_fit)
        mean_fit_history.append(float(np.mean(fit)))
        best_x_history.append(best_x)

        new_pop_bits = []
        if cfg.elitism:
            elite_count = int(np.clip(cfg.elite_count, 0, cfg.pop_size))
            if elite_count > 0:
                elite_indices = np.argsort(fit)[:elite_count]
                for idx in elite_indices:
                    new_pop_bits.append(pop_bits[idx].copy())

        while len(new_pop_bits) < cfg.pop_size:
            p1_idx = _selection_index(fit, cfg.tournament_k, random_generator)
            p2_idx = _selection_index(fit, cfg.tournament_k, random_generator)

            c1_bits, c2_bits = _gray_crossover(
                pop_bits[p1_idx],
                pop_bits[p2_idx],
                cfg.crossover_probability,
                random_generator,
            )

            c1_bits = _gray_mutation(c1_bits, cfg.mutation_probability, random_generator)
            c2_bits = _gray_mutation(c2_bits, cfg.mutation_probability, random_generator)

            new_pop_bits.append(c1_bits)
            if len(new_pop_bits) < cfg.pop_size:
                new_pop_bits.append(c2_bits)

        pop_bits = np.asarray(new_pop_bits, dtype=np.uint8)
        pop_real = _decode_population_gray(pop_bits, cfg.x_min, cfg.x_max, bits_per_dim)
        population_history.append(pop_real.copy())

    final_real = _decode_population_gray(pop_bits, cfg.x_min, cfg.x_max, bits_per_dim)
    final_fit = objective(final_real)
    best_idx = int(np.argmin(final_fit))

    return {
        "best_x": final_real[best_idx].copy(),
        "best_fit": float(final_fit[best_idx]),
        "best_fit_history": np.asarray(best_fit_history),
        "mean_fit_history": np.asarray(mean_fit_history),
        "best_x_history": np.asarray(best_x_history),
        "population_history": np.asarray(population_history),
    }


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


def demo_gray_encoding_example() -> None:
    """
    Демонстрация кодирования вещественных чисел в Gray code:
    real -> scaled int -> gray int -> bits -> decode back to real.
    """
    x_min = -10.0
    x_max = 10.0
    bits_per_dim = 52

    print("=== Quantization step by bit depth ===")
    for bits in (8, 16, 24, 32, 40, 48, 52):
        levels_i = (1 << bits) - 1
        step = (x_max - x_min) / levels_i
        print(f"bits={bits:2d} -> step={step:.3e}")
    print()

    # Пример для одной координаты
    x_value = np.array([2.75], dtype=float)
    levels = (1 << bits_per_dim) - 1
    scaled = np.clip((x_value - x_min) / (x_max - x_min), 0.0, 1.0)
    int_value = int(np.rint(scaled[0] * levels))
    gray_value = _int_to_gray(int_value)
    gray_bits = _int_to_bits(gray_value, bits_per_dim)
    decoded_real = _decode_gray_bits_to_real_vector(gray_bits.reshape(1, -1), x_min, x_max, bits_per_dim)[0]

    print("=== Gray encoding demo (single value) ===")
    print(f"range: [{x_min}, {x_max}], bits={bits_per_dim}, levels={levels}")
    print(f"x = {x_value[0]:.6f}")
    print(f"scaled int = {int_value}")
    print(f"gray int = {gray_value}")
    print("gray bits =", "".join(str(int(b)) for b in gray_bits))
    print(f"decoded x = {decoded_real:.6f}")
    print(f"abs error = {abs(decoded_real - x_value[0]):.6f}")

    # Проверка свойства соседних кодов (Gray соседние числа отличаются на 1 бит)
    print("\n=== Neighbor property demo ===")
    base = int_value
    nxt = min(base + 1, levels)
    g1 = _int_to_bits(_int_to_gray(base), bits_per_dim)
    g2 = _int_to_bits(_int_to_gray(nxt), bits_per_dim)
    hamming = int(np.sum(g1 != g2))
    print(f"int {base} -> gray {''.join(str(int(b)) for b in g1)}")
    print(f"int {nxt} -> gray {''.join(str(int(b)) for b in g2)}")
    print(f"hamming distance = {hamming}")

    # Пример для вектора координат
    x_vec = np.array([-2.903534, 1.125, 7.75], dtype=float)
    encoded_vec = _encode_real_vector_to_gray_bits(x_vec, x_min, x_max, bits_per_dim)
    decoded_vec = _decode_gray_bits_to_real_vector(encoded_vec, x_min, x_max, bits_per_dim)
    print("\n=== Vector demo ===")
    for i in range(x_vec.shape[0]):
        bits_str = "".join(str(int(b)) for b in encoded_vec[i])
        err = abs(decoded_vec[i] - x_vec[i])
        print(f"x[{i}]={x_vec[i]: .6f} -> bits={bits_str} -> decoded={decoded_vec[i]: .6f} | err={err:.6f}")


if __name__ == "__main__":
    demo_gray_encoding_example()
