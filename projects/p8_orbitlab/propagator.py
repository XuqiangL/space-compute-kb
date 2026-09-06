# -*- coding: utf-8 -*-
"""
propagator.py — OrbitLab 数值传播器（Cowell 方法 + 经典 RK4）
=============================================================

方法：Cowell 方法——直接积分直角坐标状态 y = [x,y,z,vx,vy,vz]，
  ODE 右手边 dy/dt = [v, a_total(r,v,jd)]，a_total 由
  perturbations.total_accel 给出（中心引力 + 勾选摄动）。
  对应 GMAT 数值传播器语义（Propagator/ODEModel 数据流：
  传播器把状态交给力模型，力模型返回 6 维导数）。

积分器：经典 4 阶 Runge-Kutta，定步长；step(dt_s) 内部把 dt_s 切成
  ≤10 s 子步。为什么 10 s：LEO 轨道周期 ~90 min ≈ 5400 s，10 s 子步
  即每圈 ~540 步，RK4 局部截断误差 O(h^5) 已远低于教学显示精度，
  同时 33 ms 动画帧下计算量可忽略。

单位：km / km/s / s；历元 jd 为浮点儒略日（UTC）。
零依赖：math + constants + perturbations。
"""

from perturbations import total_accel

SUBSTEP_MAX_S = 10.0     # RK4 子步上限 [s]（LEO 周期 ~90 min → ~540 子步/圈）


def rk4_step(f, t, y, h):
    """经典 4 阶 Runge-Kutta 单步：y(t+h) 的 4 阶近似。

    公式（f(t,y) = dy/dt 为 ODE 右手边）：
      k1 = f(t, y)
      k2 = f(t + h/2, y + (h/2)·k1)
      k3 = f(t + h/2, y + (h/2)·k2)
      k4 = f(t + h,   y + h·k3)
      y_new = y + (h/6)·(k1 + 2·k2 + 2·k3 + k4)
    局部截断误差 O(h^5)，全局累积 O(h^4)。
    """
    n = len(y)
    k1 = f(t, y)
    k2 = f(t + 0.5 * h, [y[i] + 0.5 * h * k1[i] for i in range(n)])
    k3 = f(t + 0.5 * h, [y[i] + 0.5 * h * k2[i] for i in range(n)])
    k4 = f(t + h, [y[i] + h * k3[i] for i in range(n)])
    return [y[i] + h * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]) / 6.0
            for i in range(n)]


class Propagator:
    """Cowell 数值传播器：状态 state[6] = [r(3), v(3)]，历元 jd。"""

    def __init__(self, cfg):
        """cfg：perturbations.PerturbConfig（摄动开关与参数）。"""
        self.cfg = cfg
        self.state = [0.0] * 6   # [x,y,z,vx,vy,vz]，km / km/s
        self.jd = 0.0            # 当前历元（儒略日）

    def reset(self, r3, v3, jd):
        """设初值：r3 [km]、v3 [km/s]、jd 历元（儒略日）。"""
        self.state = [r3[0], r3[1], r3[2], v3[0], v3[1], v3[2]]
        self.jd = jd

    def _rhs(self, t, y):
        """ODE 右手边 dy/dt = [v, a_total]；t 为相对 reset 历元的秒数。

        力模型历元 = self.jd + t/86400（秒 → 儒略日）。
        """
        r = y[0:3]
        v = y[3:6]
        a = total_accel(r, v, self.jd + t / 86400.0, self.cfg)
        return [v[0], v[1], v[2], a[0], a[1], a[2]]

    def step(self, dt_s):
        """推进 dt_s 秒：内部切成 ≤10 s 子步逐段 RK4（保证 LEO 数值稳定）。"""
        n = max(1, int(abs(dt_s) / SUBSTEP_MAX_S + 0.999999))  # 向上取整
        h = dt_s / n
        t = 0.0
        y = self.state
        for _ in range(n):
            y = rk4_step(self._rhs, t, y, h)
            t += h
        self.state = y
        self.jd += dt_s / 86400.0
