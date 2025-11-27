# uniforms.py

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from graphics_library import GraphicsLibrary
from shader_program import ShaderProgram
from matrix import Matrix
from primitives import ColorConforming

class Uniforms(ABC):
    @abstractmethod
    def link(
        self,
        graphics: Optional[GraphicsLibrary],
        shader_program: Optional[ShaderProgram],
    ) -> None:
        pass

class UniformsVertex(Uniforms, ABC):
    @property
    @abstractmethod
    def projection_matrix(self) -> Matrix:
        ...

    @projection_matrix.setter
    @abstractmethod
    def projection_matrix(self, value: Matrix) -> None:
        pass

    @property
    @abstractmethod
    def model_view_matrix(self) -> Matrix:
        pass

    @model_view_matrix.setter
    @abstractmethod
    def model_view_matrix(self, value: Matrix) -> None:
        pass


class UniformsFragment(Uniforms, ColorConforming, ABC):
    pass

