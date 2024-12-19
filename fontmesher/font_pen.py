import numpy as np
from fontTools.pens.basePen import BasePen


class FontPen(BasePen):
    """
    A pen class for handling font geometry operations.

    The input is the geometry object from gmsh,
    and parameters for font size control & normalization.

    A call to the draw method on a glyph will draw it on the geometry object.

    Attributes:
        geo: The geometry object to which points and curves are added.
        min_val (float): The minimum value for normalizing points.
        max_val (float): The maximum value for normalizing points.
        glyph_size (float): The size of the glyph for normalization.
        lc (float): The characteristic length for mesh generation.
        start_point (tuple): The starting point of the current path.
        points (list): A list of points in the current path.
        curves (list): A list of curves in the current path.
        curve_loops (list): A list of curve loops created.
        p_start: The starting point object in the geometry.
    Methods:
        _normalize_point(pt):
            Normalize the point to the range [0, self.glyph_size].
        _is_same_point(p1, p2):
            Check if two points are approximately the same.
        _moveTo(pt):
            Move to the specified point, starting a new sub-path.
        _lineTo(pt):
            Draw a line to the specified point.
        qCurveTo(*points):
            Draw a quadratic Bézier curve to the specified points.
        _closePath():
            Close the current path, creating a curve loop.
        _endPath():
            End the current path.
    """
    def __init__(self, geo, min_val=-1, max_val=1, glyph_size=1, lc=0.02, z=0):
        self.start_point = None
        self.path_start_idx = 0
        self.points = []
        self.curves = []
        self.curve_loops = []
        self.p_start = None

        self.min_val = min_val
        self.max_val = max_val
        self.glyph_size = glyph_size
        self.lc = lc
        self.z = z

        self.geo = geo

    def _clear_all(self):
        self.start_point = None
        self.points = []
        self.curves = []
        self.curve_loops = []
        self.p_start = None

    def _normalize_point(self, pt):
        """
        normalize the point to the range [0, self.glyph_size]
        prerequisites: self.min_val, self.max_val is setup correctly
        """
        scale_factor = 1 / self.glyph_size
        return (
            (pt[0] - self.min_val) / ((self.max_val - self.min_val) * scale_factor),  # noqa
            (pt[1] - self.min_val) / ((self.max_val - self.min_val) * scale_factor),  # noqa
        )

    def _is_same_point(self, p1, p2):
        return np.allclose(p1, p2)

    def _moveTo(self, pt):
        pt = self._normalize_point(pt)
        p = self.geo.addPoint(pt[0], pt[1], self.z, self.lc)
        self.p_start = p
        self.points.append(p)
        self.start_point = pt

    def _lineTo(self, pt):
        pt = self._normalize_point(pt)
        prev_p = self.points[-1]
        if self._is_same_point(pt, self.start_point):
            p = self.p_start
        else:
            p = self.geo.addPoint(pt[0], pt[1], self.z, self.lc)
        self.points.append(p)
        curve = self.geo.addLine(prev_p, p)
        self.curves.append(curve)

    def qCurveTo(self, *points):
        curve_points = [self.points[-1]]
        for i in range(len(points)):
            pt = self._normalize_point(points[i])
            if self._is_same_point(pt, self.start_point):
                p = self.p_start
            else:
                p = self.geo.addPoint(pt[0], pt[1], self.z, self.lc)
            curve_points.append(p)
        self.points.append(curve_points[-1])
        curve = self.geo.addBezier(curve_points)
        self.curves.append(curve)

    def _closePath(self):
        # check is path integrity - if not, close the path
        if self.points[self.path_start_idx] != self.points[-1]:
            end_point = self.points[-1]
            start_point = self.points[self.path_start_idx]
            curve = self.geo.addLine(end_point, start_point)
            self.curves.append(curve)
        curve_loop = self.geo.addCurveLoop(self.curves)
        self.curve_loops.append(curve_loop)
        # gmsh.model.geo.addPlaneSurface([curve_loop])
        self.path_start_idx = len(self.points)

    def _endPath(self):
        self.value.append(("endPath",))
