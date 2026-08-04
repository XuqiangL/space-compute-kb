# -*- coding: utf-8 -*-
"""bodies.py - extended solar system bodies: moons, asteroids, KBOs,
comets, bright stars, rings, axial tilts, spheres of influence.

Moon model: circular inclined orbit about parent (documented approx).
Angles in degrees, distances in km unless noted.
"""
import math

AU_KM = 149597870.7
J2000 = 2451545.0

# name: (a_km, period_days, i_ecliptic_deg, node_deg, phase0_deg, color)
MOONS = {
    "Earth": {
        "Moon": (384400.0, 27.321661, 5.14, 125.0, 135.0, "#c8c8c8"),
    },
    "Mars": {
        "Phobos": (9376.0, 0.31891, 26.0, 160.0, 20.0, "#a08070"),
        "Deimos": (23463.0, 1.26244, 26.5, 165.0, 250.0, "#b09080"),
    },
    "Jupiter": {
        "Io": (421700.0, 1.769138, 3.1, 20.0, 10.0, "#e8d850"),
        "Europa": (670900.0, 3.551181, 3.2, 21.0, 100.0, "#d8c8b0"),
        "Ganymede": (1070400.0, 7.154553, 3.3, 22.0, 200.0, "#a89888"),
        "Callisto": (1882700.0, 16.689018, 3.4, 23.0, 300.0, "#787068"),
    },
    "Saturn": {
        "Mimas": (185404.0, 0.942422, 27.0, 40.0, 0.0, "#b8b8b0"),
        "Enceladus": (237948.0, 1.370218, 27.1, 41.0, 60.0, "#e8f0f0"),
        "Tethys": (294619.0, 1.887802, 27.0, 42.0, 120.0, "#c8c0b8"),
        "Dione": (377396.0, 2.736915, 27.1, 43.0, 180.0, "#b8b0a8"),
        "Rhea": (527108.0, 4.518212, 27.2, 44.0, 240.0, "#c0b8b0"),
        "Titan": (1221870.0, 15.945420, 27.7, 45.0, 300.0, "#e0a850"),
        "Iapetus": (3560820.0, 79.321500, 15.5, 46.0, 30.0, "#988878"),
    },
    "Uranus": {
        "Miranda": (129390.0, 1.413479, 97.8, 10.0, 0.0, "#b0c0c0"),
        "Ariel": (191020.0, 2.520379, 97.8, 11.0, 90.0, "#c0d0d0"),
        "Umbriel": (266300.0, 4.144177, 97.9, 12.0, 180.0, "#909898"),
        "Titania": (435910.0, 8.705872, 98.0, 13.0, 270.0, "#b0b8b8"),
        "Oberon": (583520.0, 13.463239, 98.0, 14.0, 45.0, "#a0a8a8"),
    },
    "Neptune": {
        # Triton: retrograde, i ~ 130 deg to ecliptic
        "Triton": (354759.0, 5.876854, 130.0, 180.0, 0.0, "#d8c8d8"),
    },
    "Pluto": {
        "Charon": (19591.0, 6.387230, 119.0, 220.0, 0.0, "#b8a898"),
    },
}

# named belt asteroids: (a, e, i, Om, wbar, M0, color)
ASTEROIDS = {
    "Ceres": (2.7675, 0.0758, 10.59, 80.31, 73.75, 188.7, "#9aa5b1"),
    "Vesta": (2.3615, 0.0887, 7.14, 103.85, 150.73, 20.8, "#c8b8a0"),
    "Pallas": (2.7728, 0.2306, 34.84, 173.10, 309.93, 78.2, "#a8b0c0"),
    "Hygiea": (3.1415, 0.1155, 3.84, 283.20, 312.35, 152.3, "#9898a0"),
}

# Kuiper belt / scattered disk: (a, e, i, Om, wbar, M0, color)
KBOS = {
    "Eris": (67.86, 0.4357, 43.82, 35.95, 187.15, 204.0, "#e8e0e0"),
    "Haumea": (43.22, 0.1950, 28.20, 121.90, 239.00, 180.0, "#d8d8e0"),
    "Makemake": (45.56, 0.1620, 28.96, 79.38, 297.30, 165.0, "#e0c8c0"),
    "Sedna": (506.0, 0.8420, 11.93, 144.50, 311.30, 358.0, "#c08878"),
}

