"""p1_orbit: orbital mechanics toolkit for the space-compute KB.

Implements the formulas derived in module 02:
  - vis-viva, orbital period
  - Hohmann transfer delta-v
  - J2 nodal regression and SSO inclination solver
  - atmospheric drag decay and lifetime estimation
  - plane phasing drift (deployment)

All units: km, s, kg unless noted. mu_earth = 398600.4418 km^3/s^2.
"""
import math

MU = 398600.4418          # km^3/s^2
R_EARTH = 6378.137        # km (equatorial)
J2 = 1.08262668e-3
OMEGA_EARTH = 7.2921159e-5  # rad/s
SOLAR_YEAR_S = 365.25 * 86400.0


def orbital_period(a_km: float) -> float:
    """Kepler 3rd law: T = 2*pi*sqrt(a^3/mu)."""
    return 2.0 * math.pi * math.sqrt(a_km ** 3 / MU)


def circular_velocity(r_km: float) -> float:
    return math.sqrt(MU / r_km)


def vis_viva(r_km: float, a_km: float) -> float:
    """v^2 = mu*(2/r - 1/a)."""
    return math.sqrt(MU * (2.0 / r_km - 1.0 / a_km))


def hohmann_transfer(r1_km: float, r2_km: float):
    """Coplanar Hohmann transfer between circular orbits.

    Returns (dv1, dv2, t_transfer_s). See module 02 section 2.1.
    """
    a_t = 0.5 * (r1_km + r2_km)
    v1 = circular_velocity(r1_km)
    v2 = circular_velocity(r2_km)
    v_tp = vis_viva(r1_km, a_t)
    v_ta = vis_viva(r2_km, a_t)
    dv1 = abs(v_tp - v1)
    dv2 = abs(v2 - v_ta)
    t_transfer = math.pi * math.sqrt(a_t ** 3 / MU)
    return dv1, dv2, t_transfer


def plane_change_dv(v_kms: float, delta_i_deg: float) -> float:
    """Pure inclination change: dv = 2*v*sin(di/2)."""
    return 2.0 * v_kms * math.sin(math.radians(delta_i_deg) / 2.0)


def mean_motion(a_km: float) -> float:
    """Mean motion n in rad/s."""
    return math.sqrt(MU / a_km ** 3)


def j2_nodal_regression(a_km: float, e: float, i_deg: float) -> float:
    """Nodal regression rate dOmega/dt in rad/s (positive = eastward).

    dOmega/dt = -(3/2)*J2*n*(Re/p)^2*cos(i)
    """
    n = mean_motion(a_km)
    p = a_km * (1.0 - e ** 2)
    return -1.5 * J2 * n * (R_EARTH / p) ** 2 * math.cos(math.radians(i_deg))


def sso_inclination(a_km: float, e: float = 0.0) -> float:
    """Solve inclination for a sun-synchronous orbit at altitude a.

    Condition: dOmega/dt = +360 deg per tropical year (eastward).
    Returns inclination in degrees. Raises ValueError if impossible.
    """
    target = 2.0 * math.pi / SOLAR_YEAR_S  # rad/s eastward
    n = mean_motion(a_km)
    p = a_km * (1.0 - e ** 2)
    cos_i = -target / (1.5 * J2 * n * (R_EARTH / p) ** 2)
    if not (-1.0 <= cos_i <= 1.0):
        raise ValueError("SSO not achievable at this semi-major axis")
    return math.degrees(math.acos(cos_i))


def drag_decay_per_day(a_km: float, mass_kg: float, area_m2: float,
                       rho_kg_m3: float, cd: float = 2.2) -> float:
    """Semi-major axis decay per day for a circular orbit (km/day).

    da/dt = -(rho * v * a) / B,  B = m / (Cd * A)
    rho in kg/m^3, area in m^2 -> convert units carefully.
    """
    B = mass_kg / (cd * area_m2)            # kg/m^2
    v = circular_velocity(a_km) * 1000.0    # m/s
    a_m = a_km * 1000.0                     # m
    da_dt = -(rho_kg_m3 * v * a_m) / B      # m/s
    return da_dt * 86400.0 / 1000.0         # km/day


def lifetime_years(alt_km: float, mass_kg: float, area_m2: float,
                   rho_kg_m3: float, cd: float = 2.2,
                   floor_alt_km: float = 120.0) -> float:
    """Crude lifetime: integrate decay assuming constant density scale.

    Uses stepwise integration with density doubling every 30 km descent
    below start (very rough but captures the runaway nature of reentry).
    """
    a = R_EARTH + alt_km
    rho = rho_kg_m3
    total_days = 0.0
    while a - R_EARTH > floor_alt_km and total_days < 365.0 * 1000:
        decay = abs(drag_decay_per_day(a, mass_kg, area_m2, rho, cd))
        if decay <= 0:
            return float("inf")
        # step: lose 5 km or scale to remaining altitude
        step_km = min(5.0, a - R_EARTH - floor_alt_km)
        days = step_km / decay
        total_days += days
        a -= step_km
        rho *= 2.0 ** (step_km / 30.0)   # density doubles every 30 km down
    return total_days / 365.25


def phasing_drift_rate_deg_per_day(a_ref_km: float, delta_a_km: float) -> float:
    """Relative drift rate (deg/day) for a satellite offset by delta_a.

    drift ~ (3/2)*(da/a)*n  in rad/s -> deg/day.
    """
    n = mean_motion(a_ref_km)  # rad/s
    drift_rad_s = 1.5 * (delta_a_km / a_ref_km) * n
    return math.degrees(drift_rad_s) * 86400.0


def propellant_mass(dv_m_s: float, m0_kg: float, isp_s: float) -> float:
    """Rocket equation: propellant needed for dv. m_prop = m0*(1-exp(-dv/(isp*g0)))."""
    g0 = 9.80665
    return m0_kg * (1.0 - math.exp(-dv_m_s / (isp_s * g0)))


def deorbit_dv(alt_km: float, perigee_alt_km: float = 200.0) -> float:
    """Delta-v to lower perigee from circular orbit to perigee_alt (m/s)."""
    r1 = R_EARTH + alt_km
    r2 = R_EARTH + perigee_alt_km
    a_t = 0.5 * (r1 + r2)
    v_circ = circular_velocity(r1)
    v_trans = vis_viva(r1, a_t)
    return abs(v_circ - v_trans) * 1000.0
