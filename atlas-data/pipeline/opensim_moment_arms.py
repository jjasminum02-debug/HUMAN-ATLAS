"""Minimal OpenSim 4 (.osim) kinematics for muscle moment arms. Plain Python, no OpenSim install.

Supports what the bundled models use: CustomJoint (SpatialTransform with Constant / LinearFunction / SimmSpline),
PinJoint, UniversalJoint, WeldJoint, PhysicalOffsetFrame, PathPoint, ConditionalPathPoint and
CoordinateCouplerConstraint. Wrap objects are ignored (the path goes straight between its points), so moment arms of
muscles that wrap (e.g. gastrocnemius over the femoral condyles) are approximate; the sign is what build_actions uses.
Moment arm r = -dL/dq (m), central difference.
"""
from bisect import bisect_right
import math
import xml.etree.ElementTree as ET

STEP = math.radians(1)


def _floats(text): return [float(x) for x in (text or '').split()]


def _mat(r, t):
    return [[r[0][0], r[0][1], r[0][2], t[0]], [r[1][0], r[1][1], r[1][2], t[1]], [r[2][0], r[2][1], r[2][2], t[2]], [0, 0, 0, 1]]


def _mul(a, b): return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _inv(m):
    r = [[m[j][i] for j in range(3)] for i in range(3)]
    t = [-sum(r[i][k] * m[k][3] for k in range(3)) for i in range(3)]
    return _mat(r, t)


def _apply(m, p): return [sum(m[i][k] * p[k] for k in range(3)) + m[i][3] for i in range(3)]