# Halley: epoch elements, perihelion passage 1986-02-09 = JD 2446467.4.
# a fitted to the 1986->2061 apparition interval (Jupiter perturbations
# make the osculating period 75.47 yr, not the mean 75.32 yr).
COMETS = {
    "Halley": dict(a=17.857, e=0.96714, i=162.26, Om=58.42, w=111.33,
                   jd_peri=2446467.4, color="#a0e8ff"),
}

# bright stars: (name, RA hours, Dec deg, mag)  equatorial J2000
STARS = [
    ("Sirius", 6.752, -16.72, -1.46), ("Canopus", 6.399, -52.70, -0.74),
    ("Arcturus", 14.261, 19.18, -0.05), ("Vega", 18.616, 38.78, 0.03),
    ("Capella", 5.278, 46.00, 0.08), ("Rigel", 5.242, -8.20, 0.13),
    ("Procyon", 7.655, 5.22, 0.34), ("Betelgeuse", 5.919, 7.41, 0.50),
    ("Achernar", 1.629, -57.24, 0.46), ("Altair", 19.846, 8.87, 0.76),
    ("Aldebaran", 4.599, 16.51, 0.86), ("Antares", 16.490, -26.43, 0.96),
    ("Spica", 13.420, -11.16, 0.97), ("Pollux", 7.755, 28.03, 1.14),
    ("Fomalhaut", 22.961, -29.62, 1.16), ("Deneb", 20.690, 45.28, 1.25),
    ("Regulus", 10.140, 11.97, 1.35), ("Castor", 7.577, 31.89, 1.58),
    ("Bellatrix", 5.418, 6.35, 1.64), ("Alnilam", 5.604, -1.20, 1.69),
    ("Alnitak", 5.679, -1.94, 1.77), ("Polaris", 2.530, 89.26, 1.98),
    ("Dubhe", 11.062, 61.75, 1.79), ("Mirfak", 3.405, 49.86, 1.81),
    ("Rasalhague", 17.582, 12.56, 2.08), ("Alpheratz", 0.140, 29.09, 2.06),
    ("Algol", 3.136, 40.96, 2.12), ("Denebola", 11.818, 14.57, 2.11),
    ("Alphard", 9.460, -8.66, 1.98), ("Hamal", 2.120, 23.46, 2.00),
]

OBLIQUITY_DEG = 23.43928

# axial tilt to ecliptic, deg
AXIAL_TILT = {"Mercury": 0.03, "Venus": 177.4, "Earth": 23.44, "Mars": 25.19,
              "Jupiter": 3.13, "Saturn": 26.73, "Uranus": 97.77,
              "Neptune": 28.32, "Pluto": 122.5}

# mass kg (for SOI)
MASS = {"Mercury": 3.3011e23, "Venus": 4.8675e24, "Earth": 5.9724e24,
        "Mars": 6.4171e23, "Jupiter": 1.8982e27, "Saturn": 5.6834e26,
        "Uranus": 8.6810e25, "Neptune": 1.0241e26, "Pluto": 1.3030e22}
M_SUN = 1.9885e30

# Saturn rings in planet radii: (name, r_in, r_out, color)
SATURN_RINGS = [("C", 1.24, 1.53, "#6a5a48"), ("B", 1.53, 1.95, "#c8b490"),
                ("A", 2.03, 2.27, "#a89878")]
SATURN_POLE_RADEC = (40.6, 83.5)   # deg, equatorial J2000


def soi_au(planet: str, a_au: float) -> float:
    """Sphere of influence in AU: a*(m/Msun)^(2/5)."""
    return a_au * (MASS[planet] / M_SUN) ** 0.4


