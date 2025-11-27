# uniforms_shape.py

from __future__ import annotations

from typing import Optional

from uniforms import UniformsFragment, UniformsVertex
from graphics_library import GraphicsLibrary
from shader_program import ShaderProgram
from matrix import Matrix

class UniformsShapeFragment(UniformsFragment):
    def __init__(
        self,
        r: float = 1.0,
        g: float = 1.0,
        b: float = 1.0,
        a: float = 1.0,
    ) -> None:
        self._r = float(r)
        self._g = float(g)
        self._b = float(b)
        self._a = float(a)

    # --- ColorConforming implementation ---

    @property
    def r(self) -> float:
        return self._r

    @r.setter
    def r(self, value: float) -> None:
        self._r = float(value)

    @property
    def g(self) -> float:
        return self._g

    @g.setter
    def g(self, value: float) -> None:
        self._g = float(value)

    @property
    def b(self) -> float:
        return self._b

    @b.setter
    def b(self, value: float) -> None:
        self._b = float(value)

    @property
    def a(self) -> float:
        return self._a

    @a.setter
    def a(self, value: float) -> None:
        self._a = float(value)

    def set_rgb(self, r: float, g: float, b: float) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = 1.0

    def set_rgba(self, r: float, g: float, b: float, a: float) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a

    def link(
        self,
        graphics: Optional[GraphicsLibrary],
        shader_program: Optional[ShaderProgram],
    ) -> None:
        if graphics is None or shader_program is None:
            return
        
        graphics.uniforms_modulate_color_set(
            shader_program,
            self.r,
            self.g,
            self.b,
            self.a,
        )

class UniformsShapeVertex(UniformsVertex):

    def __init__(
        self,
        projection_matrix: Optional[Matrix] = None,
        model_view_matrix: Optional[Matrix] = None,
    ) -> None:
        self._projection_matrix: Matrix = projection_matrix or Matrix()
        self._model_view_matrix: Matrix = model_view_matrix or Matrix()

    # --- UniformsVertex abstract properties ---

    @property
    def projection_matrix(self) -> Matrix:
        return self._projection_matrix

    @projection_matrix.setter
    def projection_matrix(self, value: Matrix) -> None:
        self._projection_matrix = value

    @property
    def model_view_matrix(self) -> Matrix:
        return self._model_view_matrix

    @model_view_matrix.setter
    def model_view_matrix(self, value: Matrix) -> None:
        self._model_view_matrix = value

    # --- Uniforms implementation ---
    def link(
        self,
        graphics: Optional[GraphicsLibrary],
        shader_program: Optional[ShaderProgram],
    ) -> None:
        if graphics is None or shader_program is None:
            return
        
        graphics.uniforms_projection_matrix_set(
            shader_program,
            self.projection_matrix,
        )
        graphics.uniforms_model_view_matrix_set(
            shader_program,
            self.model_view_matrix,
        )