def _axis_rot(axis, angle):
    n = math.sqrt(sum(a * a for a in axis)); x, y, z = (a / n for a in axis)
    c, s = math.cos(angle), math.sin(angle); C = 1 - c
    return [[c + x * x * C, x * y * C - z * s, x * z * C + y * s], [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
            [z * x * C - y * s, z * y * C + x * s, c + z * z * C]]


def _euler_xyz(a):
    """OpenSim orientation: body-fixed X-Y-Z."""
    r = _mat(_axis_rot([1, 0, 0], a[0]), [0, 0, 0])
    r = _mul(r, _mat(_axis_rot([0, 1, 0], a[1]), [0, 0, 0]))
    return _mul(r, _mat(_axis_rot([0, 0, 1], a[2]), [0, 0, 0]))


class _Function:
    def __init__(self, element):
        self.kind = element.tag
        if self.kind == 'Constant': self.value = float(element.findtext('value'))
        elif self.kind == 'LinearFunction': self.a, self.b = _floats(element.findtext('coefficients'))
        elif self.kind in ('SimmSpline', 'NaturalCubicSpline', 'PiecewiseLinearFunction'):
            self.x, self.y = _floats(element.findtext('x')), _floats(element.findtext('y'))
        else: raise ValueError(f'unsupported function {self.kind}')

    def __call__(self, q):
        if self.kind == 'Constant': return self.value
        if self.kind == 'LinearFunction': return self.a * q + self.b
        # Piecewise linear through the knots: enough for a sign and a mean moment arm.
        x, y = self.x, self.y
        if q <= x[0]: return y[0]
        if q >= x[-1]: return y[-1]
        i = bisect_right(x, q) - 1
        return y[i] + (y[i + 1] - y[i]) * (q - x[i]) / (x[i + 1] - x[i])


def _function_of(element):
    for child in element:
        if child.tag in ('Constant', 'LinearFunction', 'SimmSpline', 'NaturalCubicSpline', 'PiecewiseLinearFunction'):
            return _Function(child)
    return None


class Model:
    def __init__(self, path):
        root = ET.parse(path).getroot()
        self.frames = {}   # frame name -> (body path, offset matrix)
        self.joints = []   # (parent frame, child frame, kind, data)
        self.couplers = []
        for joint in root.iter():
            if not joint.tag.endswith('Joint') or joint.find('socket_parent_frame') is None: continue
            frames = {}
            for f in joint.iter('PhysicalOffsetFrame'):
                frames[f.get('name')] = (f.findtext('socket_parent').strip(),
                                         _mul(_mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]], _floats(f.findtext('translation'))), _euler_xyz(_floats(f.findtext('orientation')))))
            parent = self._frame(joint.findtext('socket_parent_frame').strip(), frames)
            child = self._frame(joint.findtext('socket_child_frame').strip(), frames)
            coords = [c.get('name') for c in joint.iter('Coordinate')]
            if joint.tag == 'CustomJoint':
                axes = []
                for t in joint.iter('TransformAxis'):
                    names = (t.findtext('coordinates') or '').split()
                    axes.append((t.get('name'), _floats(t.findtext('axis')), names[0] if names else None, _function_of(t)))
                data = axes
            else: data = coords
            self.joints.append((parent, child, joint.tag, data))
        for c in root.iter('CoordinateCouplerConstraint'):
            holder = c.find('coupled_coordinates_function')
            f = (_function_of(holder) if holder is not None and len(holder) else None) or _function_of(c)
            self.couplers.append(((c.findtext('independent_coordinate_names') or '').split()[0], c.findtext('dependent_coordinate_name').strip(), f))
        self.child_joint = {child[0]: j for j in self.joints for child in [j[1]]}
        self.paths = {}
        for muscle in root.iter():
            gp = muscle.find('GeometryPath')
            if gp is None or not muscle.get('name'): continue
            points = []
            for p in gp.find('PathPointSet').find('objects'):
                frame = p.findtext('socket_parent_frame').strip()
                cond = None
                if p.tag == 'ConditionalPathPoint':
                    cond = (p.findtext('socket_coordinate').strip().split('/')[-1], *_floats(p.findtext('range')))
                points.append((frame, _floats(p.findtext('location')), cond))
            self.paths[muscle.get('name')] = points

    @staticmethod
    def _frame(name, frames):
        if name in frames: return frames[name]
        return (name if name.startswith('/') else f'/bodyset/{name}', _mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0]))

    def _resolve(self, q):
        q = dict(q)
        for independent, dependent, f in self.couplers:
            q[dependent] = f(q.get(independent, 0)) if f else q.get(independent, 0)
        return q

    def _joint_motion(self, kind, data, q):
        identity = _mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0])
        if kind == 'WeldJoint': return identity
        if kind == 'PinJoint': return _mat(_axis_rot([0, 0, 1], q.get(data[0], 0)), [0, 0, 0])
        if kind == 'UniversalJoint':
            return _mul(_mat(_axis_rot([1, 0, 0], q.get(data[0], 0)), [0, 0, 0]), _mat(_axis_rot([0, 1, 0], q.get(data[1], 0)), [0, 0, 0]))
        rotation, translation = identity, [0, 0, 0]
        for name, axis, coord, f in data:
            value = f(q.get(coord, 0)) if f and coord else (f(0) if f else 0)
            if name.startswith('rotation'):
                if value: rotation = _mul(rotation, _mat(_axis_rot(axis, value), [0, 0, 0]))
            else:
                translation = [translation[i] + value * axis[i] for i in range(3)]
        return _mul(_mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]], translation), rotation)

    def body_transform(self, body, q, cache):
        if body in ('/ground', 'ground'): return _mat([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0, 0, 0])
        if body in cache: return cache[body]
        parent, child, kind, data = self.child_joint[body]
        x = _mul(_mul(self.body_transform(parent[0], q, cache), parent[1]), _mul(self._joint_motion(kind, data, q), _inv(child[1])))
        cache[body] = x
        return x

    def length(self, muscle, q):
        q = self._resolve(q); cache = {}; pts = []
        for frame, location, cond in self.paths[muscle]:
            if cond and not (cond[1] <= q.get(cond[0], 0) <= cond[2]): continue
            pts.append(_apply(self.body_transform(frame if frame.startswith('/') else f'/bodyset/{frame}', q, cache), location))
        return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))

    def moment_arm(self, muscle, coordinate, value, base=None):
        q = dict(base or {})
        up, down = dict(q, **{coordinate: value + STEP}), dict(q, **{coordinate: value - STEP})
        return -(self.length(muscle, up) - self.length(muscle, down)) / (2 * STEP)