def moon_pos(parent_pos, a_km, period_d, i_deg, node_deg, phase0_deg, jd):
    """Heliocentric position of a moon (circular inclined approx)."""
    a = a_km / AU_KM
    th = math.radians(phase0_deg + 360.0 * (jd - J2000) / period_d)
    i = math.radians(i_deg)
    Om = math.radians(node_deg)
    xo, yo = a * math.cos(th), a * math.sin(th)
    x1, y1, z1 = xo, yo * math.cos(i), yo * math.sin(i)
    x = x1 * math.cos(Om) - y1 * math.sin(Om)
    y = x1 * math.sin(Om) + y1 * math.cos(Om)
    return (parent_pos[0] + x, parent_pos[1] + y, parent_pos[2] + z1)


def small_body_pos(a, e, i, Om, wbar, M0, jd):
    from kepler import elements_to_state
    M = (M0 + 360.0 / (2.0 * math.pi) * 2.0 * math.pi *
         (jd - J2000) / period_of_a(a)) % 360.0
    w = wbar - Om
    return elements_to_state(a, e, i, Om, w, M)[0]


def period_of_a(a_au: float) -> float:
    from kepler import period_days
    return period_days(a_au)


def halley_pos(jd):
    from kepler import elements_to_state, mean_motion_day
    c = COMETS["Halley"]
    n_deg = math.degrees(mean_motion_day(c["a"]))
    M = (n_deg * (jd - c["jd_peri"])) % 360.0
    return elements_to_state(c["a"], c["e"], c["i"], c["Om"], c["w"], M)[0]


def star_direction(ra_h, dec_deg):
    """Equatorial -> ecliptic J2000 unit vector."""
    ra = math.radians(ra_h * 15.0)
    dec = math.radians(dec_deg)
    eps = math.radians(OBLIQUITY_DEG)
    x = math.cos(dec) * math.cos(ra)
    y = math.cos(dec) * math.sin(ra) * math.cos(eps) + math.sin(dec) * math.sin(eps)
    z = -math.cos(dec) * math.sin(ra) * math.sin(eps) + math.sin(dec) * math.cos(eps)
    return (x, y, z)


def pole_direction(tilt_deg):
    """North pole unit vector (approx: tilt about the x axis)."""
    t = math.radians(tilt_deg)
    return (0.0, -math.sin(t), math.cos(t))


def belt_asteroids(n=1500, seed=42):
    """Procedural main belt with Kirkwood gaps (fixed seed, stable).

    Returns list of (a, e, i, Om, wbar, M0).
    """
    import random
    rng = random.Random(seed)
    gaps = [(2.50, 0.05), (2.82, 0.04), (2.95, 0.03), (3.27, 0.05)]
    out = []
    while len(out) < n:
        a = rng.uniform(2.06, 3.30)
        if any(abs(a - g) < w for g, w in gaps):
            continue
        e = abs(rng.gauss(0.12, 0.07))
        i = abs(rng.gauss(8.0, 5.0))
        out.append((a, min(e, 0.35), min(i, 25.0),
                    rng.uniform(0, 360), rng.uniform(0, 360),
                    rng.uniform(0, 360)))
    return out


# Earth-orbit demo craft: (a_km, i_deg, period_min, color)
ISS = dict(a_km=6791.0, i_deg=51.64, color="#ffffff")
CALCSAT = dict(a_km=6921.0, i_deg=97.6, color="#7fffd4")  # 550km SSO


def earth_orbit_period_s(a_km: float) -> float:
    MU_E = 398600.44       # km^3/s^2
    return 2.0 * math.pi * math.sqrt(a_km ** 3 / MU_E)


def earth_orbit_pos(earth_pos, a_km, i_deg, jd, phase0_deg=0.0,
                    node_deg=0.0):
    a = a_km / AU_KM
    n = 2.0 * math.pi / earth_orbit_period_s(a_km) * 86400.0  # rad/day
    th = math.radians(phase0_deg) + n * (jd - J2000)
    i = math.radians(i_deg)
    Om = math.radians(node_deg)
    xo, yo = a * math.cos(th), a * math.sin(th)
    x1, y1, z1 = xo, yo * math.cos(i), yo * math.sin(i)
    x = x1 * math.cos(Om) - y1 * math.sin(Om)
    y = x1 * math.sin(Om) + y1 * math.cos(Om)
    return (earth_pos[0] + x, earth_pos[1] + y, earth_pos[2] + z1)
