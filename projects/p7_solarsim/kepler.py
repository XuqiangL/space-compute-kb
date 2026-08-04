"""kepler.py - core two-body orbital mechanics.

Units: AU for heliocentric positions, degrees for angles in tables,
radians internally. mu_sun in AU^3/day^2 derived from Gaussian constant.
"""
import math

AU_KM = 149597870.7
MU_SUN_KM = 1.32712440018e11          # km^3/s^2
K_GAUSS = 0.01720209895               # AU^(3/2) / day
MU_SUN_AU = K_GAUSS ** 2              # AU^3/day^2
DAY_S = 86400.0


def solve_kepler(M_rad: float, e: float, tol: float = 1e-12) -> float:
    """Newton-Raphson solution of E - e*sin(E) = M. M in radians."""
    M = math.fmod(M_rad, 2.0 * math.pi)
    if M < 0:
        M += 2.0 * math.pi
    E = M if e < 0.8 else math.pi
    for _ in range(50):
        f = E - e * math.sin(E) - M
        fp = 1.0 - e * math.cos(E)
        dE = f / fp
        E -= dE
        if abs(dE) < tol:
            break
    return E


def elements_to_state(a, e, i_deg, Om_deg, w_deg, M_deg):
    """Keplerian elements -> ecliptic-frame position (AU).

    a in AU, angles in degrees. Returns (x, y, z) and true anomaly (deg).
    """
    i = math.radians(i_deg)
    Om = math.radians(Om_deg)
    w = math.radians(w_deg)
    M = math.radians(M_deg)
    E = solve_kepler(M, e)
    xp = a * (math.cos(E) - e)
    yp = a * math.sqrt(1.0 - e * e) * math.sin(E)
    cw, sw = math.cos(w), math.sin(w)
    cO, sO = math.cos(Om), math.sin(Om)
    ci, si = math.cos(i), math.sin(i)
    x = (cO * cw - sO * sw * ci) * xp + (-cO * sw - sO * cw * ci) * yp
    y = (sO * cw + cO * sw * ci) * xp + (-sO * sw + cO * cw * ci) * yp
    z = (sw * si) * xp + (cw * si) * yp
    nu = math.degrees(math.atan2(
        math.sqrt(1.0 - e * e) * math.sin(E), math.cos(E) - e))
    return (x, y, z), nu


def mean_motion_day(a_au: float) -> float:
    """Mean motion in rad/day for heliocentric orbit."""
    return math.sqrt(MU_SUN_AU / a_au ** 3)


def period_days(a_au: float) -> float:
    return 2.0 * math.pi / mean_motion_day(a_au)


def orbital_velocity_kms(r_au: float, a_au: float) -> float:
    """vis-viva, returns km/s."""
    v_au_day = math.sqrt(MU_SUN_AU * (2.0 / r_au - 1.0 / a_au))
    return v_au_day * AU_KM / DAY_S


def jd_of_datetime(dt) -> float:
    """UTC datetime -> Julian Date."""
    import time as _t
    ts = dt.timestamp() if hasattr(dt, "timestamp") else dt
    return ts / DAY_S + 2440587.5


def jd_now() -> float:
    import time as _t
    return _t.time() / DAY_S + 2440587.5


def datetime_of_jd(jd: float):
    from datetime import datetime, timezone
    ts = (jd - 2440587.5) * DAY_S
    return datetime.fromtimestamp(ts, tz=timezone.utc)


def jd_of_ymd(y: int, m: int, d: float) -> float:
    """Meeus algorithm; d may include fraction of day."""
    if m <= 2:
        y -= 1
        m += 12
    A = y // 100
    B = 2 - A + A // 4
    return (int(365.25 * (y + 4716)) + int(30.6001 * (m + 1))
            + d + B - 1524.5)
