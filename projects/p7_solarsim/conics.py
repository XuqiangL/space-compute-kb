"""conics.py - state vectors <-> elements, maneuvers, Lagrange points.

Enables KSP-style maneuver nodes: from a position+velocity get osculating
elements; applying a prograde/retrograde dV produces a new conic.
"""
import math

from kepler import AU_KM, DAY_S, MU_SUN_AU, MU_SUN_KM


def state_to_elements(r, v, mu=MU_SUN_AU):
    """r (AU), v (AU/day) -> dict(a, e, i, Om, w, nu)."""
    rmag = math.sqrt(sum(c * c for c in r))
    vmag2 = sum(c * c for c in v)
    h = (r[1] * v[2] - r[2] * v[1], r[2] * v[0] - r[0] * v[2],
         r[0] * v[1] - r[1] * v[0])
    hmag = math.sqrt(sum(c * c for c in h))
    n = (-h[1], h[0], 0.0)
    nmag = math.sqrt(n[0] ** 2 + n[1] ** 2)
    # eccentricity vector
    evec = tuple((vmag2 - mu / rmag) * r[i] -
                 (r[0] * v[0] + r[1] * v[1] + r[2] * v[2]) * v[i]
                 for i in range(3))
    evec = tuple(c / mu for c in evec)
    e = math.sqrt(sum(c * c for c in evec))
    energy = vmag2 / 2.0 - mu / rmag
    a = -mu / (2.0 * energy)
    i = math.degrees(math.acos(max(-1.0, min(1.0, h[2] / hmag))))
    Om = 0.0 if nmag < 1e-12 else math.degrees(math.atan2(n[1], n[0])) % 360.0
    w = 0.0
    nu = 0.0
    if nmag > 1e-12 and e > 1e-10:
        w = math.degrees(math.atan2(
            (n[0] * evec[1] - n[1] * evec[0]) / nmag / e,
            (n[0] * evec[0] + n[1] * evec[1]) / nmag / e)) % 360.0
    if e > 1e-10:
        nu = math.degrees(math.atan2(
            sum((evec[j] * r[((j + 1) % 3)] * h[(j + 2) % 3] -
                 evec[j] * r[((j + 2) % 3)] * h[(j + 1) % 3])
                for j in range(3)) / e / rmag / hmag,
            sum(evec[j] * r[j] for j in range(3)) / e / rmag)) % 360.0
    return dict(a=a, e=e, i=i, Om=Om, w=w, nu=nu, r=rmag)


def velocity_on_elements(a, e, wbar_deg, M0_deg, jd_epoch, jd):
    """Numerical velocity (AU/day) on a coplanar Keplerian arc at jd."""
    from transfer import transfer_pos_at
    dt = 1e-4
    p0 = transfer_pos_at(a, e, wbar_deg, M0_deg, jd_epoch, jd - dt)
    p1 = transfer_pos_at(a, e, wbar_deg, M0_deg, jd_epoch, jd + dt)
    return tuple((p1[k] - p0[k]) / (2.0 * dt) for k in range(3))


def apply_prograde_dv(r, v, dv_kms):
    """Scale velocity vector by prograde dV (km/s -> AU/day factor)."""
    vmag = math.sqrt(sum(c * c for c in v))
    dv = dv_kms * DAY_S / AU_KM
    f = (vmag + dv) / vmag
    return tuple(c * f for c in v)


def M_from_nu(nu_deg, e):
    """True anomaly -> mean anomaly (deg), elliptic or hyperbolic."""
    nu = math.radians(nu_deg)
    if e > 1.0:
        sF = math.sqrt(e * e - 1.0) * math.sin(nu) / (1.0 + e * math.cos(nu))
        F = math.asinh(max(-1e15, min(1e15, sF)))
        return math.degrees(e * math.sinh(F) - F)
    E = 2.0 * math.atan2(math.sqrt(1.0 - e) * math.sin(nu / 2.0),
                         math.sqrt(1.0 + e) * math.cos(nu / 2.0))
    return math.degrees(E - e * math.sin(E))


def pos_on_leg(leg, jd):
    """Position on a conic leg dict(a,e,wbar,M0,jd0) at jd."""
    from kepler import elements_to_state
    n = math.degrees(math.sqrt(MU_SUN_AU / abs(leg["a"]) ** 3))
    M = (leg["M0"] + n * (jd - leg["jd0"])) % 360.0
    return elements_to_state(leg["a"], leg["e"], 0.0, 0.0,
                             leg["wbar"], M)[0]


def leg_from_state(pos, vel, jd):
    """State vector -> leg dict (coplanar wbar convention)."""
    el = state_to_elements(pos, vel)
    wbar = (el["Om"] + el["w"]) % 360.0
    M0 = M_from_nu(el["nu"], el["e"]) % 360.0
    return dict(a=el["a"], e=el["e"], wbar=wbar, M0=M0, jd0=jd)


def lagrange_points(earth_pos):
    """Sun-planet L1..L5 for unit-Sun at origin. r = planet distance (AU)."""
    ex, ey, ez = earth_pos
    R = math.sqrt(ex * ex + ey * ey + ez * ez)
    ux, uy, uz = ex / R, ey / R, ez / R
    mu_r = 3.0035e-6          # Earth/Sun mass ratio
    h = (mu_r / 3.0) ** (1.0 / 3.0)
    l1 = tuple(u * R * (1 - h) for u in (ux, uy, uz))
    l2 = tuple(u * R * (1 + h) for u in (ux, uy, uz))
    l3 = (-ux * R, -uy * R, -uz * R)
    c60 = math.cos(math.radians(60.0))
    s60 = math.sin(math.radians(60.0))
    l4 = (ex * c60 - ey * s60, ex * s60 + ey * c60, ez)
    l5 = (ex * c60 + ey * s60, -ex * s60 + ey * c60, ez)
    return {"L1": l1, "L2": l2, "L3": l3, "L4": l4, "L5": l5}
