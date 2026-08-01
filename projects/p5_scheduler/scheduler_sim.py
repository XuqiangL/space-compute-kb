"""p5_scheduler: constellation compute-task scheduling simulator (module 09).

Simulates the 4-D joint scheduling problem (compute / energy / link /
storage) over a repeating orbit, including SAA avoidance and ground
station downlink windows.

Simplified geometry: circular SSO, period ~95.5 min; SAA passages and
ground contacts are given as periodic window tables (deterministic,
reproducible — this is a scheduling sim, not an orbit propagator).
"""
import math
from dataclasses import dataclass, field


ORBIT_PERIOD_MIN = 95.5


@dataclass
class Satellite:
    name: str
    compute_tops: float
    storage_tb: float
    battery_wh: float
    battery_capacity_wh: float
    temp_c: float = 35.0
    queue: list = field(default_factory=list)

    @property
    def soc(self) -> float:
        return self.battery_wh / self.battery_capacity_wh


@dataclass
class Task:
    name: str
    tops_needed: float          # total compute, TOPS (not per second)
    data_in_gb: float
    data_out_gb: float
    deadline_min: float
    sla: str = "silver"         # gold = dual-execution, silver, copper
    submit_min: float = 0.0
    done_min: float = None
    assigned: str = None


def saa_windows(period_min: float = ORBIT_PERIOD_MIN):
    """SAA passages: ~6 per day, 10 min each, centered at fixed phases
    of selected orbits (module 01 sec 4.2). Returns list of (start,end)
    in minutes over 24 h."""
    windows = []
    # orbits that cross the SAA: pick 6 of ~15 daily orbits
    for k in range(6):
        center = (k * 4 + 1.5) * period_min   # every ~4th orbit
        windows.append((center - 5.0, center + 5.0))
    return windows


def ground_windows(n_stations: int = 3,
                   period_min: float = ORBIT_PERIOD_MIN):
    """Ground contacts: each station gives ~4 passes/day, 10 min each."""
    windows = []
    for s in range(n_stations):
        for k in range(4):
            center = (k * 4 + s * 1.3 + 0.7) * period_min
            windows.append((center - 5.0, center + 5.0))
    return sorted(windows)


def in_any_window(t_min: float, windows) -> bool:
    return any(a <= t_min < b for a, b in windows)


class Scheduler:
    """Rolling-horizon greedy scheduler with the module-09 rule set:

    1. data-locality first (task prefers satellite holding its model)
    2. downlink-window aware (big-output tasks -> satellite with soonest pass)
    3. thermal guard (T > 80 C -> no new tasks)
    4. SAA guard (no critical execution inside SAA windows)
    5. balance (prefer least-loaded satellite)
    """

    def __init__(self, satellites, downlink_rate_gbps: float = 1.0):
        self.sats = satellites
        self.saa = saa_windows()
        self.gs = ground_windows()
        self.downlink_rate_gbps = downlink_rate_gbps

    def _next_downlink_wait(self, t_min: float) -> float:
        for a, b in self.gs:
            if b >= t_min:
                return max(0.0, a - t_min)
        # wrap to next day
        return self.gs[0][0] + 1440.0 - t_min

    def _score(self, sat: Satellite, task: Task, t_min: float) -> float:
        if sat.temp_c > 80.0:
            return -1e9
        if sat.soc < 0.3:
            return -1e9
        load_penalty = len(sat.queue) * 30.0
        dl_wait = self._next_downlink_wait(t_min)
        out_penalty = task.data_out_gb * dl_wait / 100.0
        return -(load_penalty + out_penalty)

    def assign(self, task: Task, t_min: float) -> Satellite:
        best, best_score = None, -1e18
        for sat in self.sats:
            s = self._score(sat, task, t_min)
            if s > best_score:
                best, best_score = sat, s
        if best is None:
            return None
        task.assigned = best.name
        best.queue.append(task)
        return best

    def run_task(self, sat: Satellite, task: Task, t_min: float,
                 sim=None) -> float:
        """Execute: duration = compute/rate; SAA blocks critical work."""
        duration = task.tops_needed / sat.compute_tops * 60.0  # minutes
        t = t_min
        remaining = duration
        while remaining > 1e-6:
            if in_any_window(t, self.saa):
                # skip to end of SAA window (checkpoint & pause)
                end = min(b for a, b in self.saa if a <= t < b)
                t = end
                continue
            step = min(remaining, 5.0)
            t += step
            remaining -= step
            sat.temp_c += 0.3 * step          # heating while computing
            sat.battery_wh -= 0.9 * step / 60.0 * 1000.0 / 60.0
        task.done_min = t
        if task in sat.queue:
            sat.queue.remove(task)
        return t

    def downlink_volume_tb(self, t_start: float, t_end: float) -> float:
        """Total downlink capacity between two epochs (TB)."""
        vol = 0.0
        for a, b in self.gs:
            lo, hi = max(a, t_start), min(b, t_end)
            if hi > lo:
                vol += (hi - lo) * 60.0 * self.downlink_rate_gbps / 8.0 / 1000.0
        return vol


def make_constellation(n_sats: int = 3) -> list:
    """Suangxing-class satellites: 500 TOPS effective, 8 TB, 6 kWh."""
    return [
        Satellite(
            name=f"SX-{i+1}", compute_tops=500.0, storage_tb=8.0,
            battery_wh=6000.0, battery_capacity_wh=6000.0,
        )
        for i in range(n_sats)
    ]
