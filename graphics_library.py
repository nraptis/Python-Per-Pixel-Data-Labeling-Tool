# graphics_library.py

from __future__ import annotations

from typing import Optional, Sequence, TypeVar

import numpy as np
from OpenGL import GL as gl

from float_bufferable import FloatBufferable
from graphics_array_buffer import GraphicsArrayBuffer
from graphics_texture import GraphicsTexture
from sprite import Sprite
from color import Color
from matrix import Matrix
from shader_program import ShaderProgram

T = TypeVar("T", bound=FloatBufferable)

class GraphicsLibrary:
    def __init__(
        self,
        activity,        # kept for signature parity, but unused here
        renderer,        # kept for parity; not used internally
        pipeline,        # kept for parity; not used here
        surface_view,    # kept for parity; not used here
        width: int,
        height: int,
    ) -> None:
        self.width: int = int(width)
        self.height: int = int(height)
        self.widthf: float = float(width)
        self.heightf: float = float(height)

        # we don't hold weakrefs here; not needed for Python version

        self.texture_set_filter_linear()
        self.texture_set_clamp()

    # ----------------------------------------------------------------------
    # VBO helpers (ARRAY_BUFFER)
    # ----------------------------------------------------------------------

    def buffer_array_generate(self) -> int:
        """Generate a GL_ARRAY_BUFFER VBO and return its id."""
        buf = gl.glGenBuffers(1)
        if isinstance(buf, (list, tuple)):
            return int(buf[0])
        return int(buf)

    def buffer_array_delete(self, index: int) -> None:
        """Delete a GL_ARRAY_BUFFER VBO."""
        if index != -1:
            gl.glDeleteBuffers(1, [int(index)])

    def buffer_array_write(self, index: int, data: Sequence[float]) -> None:
        if index == -1:
            return

        arr = np.asarray(data, dtype=np.float32)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, index)
        # PyOpenGL can infer size from 'arr'
        gl.glBufferData(gl.GL_ARRAY_BUFFER, arr, gl.GL_STATIC_DRAW)

    def buffer_array_bind(self, index: int) -> None:
        if index != -1:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, index)

    def buffer_array_bind_from_wrapper(
        self,
        graphics_array_buffer: Optional[GraphicsArrayBuffer[T]],
    ) -> None:
        if graphics_array_buffer is None:
            return

        if graphics_array_buffer.buffer_index != -1:
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, graphics_array_buffer.buffer_index)

    # ----------------------------------------------------------------------
    # Index buffers (client-side numpy arrays for glDrawElements)
    # ----------------------------------------------------------------------

    def buffer_index_generate_from_list(self, values: Sequence[int]) -> np.ndarray:
        return np.asarray(values, dtype=np.uint32)

    def buffer_index_write_from_list(
        self,
        values: Sequence[int],
        index_buffer: np.ndarray,
        count: Optional[int] = None,
    ) -> None:
        if count is None:
            count = len(values)
        count = min(count, len(values), index_buffer.size)
        index_buffer[:count] = np.asarray(values[:count], dtype=np.uint32)

    def buffer_index_generate_from_int_array(self, values: Sequence[int]) -> np.ndarray:
        return self.buffer_index_generate_from_list(values)

    # ----------------------------------------------------------------------
    # Float buffers (for FloatBufferable -> list[float])
    # ----------------------------------------------------------------------

    def buffer_float_size(self, items: Sequence[T]) -> int:
        if not items:
            return 0
        element_size = items[0].size()
        return len(items) * element_size

    def buffer_float_generate_from_item(self, item: T) -> list[float]:
        buf: list[float] = []
        item.write_to_buffer(buf)
        return buf

    def buffer_float_generate_from_array(self, items: Sequence[T]) -> list[float]:
        buf: list[float] = []
        self.buffer_float_write_from_list(items, buf)
        return buf

    def buffer_float_write_from_list(
        self,
        items: Sequence[T],
        float_buffer: list[float],
        count: Optional[int] = None,
    ) -> None:
        float_buffer.clear()
        if count is None:
            count = len(items)
        limit = min(count, len(items))

        for i in range(limit):
            items[i].write_to_buffer(float_buffer)

    def buffer_float_write_from_item(self, item: T, float_buffer: list[float]) -> None:
        float_buffer.clear()
        item.write_to_buffer(float_buffer)

    # ----------------------------------------------------------------------
    # Texture state & creation
    # ----------------------------------------------------------------------

    def texture_set_filter_mipmap(self) -> None:
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR_MIPMAP_LINEAR)

    def texture_set_filter_linear(self) -> None:
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)

    def texture_set_wrap_repeat(self) -> None:
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)

    def texture_set_clamp(self) -> None:
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    def texture_bind(self, texture: Optional[GraphicsTexture]) -> None:
        if texture is not None and texture.texture_index != -1:
            gl.glBindTexture(gl.GL_TEXTURE_2D, int(texture.texture_index))

    # --- variant that takes a "bitmap" (you decide what that is) ----------

    def texture_generate_from_bitmap(self, bitmap) -> int:
        if bitmap is None:
            return -1

        # Expecting numpy array (H, W, 4), dtype=uint8
        data = np.asarray(bitmap, dtype=np.uint8)
        if data.ndim != 3 or data.shape[2] != 4:
            raise ValueError("texture_generate_from_bitmap expects shape (H, W, 4) RGBA array")

        height, width, _ = data.shape

        tex = gl.glGenTextures(1)
        tex_id = int(tex[0] if isinstance(tex, (list, tuple)) else tex)
        if tex_id == 0:
            return -1

        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        self.texture_set_filter_linear()
        self.texture_set_clamp()

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA,
            width,
            height,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            data,
        )
        return tex_id

    # --- variant that creates a random RGBA texture -----------------------

    def texture_generate_random(self, width: int, height: int) -> int:
        width = int(width)
        height = int(height)

        tex = gl.glGenTextures(1)
        tex_id = int(tex[0] if isinstance(tex, (list, tuple)) else tex)
        if tex_id == 0:
            return -1

        gl.glBindTexture(gl.GL_TEXTURE_2D, tex_id)
        self.texture_set_filter_linear()
        self.texture_set_clamp()

        # random RGBA, each channel 0..255
        pixels = np.random.randint(0, 256, size=(height, width, 4), dtype=np.uint8)

        gl.glTexImage2D(
            gl.GL_TEXTURE_2D,
            0,
            gl.GL_RGBA,
            width,
            height,
            0,
            gl.GL_RGBA,
            gl.GL_UNSIGNED_BYTE,
            pixels,
        )
        return tex_id

    # ----------------------------------------------------------------------
    # Blending
    # ----------------------------------------------------------------------

    def blend_set_alpha(self) -> None:
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def blend_set_additive(self) -> None:
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)

    def blend_set_disabled(self) -> None:
        gl.glDisable(gl.GL_BLEND)

    # ----------------------------------------------------------------------
    # Draw helpers
    # ----------------------------------------------------------------------

    def draw_triangles(self, index_buffer: np.ndarray, count: int) -> None:
        gl.glDrawElements(
            gl.GL_TRIANGLES,
            int(count),
            gl.GL_UNSIGNED_INT,
            index_buffer,
        )

    def draw_triangle_strips(self, index_buffer: Optional[np.ndarray], count: int) -> None:
        if index_buffer is None:
            return
        gl.glDrawElements(
            gl.GL_TRIANGLE_STRIP,
            int(count),
            gl.GL_UNSIGNED_INT,
            index_buffer,
        )

    def draw_primitives(self, index_buffer: np.ndarray, primitive_type: int, count: int) -> None:
        gl.glDrawElements(
            int(primitive_type),
            int(count),
            gl.GL_UNSIGNED_INT,
            index_buffer,
        )

    # ----------------------------------------------------------------------
    # Linking buffers to shader program (vertex attribs)
    # ----------------------------------------------------------------------

    def link_buffer_to_shader_program_from_wrapper(
        self,
        program: Optional[ShaderProgram],
        buffer: Optional[GraphicsArrayBuffer[T]],
    ) -> None:
        if buffer is None:
            return
        self.link_buffer_to_shader_program(program, buffer.buffer_index)

    def link_buffer_to_shader_program(
        self,
        program: Optional[ShaderProgram],
        buffer_index: int,
    ) -> None:
        if program is None:
            print("BAD1")
            return
        if program.program == 0 or buffer_index == -1:
            print("BAD2")
            return

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer_index)
        gl.glUseProgram(program.program)

        # Position attribute
        if program.attribute_location_position != -1:
            gl.glEnableVertexAttribArray(program.attribute_location_position)
            gl.glVertexAttribPointer(
                program.attribute_location_position,
                program.attribute_size_position,
                gl.GL_FLOAT,
                False,
                program.attribute_stride_position,
                program.attribute_offset_position,
            )
            
        # Texture coordinates attribute
        if program.attribute_location_texture_coordinates != -1:
            gl.glEnableVertexAttribArray(program.attribute_location_texture_coordinates)
            gl.glVertexAttribPointer(
                program.attribute_location_texture_coordinates,
                program.attribute_size_texture_coordinates,
                gl.GL_FLOAT,
                False,
                program.attribute_stride_texture_coordinates,
                program.attribute_offset_texture_coordinates,
            )

    def unlink_buffer_from_shader_program(self, program: Optional[ShaderProgram]) -> None:
        if program is None or program.program == 0:
            return

        if program.attribute_location_texture_coordinates != -1:
            gl.glDisableVertexAttribArray(program.attribute_location_texture_coordinates)

        if program.attribute_location_position != -1:
            gl.glDisableVertexAttribArray(program.attribute_location_position)

    # ----------------------------------------------------------------------
    # Uniform helpers
    # ----------------------------------------------------------------------

    def uniforms_texture_size_set(self, program: Optional[ShaderProgram], width: float, height: float) -> None:
        if program is None:
            return
        if program.uniform_location_texture_size != -1:
            gl.glUniform2f(program.uniform_location_texture_size, float(width), float(height))

    # ModulateColor (from Color object)
    def uniforms_modulate_color_set_from_color(
        self,
        program: Optional[ShaderProgram],
        color: Color,
    ) -> None:
        if program is None:
            return
        loc = program.uniform_location_modulate_color
        if loc != -1:
            gl.glUniform4f(loc, color.r, color.g, color.b, color.a)

    # ModulateColor (explicit RGBA)
    def uniforms_modulate_color_set(
        self,
        program: Optional[ShaderProgram],
        r: float,
        g: float,
        b: float,
        a: float,
    ) -> None:
        if program is None:
            return
        loc = program.uniform_location_modulate_color
        if loc != -1:
            gl.glUniform4f(loc, float(r), float(g), float(b), float(a))

    # ProjectionMatrix from raw list/array
    def uniforms_projection_matrix_set_from_buffer(
        self,
        program: Optional[ShaderProgram],
        buffer_16_floats,
    ) -> None:
        if program is None:
            return
        loc = program.uniform_location_projection_matrix
        if loc == -1:
            return

        arr = np.asarray(buffer_16_floats, dtype=np.float32)
        if arr.size != 16:
            raise ValueError("Projection matrix buffer must contain 16 floats")
        gl.glUniformMatrix4fv(loc, 1, False, arr)

    # ProjectionMatrix from Matrix object
    def uniforms_projection_matrix_set(self, program: Optional[ShaderProgram], matrix: Optional[Matrix]) -> None:
        if program is None or matrix is None:
            return
        loc = program.uniform_location_projection_matrix
        if loc == -1:
            return

        arr = np.asarray(matrix.array(), dtype=np.float32)
        gl.glUniformMatrix4fv(loc, 1, False, arr)

    # ModelViewMatrix from raw buffer
    def uniforms_model_view_matrix_set_from_buffer(
        self,
        program: Optional[ShaderProgram],
        buffer_16_floats,
    ) -> None:
        if program is None:
            return
        loc = program.uniform_location_model_view_matrix
        if loc == -1:
            return

        arr = np.asarray(buffer_16_floats, dtype=np.float32)
        if arr.size != 16:
            raise ValueError("Model-view matrix buffer must contain 16 floats")
        gl.glUniformMatrix4fv(loc, 1, False, arr)

    # ModelViewMatrix from Matrix object
    def uniforms_model_view_matrix_set(self, program: Optional[ShaderProgram], matrix: Optional[Matrix]) -> None:
        if program is None or matrix is None:
            return
        loc = program.uniform_location_model_view_matrix
        if loc == -1:
            return

        arr = np.asarray(matrix.array(), dtype=np.float32)
        gl.glUniformMatrix4fv(loc, 1, False, arr)

    # Texture uniforms (sampler2D on unit 0)

    def uniforms_texture_set_from_texture(
        self,
        program: Optional[ShaderProgram],
        texture: Optional[GraphicsTexture],
    ) -> None:
        if program is None:
            return
        loc = program.uniform_location_texture
        if loc == -1 or texture is None or texture.texture_index == -1:
            return

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, int(texture.texture_index))
        gl.glUniform1i(loc, 0)

    def uniforms_texture_set_from_sprite(
        self,
        program: Optional[ShaderProgram],
        sprite: Optional[Sprite],
    ) -> None:
        if sprite is None:
            return
        self.uniforms_texture_set_from_texture(program, sprite.texture)

    def uniforms_texture_set_from_index(
        self,
        program: Optional[ShaderProgram],
        texture_index: int,
    ) -> None:
        if program is None:
            return
        loc = program.uniform_location_texture
        if loc == -1 or texture_index == -1:
            return

        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, int(texture_index))
        gl.glUniform1i(loc, 0)
