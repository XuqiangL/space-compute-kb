"""earth_texture.py - 地球纹理贴图：世界地图 → 3D 球面（随 GMST 在惯性系自转）。

教学目的：让用户在 J2000 惯性系中直接看到"地球转到哪了"——
本初子午线、各大洲相对春分点方向（X 轴）的方位一目了然。

原理（球面贴图的正交投影逆映射）：
  屏幕上每个像素 (dx, dy)（相对球心，半径 R_px 内）对应球面单位方向
      d = (dx·r̂ − dy·û + √(R²−dx²−dy²)·t̂) / R
  其中 (r̂, û, t̂) 为相机基矢量（右/上/指向相机），t̂ = −f̂。
  由 d 求惯性系经纬度：φ = asin(dz)，λ_inertial = atan2(dy, dx)
  纹理经度（地固）：λ_tex = λ_inertial − GMST(jd)   ← 地球自转就在这里
  等距圆柱纹理采样：u = (λ_tex+180°)/360°·W，v = (90°−φ)/180°·H

性能：numpy 向量化（约 5 ms/帧 @R=200px）+ 缓存（相机角/GMST/半径量化）。
纹理文件：earth_map.ppm（512×256 P6，NASA Blue Marble 衍生，见 README 署名）。
exe 打包时经 sys._MEIPASS 定位资源。
"""
import math
import os
import sys
import tkinter as tk

import numpy as np

from constants import gmst_rad

TEX_PATH = os.path.join(getattr(sys, "_MEIPASS",
                                os.path.dirname(os.path.abspath(__file__))),
                        "earth_map.ppm")


def load_texture(path=TEX_PATH):
    """读取 P6 PPM → (H, W, 3) uint8 数组；文件缺失返回 None（走蓝色球兜底）。"""
    try:
        with open(path, "rb") as f:
            data = f.read()
        # PPM 头：P6 <宽> <高> <最大灰度>\n（允许注释行 #...）
        parts, idx = [], 0
        while len(parts) < 4:
            # 跳过空白与注释
            while data[idx:idx + 1].isspace():
                idx += 1
            if data[idx:idx + 1] == b"#":
                while data[idx:idx + 1] != b"\n":
                    idx += 1
                continue
            start = idx
            while not data[idx:idx + 1].isspace():
                idx += 1
            parts.append(data[start:idx])
        idx += 1  # 头部后单个换行
        w, h = int(parts[1]), int(parts[2])
        arr = np.frombuffer(data[idx:idx + w * h * 3],
                            dtype=np.uint8).reshape(h, w, 3)
        return arr
    except (OSError, ValueError, IndexError):
        return None


class EarthTexture:
    """球面纹理渲染器（带缓存）。用法：img = et.render(cam, jd, R_px)。"""

    def __init__(self, tex=None):
        self.tex = tex if tex is not None else load_texture()
        self._cache_key = None
        self._cache_img = None     # tk.PhotoImage（由调用方持有防 GC）

    @property
    def available(self):
        return self.tex is not None

    def render_array(self, right, up, toward, gmst, R):
        """核心映射：相机基矢量 + GMST + 半径 → (2R, 2R, 3) uint8 颜色数组。

        right/up/toward：相机右/上/指向相机 的世界系单位矢量（3 元组）。
        圆盘外像素置透明标记色 (0,0,0)——调用方用 mask 处理。
        """
        tex = self.tex
        H, W = tex.shape[0], tex.shape[1]
        n = 2 * R
        # 屏幕圆盘归一化坐标（y 向下为正）
        gy, gx = np.mgrid[0:n, 0:n].astype(np.float64)
        dx = (gx - R + 0.5) / R
        dy = (gy - R + 0.5) / R
        r2 = dx * dx + dy * dy
        inside = r2 <= 1.0
        dz_c = np.sqrt(np.clip(1.0 - r2, 0.0, None))   # 朝相机方向的深度
        # 球面方向（世界惯性系）：d = dx·r̂ − dy·û + dz_c·t̂
        rx, ry, rz = right
        ux, uy, uz = up
        tx, ty, tz = toward
        wx = dx * rx - dy * ux + dz_c * tx
        wy = dx * ry - dy * uy + dz_c * ty
        wz = dx * rz - dy * uz + dz_c * tz
        # 惯性系经纬度 → 地固纹理经度（减 GMST，地球自转）
        lat = np.arcsin(np.clip(wz, -1.0, 1.0))
        lon = np.arctan2(wy, wx) - gmst
        u = ((np.degrees(lon) + 180.0) % 360.0) / 360.0 * W
        v = (90.0 - np.degrees(lat)) / 180.0 * H
        ui = np.clip(u.astype(np.int32), 0, W - 1)
        vi = np.clip(v.astype(np.int32), 0, H - 1)
        out = tex[vi, ui]                              # 最近邻采样
        # 简单朗伯明暗：cos(入射角)≈dz_c，压暗晨昏线附近增强立体感
        shade = (0.55 + 0.45 * dz_c)[..., None]
        out = np.clip(out.astype(np.float64) * shade, 0, 255).astype(np.uint8)
        out[~inside] = 0
        return out, inside

    @staticmethod
    def _to_ppm_bytes(arr):
        h, w = arr.shape[0], arr.shape[1]
        return b"P6\n%d %d\n255\n" % (w, h) + arr.tobytes()

    @staticmethod
    def _to_png_bytes(rgba):
        """最小 PNG 编码器（8-bit RGBA，滤波 0）：zlib(标准库) 压缩 + CRC。
        用 PNG 是因为 tkinter 只有 PNG/GIF 支持 alpha 透明通道。"""
        import struct
        import zlib
        h, w = rgba.shape[0], rgba.shape[1]
        raw = b"".join(b"\x00" + rgba[i].tobytes() for i in range(h))

        def chunk(tag, payload):
            return (struct.pack(">I", len(payload)) + tag + payload
                    + struct.pack(">I", zlib.crc32(tag + payload) & 0xffffffff))

        ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)  # 6=RGBA
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))

    def render_photo(self, cam, jd, R_px):
        """渲染为 tk.PhotoImage（带量化缓存：相机角 1°、GMST 0.5°、半径 2px）。

        圆盘外像素 alpha=0（透明，不遮挡轨道线）。返回 PhotoImage 或 None；
        返回值需调用方持有引用防 GC。
        """
        if self.tex is None or R_px < 6:
            return None
        R = int(R_px)
        key = (round(math.degrees(cam.az)), round(math.degrees(cam.el)),
               round(math.degrees(gmst_rad(jd)) * 2), round(R / 2))
        if key == self._cache_key and self._cache_img is not None:
            return self._cache_img
        # 相机基矢量：右 r̂、上 û、指向相机 t̂ = −f̂
        (cx, cy, cz), right, up, fwd = cam._basis()
        toward = (-fwd[0], -fwd[1], -fwd[2])
        arr, inside = self.render_array(right, up, toward, gmst_rad(jd), R)
        # 拼 alpha 通道：盘内 255 不透明，盘外 0 全透明
        alpha = np.where(inside, 255, 0).astype(np.uint8)[..., None]
        rgba = np.concatenate([arr, alpha], axis=2)
        img = tk.PhotoImage(data=self._to_png_bytes(rgba))
        self._cache_key = key
        self._cache_img = img
        return img
