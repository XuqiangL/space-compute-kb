"""render3d.py - minimal 3D camera + perspective projection (no deps).

World frame: heliocentric ecliptic J2000 (x->vernal equinox, z->north).
Camera: spherical coords around a target point; perspective projection.
"""
import math


class Camera:
    def __init__(self):
        self.az = math.radians(-90.0)     # azimuth
        self.el = math.radians(35.0)      # elevation
        self.dist = 60.0                  # AU from target
        self.target = [0.0, 0.0, 0.0]     # look-at (AU)
        self.f = 900.0                    # focal scale (px * AU^{-0})

    def _basis(self):
        ca, sa = math.cos(self.az), math.sin(self.az)
        ce, se = math.cos(self.el), math.sin(self.el)
        # camera position on sphere around target
        cx = self.target[0] + self.dist * ce * ca
        cy = self.target[1] + self.dist * ce * sa
        cz = self.target[2] + self.dist * se
        # forward (from camera to target)
        fx, fy, fz = (self.target[0] - cx, self.target[1] - cy,
                      self.target[2] - cz)
        fn = math.sqrt(fx * fx + fy * fy + fz * fz)
        fx, fy, fz = fx / fn, fy / fn, fz / fn
        # right = forward x world_up(0,0,1) (fallback if degenerate)
        rx, ry, rz = fy * 1.0 - fz * 0.0, fz * 0.0 - fx * 1.0, 0.0
        rn = math.sqrt(rx * rx + ry * ry + rz * rz)
        if rn < 1e-9:
            rx, ry, rz = 1.0, 0.0, 0.0
            rn = 1.0
        rx, ry, rz = rx / rn, ry / rn, rz / rn
        # up = right x forward
        ux = ry * fz - rz * fy
        uy = rz * fx - rx * fz
        uz = rx * fy - ry * fx
        return (cx, cy, cz), (rx, ry, rz), (ux, uy, uz), (fx, fy, fz)

    def project(self, p, w, h):
        """World point -> (sx, sy, depth) or None if behind camera."""
        (cx, cy, cz), (rx, ry, rz), (ux, uy, uz), (fx, fy, fz) = self._basis()
        dx, dy, dz = p[0] - cx, p[1] - cy, p[2] - cz
        zc = dx * fx + dy * fy + dz * fz
        if zc <= 1e-6:
            return None
        xc = dx * rx + dy * ry + dz * rz
        yc = dx * ux + dy * uy + dz * uz
        sx = w * 0.5 + self.f * xc / zc
        sy = h * 0.5 - self.f * yc / zc
        return sx, sy, zc

    def rotate(self, daz_deg, del_deg):
        self.az += math.radians(daz_deg)
        self.el = max(math.radians(-89.0),
                      min(math.radians(89.0), self.el + math.radians(del_deg)))

    def zoom(self, factor):
        self.dist = max(0.02, min(300.0, self.dist * factor))

    def pan(self, dx_px, dy_px, w, h):
        (cx, cy, cz), (rx, ry, rz), (ux, uy, uz), _ = self._basis()
        scale = self.dist / self.f
        self.target[0] += (-dx_px * scale) * rx + (dy_px * scale) * ux
        self.target[1] += (-dx_px * scale) * ry + (dy_px * scale) * uy
        self.target[2] += (-dx_px * scale) * rz + (dy_px * scale) * uz
