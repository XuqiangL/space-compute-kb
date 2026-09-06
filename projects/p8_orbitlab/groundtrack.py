"""groundtrack.py - OrbitLab 星下点轨迹模块：惯性系位置 → 地理经纬度 + 轨迹图。

教学意义：星下点轨迹 = 轨道面（惯性系中近似固定）与自转地球的相对运动，
可直观看到轨道倾角（轨迹纬度范围 ±i）、交点西退（J2 摄动）等现象。
"""
import math
import tkinter as tk

from constants import RE_EARTH, gmst_rad   # 单一数据源：GMAT 常量与时间系统


def inertial_to_latlon(r3, jd):
    """惯性系位置 → 星下点地理经纬度 + 高度。

    公式：地固经度 λ = atan2(y, x) − GMST（归一化到 −180°~180°）
          地心纬度 φ = asin(z/|r|)
          高度     h = |r| − RE_EARTH
    返回 (lat_deg, lon_deg, alt_km)。
    """
    x, y, z = r3
    r = math.sqrt(x * x + y * y + z * z)
    lat = math.degrees(math.asin(z / r))
    lon = math.degrees(math.atan2(y, x)) - math.degrees(gmst_rad(jd))
    lon = (lon + 180.0) % 360.0 - 180.0
    return lat, lon, r - RE_EARTH


class GroundTrackCanvas(tk.Canvas):
    """星下点轨迹图：等距圆柱投影网格 + 红色轨迹 + 黄色当前点（带闪光圈）。"""

    W, H = 280, 150

    def __init__(self, parent, **kw):
        super().__init__(parent, width=self.W, height=self.H,
                         bg='#2b2b2b', highlightthickness=0, **kw)
        self._current = None      # 当前星下点 (lat, lon)
        self._blinking = False    # 闪光圈动画是否在跑
        self._pulse_on = False
        self._blink_r = 6
        self._map_img = None      # 世界地图背景（PhotoImage，需持有引用）
        self._load_map_background()
        self.draw_base()

    def _load_map_background(self):
        """把同一份世界地图纹理（earth_map.ppm）缩放为画布大小的背景图。

        等距圆柱投影的纹理与星下点图投影方式相同，直接逐像素重采样即可。
        失败（纹理缺失）则保持纯色背景，仅画网格。
        """
        try:
            import numpy as np
            from earth_texture import load_texture, EarthTexture
            tex = load_texture()
            if tex is None:
                return
            th, tw = tex.shape[0], tex.shape[1]
            # 目标 (H, W) 网格 → 源纹理最近邻重采样
            gy, gx = np.mgrid[0:self.H, 0:self.W]
            si = np.clip((gy + 0.5) / self.H * th, 0, th - 1).astype(np.int32)
            sj = np.clip((gx + 0.5) / self.W * tw, 0, tw - 1).astype(np.int32)
            small = tex[si, sj]
            # 压暗 40%：让红色轨迹线在地图上更醒目
            small = (small.astype(np.float64) * 0.6).astype(np.uint8)
            self._map_img = tk.PhotoImage(
                data=EarthTexture._to_ppm_bytes(small))
            self.create_image(0, 0, image=self._map_img, anchor='nw',
                              tags='base')
        except Exception:
            self._map_img = None

    def _proj(self, lat, lon):
        """等距圆柱投影：x = (λ+180)/360·W，y = (90−φ)/180·H。"""
        return ((lon + 180.0) / 360.0 * self.W,
                (90.0 - lat) / 180.0 * self.H)

    def draw_base(self):
        """经纬网格：经度每 60°、纬度每 30°，赤道加亮，附经纬标签。"""
        self.delete('base')
        for lon in range(-180, 181, 60):
            x, _ = self._proj(0, lon)
            self.create_line(x, 0, x, self.H, fill='#444444', tags='base')
            self.create_text(x, self.H - 8, text='%d°' % lon, fill='#888888',
                             font=('', 7), tags='base')
        for lat in range(-90, 91, 30):
            _, y = self._proj(lat, 0)
            eq = (lat == 0)
            self.create_line(0, y, self.W, y,
                             fill='#777777' if eq else '#444444',
                             width=2 if eq else 1, tags='base')   # 赤道加亮
            self.create_text(12, y, text='%d°' % lat, fill='#888888',
                             font=('', 7), tags='base')

    def set_track(self, points, current):
        """points = [(lat, lon), ...] 轨迹；current = (lat, lon) 当前星下点或 None。

        ±180° 经度跳变断线：相邻点经度差 >180° 说明轨迹穿过图幅东西边界，
        若不断开会拉出一条横贯全图的假线。
        """
        self.delete('track')
        seg = []
        prev_lon = None
        for lat, lon in points:
            if prev_lon is not None and abs(lon - prev_lon) > 180.0:
                if len(seg) >= 4:
                    self.create_line(*seg, fill='#ff4444', width=1, tags='track')
                seg = []
            x, y = self._proj(lat, lon)
            seg.append(x)
            seg.append(y)
            prev_lon = lon
        if len(seg) >= 4:
            self.create_line(*seg, fill='#ff4444', width=1, tags='track')
        self._current = current
        self._pulse_on = current is not None
        if current is not None:
            x, y = self._proj(*current)
            self.create_oval(x - 3, y - 3, x + 3, y + 3,
                             fill='#ffee00', outline='', tags='track')
            self._draw_ring(x, y, self._blink_r)
            if not self._blinking:
                self._blinking = True
                self.after(500, self._blink)

    def _draw_ring(self, x, y, r):
        """当前点外围的闪光圈（tag 'ring' 便于单独重绘）。"""
        self.delete('ring')
        self.create_oval(x - r, y - r, x + r, y + r,
                         outline='#ffee00', tags=('track', 'ring'))

    def _blink(self):
        """闪光圈呼吸动画：半径 6↔10 往返，直到当前点清空或画布销毁。"""
        if not self._pulse_on or self._current is None:
            self._blinking = False
            return
        try:
            self._blink_r = 10 if self._blink_r == 6 else 6
            x, y = self._proj(*self._current)
            self._draw_ring(x, y, self._blink_r)
            self.after(500, self._blink)
        except tk.TclError:
            self._blinking = False   # 画布已销毁
