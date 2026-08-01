"""p3_link: RF and optical link budget toolkit (module 07).

Implements Friis equation, Eb/N0 budgets, DVB-S2 thresholds,
optical link budgets, point-ahead angle, and cloud availability.

Units: dB domain where natural; Hz, m, W otherwise.
"""
import math

C_LIGHT = 299792458.0        # m/s
K_BOLTZMANN_DB = -228.6      # dBW/(K Hz)

# DVB-S2 representative Es/N0 thresholds (dB), module 07 sec 1.3
MODCOD_TABLE = {
    "QPSK_1/2": 4.5,
    "8PSK_2/3": 5.5,
    "16APSK_3/4": 10.0,
    "32APSK_4/5": 16.0,
}


def db(x: float) -> float:
    return 10.0 * math.log10(x)


def undb(x_db: float) -> float:
    return 10.0 ** (x_db / 10.0)


def fspl_db(distance_m: float, freq_hz: float) -> float:
    """Free-space path loss: (4*pi*d/lambda)^2 in dB."""
    lam = C_LIGHT / freq_hz
    return 20.0 * math.log10(4.0 * math.pi * distance_m / lam)


def antenna_gain_db(diameter_m: float, freq_hz: float,
                    efficiency: float = 0.6) -> float:
    """Parabolic antenna gain G = eff*(pi*D/lambda)^2."""
    lam = C_LIGHT / freq_hz
    return db(efficiency * (math.pi * diameter_m / lam) ** 2)


def rf_link_budget(p_tx_w: float, g_tx_db: float, g_t_dbk: float,
                   distance_m: float, freq_hz: float,
                   data_rate_bps: float, modcod: str,
                   misc_loss_db: float = 2.5) -> dict:
    """Full RF link budget following module 07 sec 1.4.

    g_t_dbk: ground station G/T in dB/K. misc_loss: atmosphere+pointing+feed.
    Returns dict with eirp, cn0, ebn0, margin.
    """
    eirp = db(p_tx_w) + g_tx_db
    cn0 = eirp - fspl_db(distance_m, freq_hz) - misc_loss_db \
        + g_t_dbk - K_BOLTZMANN_DB
    ebn0 = cn0 - db(data_rate_bps)
    required = MODCOD_TABLE[modcod]
    return {
        "eirp_dbw": eirp,
        "fspl_db": fspl_db(distance_m, freq_hz),
        "cn0_dbhz": cn0,
        "ebn0_db": ebn0,
        "required_db": required,
        "margin_db": ebn0 - required,
    }


def optical_beam_divergence_urad(wavelength_m: float,
                                 aperture_m: float) -> float:
    """Diffraction-limited half-angle divergence theta ~ lambda/(pi*w0),
    with w0 ~ aperture/2 -> theta ~ 2*lambda/(pi*D). Returns microrad."""
    return 2.0 * wavelength_m / (math.pi * aperture_m) * 1e6


def optical_antenna_gain_db(diameter_m: float, wavelength_m: float) -> float:
    """Optical 'antenna gain' G = (pi*D/lambda)^2 (module 07 sec 2.2)."""
    return db((math.pi * diameter_m / wavelength_m) ** 2)


def optical_link_budget(p_tx_w: float, d_tx_m: float, d_rx_m: float,
                        wavelength_m: float, distance_m: float,
                        pointing_loss_db: float = 3.0,
                        optics_eff: float = 0.5) -> dict:
    """Optical inter-satellite link budget (module 07 sec 2.2)."""
    g_tx = optical_antenna_gain_db(d_tx_m, wavelength_m)
    g_rx = optical_antenna_gain_db(d_rx_m, wavelength_m)
    fspl = 20.0 * math.log10(4.0 * math.pi * distance_m / wavelength_m)
    p_rx_dbm = db(p_tx_w) + 30.0 + g_tx + g_rx - fspl \
        - pointing_loss_db + db(optics_eff)
    return {
        "g_tx_db": g_tx, "g_rx_db": g_rx, "fspl_db": fspl,
        "p_rx_dbm": p_rx_dbm,
        "p_rx_uw": undb(p_rx_dbm - 30.0) * 1e6,
    }


def point_ahead_urad(v_rel_m_s: float, distance_m: float) -> float:
    """Point-ahead angle = v_rel * (d/c) / d = v_rel/c (module 07 sec 2.3.2).

    Note the elegant cancellation: angle depends only on relative velocity.
    """
    return v_rel_m_s / C_LIGHT * 1e6


def cloud_availability(n_sites: float, p_clear_single: float) -> float:
    """Site-diversity availability: 1 - (1-p)^n (module 07 sec 3.1)."""
    return 1.0 - (1.0 - p_clear_single) ** n_sites


def daily_downlink_tb(rate_bps: float, passes_per_day: int,
                      pass_duration_s: float) -> float:
    """Daily downlink volume in TB."""
    return rate_bps * passes_per_day * pass_duration_s / 8.0 / 1e12
