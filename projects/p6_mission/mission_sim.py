"""p6_mission: end-to-end mission simulation for the Suangxing-1
(150 kg, 550 km dawn-dusk SSO, 1 kW compute payload, 3-year life).

This is the integrator project: it chains the p1..p5 toolkits into a
single launch-to-deorbit timeline, mirroring module 12's case study:

  launch -> parking orbit -> Hohmann raise -> commissioning
  -> routine operations (compute tasks, SAA avoidance, thermal &
     power budget tracking, SEU logging, downlink in ground windows)
  -> end-of-life deorbit

All numbers traceable to KB modules; tests lock the worked examples.
"""
import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p1_orbit"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p2_thermal"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p3_link"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p4_radiation"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "p5_scheduler"))

import orbit_sim as orb
import thermal_sim as thm
import link_budget as lb
import radiation_sim as rad
import scheduler_sim as sch


# ---------------- spacecraft configuration (module 01 budget tables) --------
CONFIG = {
    "name": "Suangxing-1",
    "mass_kg": 150.0,
    "alt_parking_km": 400.0,
    "alt_ops_km": 550.0,
    "compute_tops": 500.0,          # effective after derating
    "compute_power_w": 1000.0,
    "platform_power_w": 225.0,
    "solar_area_m2": 7.0,
    "solar_flux_w_m2": 300.0,       # BOL effective (module 03)
    "eol_factor": 0.85,
    "battery_wh": 6000.0,
    "radiator_area_m2": 3.5,
    "radiator_eps": 0.80,
    "radiator_temp_k": 313.0,
    "shield_mm_al": 3.0,
    "life_years": 3.0,
}


def phase_launch_and_raise(cfg) -> dict:
    """Phase 1: launch to parking orbit, Hohmann raise to ops orbit."""
    r1 = orb.R_EARTH + cfg["alt_parking_km"]
    r2 = orb.R_EARTH + cfg["alt_ops_km"]
    dv1, dv2, t_h = orb.hohmann_transfer(r1, r2)
    dv_total_ms = (dv1 + dv2) * 1000.0
    prop = orb.propellant_mass(dv_total_ms + 20.0,   # + injection trim
                               cfg["mass_kg"], isp_s=220.0)
    return {
        "dv_raise_ms": dv_total_ms,
        "transfer_min": t_h / 60.0,
        "propellant_kg": prop,
    }


def phase_power_check(cfg) -> dict:
    """Phase 2: verify EOL power budget (module 03 sizing formulas)."""
    p_bol = cfg["solar_area_m2"] * cfg["solar_flux_w_m2"]
    p_eol = p_bol * cfg["eol_factor"]
    p_load = cfg["compute_power_w"] * 0.7 + cfg["platform_power_w"]
    return {
        "p_bol_w": p_bol,
        "p_eol_w": p_eol,
        "p_load_avg_w": p_load,
        "margin_pct": (p_eol / p_load - 1.0) * 100.0,
        "ok": p_eol >= p_load * 1.15,
    }


def phase_thermal_check(cfg) -> dict:
    """Phase 3: radiator capacity vs dissipation (module 05)."""
    cap_per_m2 = thm.radiator_capacity(cfg["radiator_eps"],
                                       cfg["radiator_temp_k"])
    cap = cap_per_m2 * cfg["radiator_area_m2"] * 0.9   # env knockdown
    q = cfg["compute_power_w"] + cfg["platform_power_w"] * 0.5
    r_chain = 0.145 * (350.0 / cfg["compute_power_w"] * 2)  # scaled chain
    tj = thm.junction_temp(cfg["radiator_temp_k"], 300.0, 0.145)
    return {
        "capacity_w": cap,
        "dissipation_w": q,
        "margin_pct": (cap / q - 1.0) * 100.0,
        "junction_c_derated": tj - 273.15,
        "ok": cap >= q * 1.2 and tj - 273.15 <= 85.0,
    }


def phase_radiation_check(cfg) -> dict:
    """Phase 4: TID behind shielding + SEU rates (module 06)."""
    d_surface = 80.0    # krad/5yr class surface environment
    d5 = rad.tid_shielding(d_surface, cfg["shield_mm_al"], t0_mm=2.0)
    d_mission = d5 * cfg["life_years"] / 5.0
    rate = rad.seu_rate_per_bit_day(1e-7, 2.0, 20.0, 1.5, 1e-4)
    upsets = rad.memory_upsets_per_day(rate, 8e9)     # 8 GB exposed
    t_ckpt = rad.checkpoint_interval_young(60.0, 86400.0)
    return {
        "tid_mission_krad": d_mission,
        "cots_ok": d_mission < 20.0,        # COTS qualified to 20 krad
        "seu_per_day_8gb": upsets,
        "checkpoint_s": t_ckpt,
    }


def phase_operations(cfg, days: int = 3, tasks_per_day: int = 20) -> dict:
    """Phase 5: simulate routine operations with the p5 scheduler."""
    sats = sch.make_constellation(1)
    sats[0].compute_tops = cfg["compute_tops"]
    scheduler = sch.Scheduler(sats, downlink_rate_gbps=1.0)
    done, missed = 0, 0
    t_now = 0.0
    for day in range(days):
        for k in range(tasks_per_day):
            task = sch.Task(
                name=f"d{day}-t{k}", tops_needed=2000.0,
                data_in_gb=5.0, data_out_gb=0.5,
                deadline_min=t_now + 1440.0,
            )
            sat = scheduler.assign(task, t_now)
            if sat is None:
                missed += 1
                continue
            end = scheduler.run_task(sat, task, t_now)
            if end <= task.deadline_min:
                done += 1
            else:
                missed += 1
            t_now += 1440.0 / tasks_per_day
        # daily reset of thermal/soc (dawn-dusk SSO: near-continuous sun)
        for s in sats:
            s.temp_c = 35.0
            s.battery_wh = s.battery_capacity_wh
    vol = scheduler.downlink_volume_tb(0.0, 1440.0)
    return {
        "days": days,
        "tasks_done": done,
        "tasks_missed": missed,
        "success_rate": done / max(1, done + missed),
        "daily_downlink_tb": vol,
        "daily_output_tb": tasks_per_day * 0.5 / 1000.0,
    }


def phase_deorbit(cfg) -> dict:
    """Phase 6: EOL deorbit to 200 km perigee (module 02 sec 6.3)."""
    dv = orb.deorbit_dv(cfg["alt_ops_km"], 200.0)
    prop = orb.propellant_mass(dv, cfg["mass_kg"], isp_s=220.0)
    return {"dv_deorbit_ms": dv, "propellant_kg": prop}


def run_mission(cfg=CONFIG, sim_days: int = 3) -> dict:
    """Full mission chain; every phase must pass its gate."""
    results = {
        "launch": phase_launch_and_raise(cfg),
        "power": phase_power_check(cfg),
        "thermal": phase_thermal_check(cfg),
        "radiation": phase_radiation_check(cfg),
        "operations": phase_operations(cfg, days=sim_days),
        "deorbit": phase_deorbit(cfg),
    }
    gates = [
        results["power"]["ok"],
        results["thermal"]["ok"],
        results["radiation"]["cots_ok"],
        results["operations"]["success_rate"] > 0.95,
        results["operations"]["daily_downlink_tb"]
            > results["operations"]["daily_output_tb"],
    ]
    results["mission_go"] = all(gates)
    return results


if __name__ == "__main__":
    import json
    out = run_mission()
    print(json.dumps(out, indent=2, default=str))
