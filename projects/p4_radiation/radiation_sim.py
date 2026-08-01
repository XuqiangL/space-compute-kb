"""p4_radiation: radiation effects toolkit (module 06).

Implements Weibull SEU cross-section fitting, on-orbit rate estimation,
TID shielding attenuation, checkpoint interval optimization (Young),
and reliability block math.

Units: LET in MeV*cm^2/mg, cross-section in cm^2, dose in krad(Si).
"""
import math


def weibull_sigma(let: float, sigma_sat: float, l0: float,
                  w: float, s: float) -> float:
    """Weibull fit: sigma(LET) = sigma_sat*(1-exp(-((LET-L0)/W)^s)).

    Returns 0 below threshold L0.
    """
    if let <= l0:
        return 0.0
    return sigma_sat * (1.0 - math.exp(-(((let - l0) / w) ** s)))


def seu_rate_per_bit_day(sigma_sat: float, l0: float, w: float, s: float,
                         flux_above_l0: float) -> float:
    """Crude on-orbit SEU rate: R ~ sigma_eff * integral_flux.

    Uses saturation cross-section times integral flux above threshold
    (conservative upper bound). flux in particles/(cm^2 s).
    Returns upsets per bit per day.
    """
    sigma_eff = sigma_sat * 0.5   # rough average of Weibull rise
    return sigma_eff * flux_above_l0 * 86400.0


def memory_upsets_per_day(rate_per_bit_day: float,
                          capacity_bytes: float) -> float:
    """Total upsets/day for a memory of given size."""
    return rate_per_bit_day * capacity_bytes * 8.0


def tid_shielding(d0_krad: float, thickness_mm_al: float,
                  t0_mm: float = 3.0) -> float:
    """Exponential attenuation: D(t) = D0 * exp(-t/t0) (module 06 sec 3.1)."""
    return d0_krad * math.exp(-thickness_mm_al / t0_mm)


def checkpoint_interval_young(delta_s: float, mtbf_s: float) -> float:
    """Young's optimal checkpoint interval: T = sqrt(2*delta*M).

    delta_s: time to write one checkpoint. mtbf_s: mean time between
    detectable failures. Returns optimal interval in seconds.
    """
    return math.sqrt(2.0 * delta_s * mtbf_s)


def checkpoint_overhead(delta_s: float, interval_s: float) -> float:
    """Fraction of compute time spent checkpointing."""
    return delta_s / interval_s


def expected_lost_work(interval_s: float, mtbf_s: float) -> float:
    """Expected rework per failure ~ interval/2 (+ one checkpoint write)."""
    return interval_s / 2.0


def r_series(reliabilities) -> float:
    """Series reliability: product."""
    r = 1.0
    for x in reliabilities:
        r *= x
    return r


def r_parallel(reliabilities) -> float:
    """Active parallel redundancy: 1 - product(1-Ri)."""
    p = 1.0
    for x in reliabilities:
        p *= (1.0 - x)
    return 1.0 - p


def r_k_of_n(k: int, n: int, r: float) -> float:
    """k-out-of-n reliability (identical units), e.g. TMR = 2oo3."""
    total = 0.0
    for i in range(k, n + 1):
        total += math.comb(n, i) * r ** i * (1.0 - r) ** (n - i)
    return total


def mtbf_from_lambda(lambda_per_hr: float) -> float:
    return 1.0 / lambda_per_hr


def availability(mtbf_hr: float, mttr_hr: float) -> float:
    """Steady-state availability A = MTBF/(MTBF+MTTR)."""
    return mtbf_hr / (mtbf_hr + mttr_hr)


def derating_junction_limit(t_rated_c: float, margin_c: float = 20.0) -> float:
    """ECSS-style junction derating: operate <= rated - margin."""
    return t_rated_c - margin_c
