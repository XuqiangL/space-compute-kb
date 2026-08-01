"""p2_thermal: spacecraft thermal toolkit for the space-compute KB.

Implements module 01 (equilibrium temperature) and module 05
(radiator sizing, thermal resistance network, transient RC, PCM trade).

Units: SI (W, m, K, kg, s).
"""
import math

SIGMA = 5.670374419e-8   # W/(m^2 K^4)
SOLAR_CONSTANT = 1361.0  # W/m^2
EARTH_IR = 237.0         # W/m^2 at LEO, Earth-facing
ALBEDO = 0.30
DEEP_SPACE_K = 3.0


def equilibrium_plate(alpha: float, eps: float,
                      solar: float = SOLAR_CONSTANT,
                      q_internal: float = 0.0,
                      q_extra: float = 0.0) -> float:
    """Flat plate facing the Sun, insulated back (module 01 sec 3.2.2).

    alpha*S + q_internal + q_extra = eps*sigma*T^4
    q_internal/q_extra are total W over 1 m^2 reference area.
    """
    absorbed = alpha * solar + q_internal + q_extra
    return (absorbed / (eps * SIGMA)) ** 0.25


def equilibrium_sphere(alpha: float, eps: float,
                       solar: float = SOLAR_CONSTANT) -> float:
    """Isothermal sphere (module 01 sec 3.2.3): T = (alpha*S/(4*eps*sigma))^1/4."""
    return (alpha * solar / (4.0 * eps * SIGMA)) ** 0.25


def radiator_capacity(eps: float, t_k: float,
                      t_sink: float = DEEP_SPACE_K) -> float:
    """Heat rejection per m^2 (module 05 sec 1.2): Q/A = eps*sigma*(T^4 - Tsink^4)."""
    return eps * SIGMA * (t_k ** 4 - t_sink ** 4)


def radiator_area(q_w: float, eps: float, t_k: float,
                  env_factor: float = 0.9, margin: float = 1.2,
                  t_sink: float = DEEP_SPACE_K) -> float:
    """Radiator sizing with environmental knockdown and margin.

    env_factor: accounts for Earth IR / albedo intrusion on the panel.
    margin: engineering margin (module 05 example uses 1.2).
    """
    cap = radiator_capacity(eps, t_k, t_sink) * env_factor
    return q_w * margin / cap


class ThermalNode:
    """Lumped-capacitance node for transient RC networks."""

    def __init__(self, name: str, capacity_j_per_k: float, t0_k: float):
        self.name = name
        self.c = capacity_j_per_k
        self.t = t0_k
        self.links = []      # (other_node, conductance W/K)
        self.heat_w = 0.0    # internal dissipation

    def connect(self, other: "ThermalNode", conductance: float):
        self.links.append((other, conductance))
        other.links.append((self, conductance))


def simulate_network(nodes, t_end_s: float, dt_s: float,
                     radiators=None):
    """Explicit Euler transient solve of a node network.

    radiators: list of (node, eps*area) radiating to deep space.
    Returns list of (time, {name: T}) snapshots (every 100 steps).
    """
    radiators = radiators or []
    history = []
    steps = int(t_end_s / dt_s)
    for k in range(steps):
        dts = {}
        for n in nodes:
            dq = n.heat_w
            for other, g in n.links:
                if id(other) > id(n):      # count each link once per node
                    pass
                dq += g * (other.t - n.t) if id(other) < id(n) else 0.0
            # recompute properly: sum over links without double counting
            dq = n.heat_w
            for other, g in n.links:
                dq += g * (other.t - n.t)
            for node, ea in radiators:
                if node is n:
                    dq -= ea * SIGMA * (n.t ** 4 - DEEP_SPACE_K ** 4)
            dts[n.name] = n.t + dq / n.c * dt_s
        for n in nodes:
            n.t = dts[n.name]
        if k % 100 == 0:
            history.append((k * dt_s, {n.name: n.t for n in nodes}))
    history.append((steps * dt_s, {n.name: n.t for n in nodes}))
    return history


def conduction_r(thickness_m: float, k_w_mk: float, area_m2: float) -> float:
    """Conduction resistance R = L/(kA)."""
    return thickness_m / (k_w_mk * area_m2)


def contact_r(r_k_cm2_w: float, area_cm2: float) -> float:
    """Contact/TIM resistance from specific value (K*cm^2/W)."""
    return r_k_cm2_w / area_cm2


def junction_temp(t_sink_k: float, q_w: float, r_total: float) -> float:
    """T_j = T_sink + Q * sum(R)  (module 05 sec 2.1)."""
    return t_sink_k + q_w * r_total


def pcm_mass(peak_w: float, duration_s: float,
             latent_j_kg: float = 200e3) -> float:
    """PCM mass to absorb a power pulse (module 05 sec 3.4)."""
    return peak_w * duration_s / latent_j_kg


def heat_pipe_capillary_pressure(sigma_lv: float, r_eff_m: float,
                                 theta_deg: float = 0.0) -> float:
    """Capillary pressure head: dP = 2*sigma*cos(theta)/r_eff (Pa)."""
    return 2.0 * sigma_lv * math.cos(math.radians(theta_deg)) / r_eff_m


def solder_fatigue_life(n_f_ref: float, dt_ref: float, dt_new: float,
                        m: float = 2.0) -> float:
    """Coffin-Manson scaling: N_new = N_ref * (dT_ref/dT_new)^m (module 01 sec 3.3.3)."""
    return n_f_ref * (dt_ref / dt_new) ** m
