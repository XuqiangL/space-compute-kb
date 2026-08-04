"""ephemeris.py - planetary positions from JPL approximate Keplerian
elements (valid 1800-2050, arcminute-class accuracy for inner planets).

Table: 'Keplerian Elements for Approximate Positions of the Major Planets'
(JPL Solar System Dynamics). Elements at J2000 + rates per Julian century:
  a (AU), e, I (deg), L (deg), long.peri (deg), long.node (deg)
Moon: Meeus low-precision geocentric model (arcminute class).
"""
import math

from kepler import elements_to_state

J2000 = 2451545.0

# name: (a0, da, e0, de, I0, dI, L0, dL, p0, dp, O0, dO, color, radius_km)
PLANETS = {
    "Mercury": (0.38709927, 0.00000037, 0.20563593, 0.00001906,
                7.00497902, -0.00594749, 252.25032350, 149472.67411175,
                77.45779628, 0.16047689, 48.33076593, -0.12534081,
                "#b8a898", 2439.7),
    "Venus": (0.72333566, 0.00000390, 0.00677672, -0.00004107,
              3.39467605, -0.00078890, 181.97909950, 58517.81538729,
              131.60246718, 0.00268329, 76.67984255, -0.27769418,
              "#e8c878", 6051.8),
    "Earth": (1.00000261, 0.00000562, 0.01671123, -0.00004392,
              -0.00001531, -0.01294668, 100.46457166, 35999.37244981,
              102.93768193, 0.32327364, 0.0, 0.0,
              "#4f8ff7", 6371.0),
    "Mars": (1.52371034, 0.00001847, 0.09339410, 0.00007882,
             1.84969142, -0.00813131, -4.55343205, 19140.30268499,
             -23.94362959, 0.44441088, 49.55953891, -0.29257343,
             "#e06040", 3389.5),
    "Jupiter": (5.20288700, -0.00011607, 0.04838624, -0.00013253,
                1.30439695, -0.00183714, 34.39644051, 3034.74612775,
                14.72847983, 0.21252668, 100.47390909, 0.20469106,
                "#d8a860", 69911.0),
    "Saturn": (9.53667594, -0.00125060, 0.05386179, -0.00050991,
               2.48599187, 0.00193609, 49.95424423, 1222.49362201,
               92.59887831, -0.41897216, 113.66242448, -0.28867794,
               "#e0c890", 58232.0),
    "Uranus": (19.18916464, -0.00196176, 0.04725744, -0.00004397,
               0.77263783, -0.00242939, 313.23810451, 428.48202785,
               170.95427630, 0.40805281, 74.01692503, 0.04240589,
               "#88d8e0", 25362.0),
    "Neptune": (30.06992276, 0.00026291, 0.00859048, 0.00005105,
                1.77004347, 0.00035372, -55.12002969, 218.45945325,
                44.96476227, -0.32241464, 131.78422574, -0.00508664,
                "#4878f0", 24622.0),
    "Pluto": (39.48211675, -0.00031596, 0.24882730, 0.00005170,
              17.14001206, 0.00004818, 238.92903833, 145.20780515,
              224.06891629, -0.04062942, 110.30393684, -0.01183482,
              "#c0a890", 1188.3),
}

CN = {"Mercury": "水星", "Venus": "金星", "Earth": "地球", "Mars": "火星",
      "Jupiter": "木星", "Saturn": "土星", "Uranus": "天王星",
      "Neptune": "海王星", "Pluto": "冥王星", "Moon": "月球", "Sun": "太阳"}


def planet_elements(name: str, jd: float):
    """(a, e, i, Omega, w, M) at jd; angles in degrees."""
    t = PLANETS[name]
    T = (jd - J2000) / 36525.0
    a = t[0] + t[1] * T
    e = t[2] + t[3] * T
    I = t[4] + t[5] * T
    L = t[6] + t[7] * T
    p = t[8] + t[9] * T       # longitude of perihelion
    O = t[10] + t[11] * T     # longitude of ascending node
    w = p - O
    M = L - p
    return a, e, I, O, w, M


def planet_state(name: str, jd: float):
    """Heliocentric ecliptic position (AU) and true anomaly."""
    a, e, I, O, w, M = planet_elements(name, jd)
    return elements_to_state(a, e, I, O, w, M)


def planet_elements_for_display(name: str, jd: float):
    a, e, I, O, w, M = planet_elements(name, jd)
    p = (w + O) % 360.0
    return {"a": a, "e": e, "i": I, "Om": O, "wbar": p, "M": M % 360.0}


def moon_state_geo(jd: float):
    """Geocentric ecliptic lon/lat/dist of the Moon (Meeus low precision).

    Returns (lon_deg, lat_deg, dist_km).
    """
    T = (jd - J2000) / 36525.0
    Lp = 218.3164477 + 481267.88123421 * T
    D = 297.8501921 + 445267.1114034 * T
    M = 357.5291092 + 35999.0502909 * T
    Mp = 134.9633964 + 477198.8675055 * T
    F = 93.2720950 + 483202.0175233 * T
    rD, rM, rMp, rF = (math.radians(x) for x in (D, M, Mp, F))
    lon = (Lp + 6.289 * math.sin(rMp)
           - 1.274 * math.sin(2 * rD - rMp)
           + 0.658 * math.sin(2 * rD)
           - 0.186 * math.sin(rM)
           - 0.114 * math.sin(2 * rF))
    lat = (5.128 * math.sin(rF)
           + 0.281 * math.sin(rMp + rF)
           + 0.278 * math.sin(rMp - rF))
    dist = (385001.0 - 20905.0 * math.cos(rMp)
            - 3699.0 * math.cos(2 * rD - rMp)
            - 2956.0 * math.cos(2 * rD))
    return lon % 360.0, lat, dist


def moon_state_helio(jd: float):
    """Heliocentric ecliptic position of the Moon (AU)."""
    lon, lat, dist = moon_state_geo(jd)
    ex, ey, ez = planet_state("Earth", jd)[0]
    d_au = dist / 149597870.7
    rl, rb = math.radians(lon), math.radians(lat)
    mx = d_au * math.cos(rb) * math.cos(rl)
    my = d_au * math.cos(rb) * math.sin(rl)
    mz = d_au * math.sin(rb)
    return (ex + mx, ey + my, ez + mz), dist
