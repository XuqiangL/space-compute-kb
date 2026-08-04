"""transfer.py - Hohmann transfer design between heliocentric orbits.

Circular-coplanar approximation (documented for learning): planet
eccentricities and inclinations are small, so the transfer ellipse is
computed in the ecliptic plane. The miss-distance readout shows the
consequence of this approximation plus wrong phase angle.
"""
import math

from kepler import (AU_KM, DAY_S, MU_SUN_KM, mean_motion_day,
                    orbital_velocity_kms, period_days)

MU_AU_DAY = 2.9591220828559093e-04   # = K_GAUSS^2


def hohmann(r1_au: float, r2_au: float):
    """Returns (dv1, dv2, tof_days, a_t). dv in km/s."""
    a_t = 0.5 * (r1_au + r2_au)
    v1 = orbital_velocity_kms(r1_au, r1_au)
    v2 = orbital_velocity_kms(r2_au, r2_au)
    vtp = orbital_velocity_kms(r1_au, a_t)
    vta = orbital_velocity_kms(r2_au, a_t)
    dv1 = abs(vtp - v1)
    dv2 = abs(v2 - vta)
    tof = math.pi * math.sqrt(a_t ** 3 / MU_AU_DAY)
    return dv1, dv2, tof, a_t


def required_phase_deg(r1_au: float, r2_au: float) -> float:
    """Target's lead angle over departure body at departure instant."""
    _, _, tof, _ = hohmann(r1_au, r2_au)
    n2 = 360.0 / period_days(r2_au)         # deg/day of target
    return (180.0 - n2 * tof) % 360.0


def synodic_days(r1_au: float, r2_au: float) -> float:
    t1, t2 = period_days(r1_au), period_days(r2_au)
    return 1.0 / abs(1.0 / t1 - 1.0 / t2)


def current_phase_deg(pos1, pos2) -> float:
    """Ecliptic longitude of body2 relative to body1, 0..360."""
    l1 = math.degrees(math.atan2(pos1[1], pos1[0]))
    l2 = math.degrees(math.atan2(pos2[1], pos2[0]))
    return (l2 - l1) % 360.0


def wait_days(r1_au: float, r2_au: float, phase_now_deg: float) -> float:
    """Days until the required phase angle occurs (circular approx)."""
    req = required_phase_deg(r1_au, r2_au)
    delta = (req - phase_now_deg) % 360.0
    rate = abs(360.0 / period_days(r1_au) - 360.0 / period_days(r2_au))
    return delta / rate


def transfer_elements(r1_au: float, r2_au: float, lon_dep_deg: float):
    """Elements of the transfer ellipse (coplanar approx).

    Departure at perihelion if r2>r1 (outer target), else at aphelion.
    Returns (a_t, e_t, wbar_deg, M0_deg, depart_at_peri: bool).
    """
    a_t = 0.5 * (r1_au + r2_au)
    e_t = abs(r2_au - r1_au) / (r2_au + r1_au)
    if r2_au >= r1_au:
        return a_t, e_t, lon_dep_deg, 0.0, True
    return a_t, e_t, (lon_dep_deg + 180.0) % 360.0, 180.0, False


def transfer_pos_at(a_t, e_t, wbar_deg, M0_deg, jd_dep, jd):
    from kepler import elements_to_state
    n_deg_day = math.degrees(mean_motion_day(a_t))
    M = (M0_deg + n_deg_day * (jd - jd_dep)) % 360.0
    pos, nu = elements_to_state(a_t, e_t, 0.0, 0.0, wbar_deg, M)
    return pos


def miss_distance_km(sc_pos, target_pos) -> float:
    dx = sc_pos[0] - target_pos[0]
    dy = sc_pos[1] - target_pos[1]
    dz = sc_pos[2] - target_pos[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz) * AU_KM
