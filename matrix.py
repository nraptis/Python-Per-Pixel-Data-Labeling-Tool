# matrix.py

import numpy as np
from math import cos, sin
from float_bufferable import FloatBufferable

class Matrix(FloatBufferable):
    def __init__(self):
        # Identity by default
        self.m = np.eye(4, dtype=np.float32)

    # ---------------------------------------------------------
    # FloatBufferable
    # ---------------------------------------------------------

    def write_to_buffer(self, buffer) -> None:
        for v in self.array():
            buffer.append(v)

    def size(self) -> int:
        return 16
    
    def array(self):
        return self.m.T.flatten().tolist()

    def reset(self):
        self.m = np.eye(4, dtype=np.float32)

    def make(
        self,
        m00, m01, m02, m03,
        m10, m11, m12, m13,
        m20, m21, m22, m23,
        m30, m31, m32, m33,
    ):
        self.m = np.array(
            [
                [m00, m01, m02, m03],
                [m10, m11, m12, m13],
                [m20, m21, m22, m23],
                [m30, m31, m32, m33],
            ],
            dtype=np.float32,
        )

    # ---------------------------------------------------------
    # Ortho (OpenGL-style, same math as First Man)
    # ---------------------------------------------------------

    def ortho(self, left: float, right: float, bottom: float,
              top: float, near_z: float, far_z: float) -> None:
        ral = right + left
        rsl = right - left
        tab = top + bottom
        tsb = top - bottom
        fan = far_z + near_z
        fsn = far_z - near_z

        self.make(
            2.0 / rsl, 0.0,        0.0,       0.0,
            0.0,       2.0 / tsb,  0.0,       0.0,
            0.0,       0.0,       -2.0 / fsn, 0.0,
            -ral / rsl, -tab / tsb, -fan / fsn, 1.0,
        )

    # ---------------------------------------------------------
    # Translation
    # ---------------------------------------------------------

    def translate(self, x: float, y: float, z: float) -> None:
        m = self.m

        tx = m[0, 0] * x + m[1, 0] * y + m[2, 0] * z + m[3, 0]
        ty = m[0, 1] * x + m[1, 1] * y + m[2, 1] * z + m[3, 1]
        tz = m[0, 2] * x + m[1, 2] * y + m[2, 2] * z + m[3, 2]

        m[3, 0] = tx
        m[3, 1] = ty
        m[3, 2] = tz

    def translation(self, x: float, y: float, z: float) -> None:
        self.make(
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            x,   y,   z,   1.0,
        )

    # ---------------------------------------------------------
    # Scaling
    # ---------------------------------------------------------

    def scale(self, scale_x: float, scale_y: float, scale_z: float) -> None:
        m = self.m

        sx = float(scale_x)
        sy = float(scale_y)
        sz = float(scale_z)

        # row 0 *= sx
        m[0, 0:4] *= sx
        # row 1 *= sy
        m[1, 0:4] *= sy
        # row 2 *= sz
        m[2, 0:4] *= sz

    # ---------------------------------------------------------
    # Rotations (set + multiply versions)
    # ---------------------------------------------------------

    def rotation_z(self, radians: float) -> None:
        _cos = cos(radians)
        _sin = sin(radians)
        self.make(
            _cos,  _sin,  0.0, 0.0,
            -_sin, _cos,  0.0, 0.0,
            0.0,   0.0,   1.0, 0.0,
            0.0,   0.0,   0.0, 1.0,
        )

    def rotate_z(self, radians: float) -> None:
        rotation_matrix = Matrix()
        rotation_matrix.rotation_z(radians)
        self.multiply(rotation_matrix)

    def rotation_y(self, radians: float) -> None:
        _cos = cos(radians)
        _sin = sin(radians)
        self.make(
            _cos, 0.0, -_sin, 0.0,
            0.0,  1.0, 0.0,   0.0,
            _sin, 0.0, _cos,  0.0,
            0.0,  0.0, 0.0,   1.0,
        )

    def rotate_y(self, radians: float) -> None:
        rotation_matrix = Matrix()
        rotation_matrix.rotation_y(radians)
        self.multiply(rotation_matrix)

    def rotation_x(self, radians: float) -> None:
        _cos = cos(radians)
        _sin = sin(radians)
        self.make(
            1.0, 0.0,  0.0, 0.0,
            0.0, _cos, _sin, 0.0,
            0.0, -_sin, _cos, 0.0,
            0.0, 0.0,  0.0, 1.0,
        )

    def rotate_x(self, radians: float) -> None:
        rotation_matrix = Matrix()
        rotation_matrix.rotation_x(radians)
        self.multiply(rotation_matrix)

    # ---------------------------------------------------------
    # Matrix multiply: self = self * right
    # ---------------------------------------------------------

    def multiply(self, right: "Matrix") -> None:
        """
        Multiply this matrix by `right` (self = self * right),
        matching the exact weird Kotlin formula.

        Kotlin pattern for m00Result, m10Result, ... corresponds to:

            res[i, j] = sum_k self.m[k, j] * right.m[i, k]

        i = row index, j = column index.

        This is *not* the standard A @ B row-major product, so we reimplement it
        explicitly in terms of the underlying NumPy arrays.
        """
        a = self.m
        b = right.m
        res = np.zeros((4, 4), dtype=np.float32)

        for j in range(4):      # column
            for i in range(4):  # row
                s = 0.0
                for k in range(4):
                    s += a[k, j] * b[i, k]
                res[i, j] = s

        self.m = res
