# main.py
import sys
import ctypes
from pathlib import Path

import glfw
import numpy as np
from OpenGL import GL as gl
from PIL import Image

from shader_program_shape_2d import ShaderProgramShape2D
from graphics_array_buffer import GraphicsArrayBuffer
from primitives import Shape2DVertex
from matrix import Matrix
from uniforms_shape import UniformsShapeVertex, UniformsShapeFragment
from graphics_library import GraphicsLibrary
from graphics_pipeline import GraphicsPipeline
from color import Color

# ----------------------------------------------------------------------
# Main: Hello Triangle using your stack
# ----------------------------------------------------------------------
def main():
    # --------------------------------------------------------------
    # Initialize GLFW and create a window / context
    # --------------------------------------------------------------
    if not glfw.init():
        print("Failed to initialize GLFW")
        sys.exit(1)
        
    # OpenGL 2.1-ish is fine for this; we just need a basic context.
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 2)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)

    width, height = 800, 600
    window = glfw.create_window(width, height, "Hello Shape2D (Your Stack)", None, None)
    if not window:
        glfw.terminate()
        print("Failed to create GLFW window")
        sys.exit(1)

    glfw.make_context_current(window)


    base_dir = Path(__file__).resolve().parent
    shader_path = base_dir / "shaders"
    pipeline = GraphicsPipeline(shader_path)


    # --- Create a VBO for the triangle positions ---
    positions = np.array([
        -0.5, -0.5,
         0.5, -0.5,
         0.5,  0.5,
    ], dtype=np.float32)

    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, positions.nbytes, positions, gl.GL_STATIC_DRAW)
    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    # --------------------------------------------------------------
    # Create your GraphicsLibrary (activity/renderer/pipeline/surface_view unused)
    # --------------------------------------------------------------
    graphics = GraphicsLibrary(
        activity=None,
        renderer=None,
        pipeline=None,
        surface_view=None,
        width=width,
        height=height,
    )

    # --------------------------------------------------------------
    # Build a simple triangle using Shape2DVertex + GraphicsArrayBuffer
    # --------------------------------------------------------------
    """
    vertices = [
        Shape2DVertex(x=100.0, y=100.0),
        Shape2DVertex(x=250.0,  y=120.0),
        Shape2DVertex(x=160.0,  y=300.0),
    ]
    """

    vertices = [
        Shape2DVertex(x=-0.75, y=-0.75),
        Shape2DVertex(x=0.5,  y=-0.5),
        Shape2DVertex(x=0.5,  y=0.5),
    ]

    vertex_buffer = GraphicsArrayBuffer[Shape2DVertex]()
    vertex_buffer.load(graphics, vertices)

    # Index buffer [0, 1, 2] for drawElements (uint32)
    indices = graphics.buffer_index_generate_from_list([0, 1, 2])

    # --------------------------------------------------------------
    # Set up uniforms via UniformsShapeVertex / UniformsShapeFragment
    # --------------------------------------------------------------
    # Simple identity matrices = clip-space already
    uniforms_vertex = UniformsShapeVertex(
        projection_matrix=Matrix(),  # identity by default
        model_view_matrix=Matrix(),  # identity by default
    )

    # Solid color (reddish)
    uniforms_fragment = UniformsShapeFragment(
        r=1.0,
        g=0.3,
        b=0.2,
        a=1.0,
    )
    
    print("GL VERSION:", gl.glGetString(gl.GL_VERSION))
    print("GLSL VERSION:", gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION))
    print("VENDOR:", gl.glGetString(gl.GL_VENDOR))

    err = gl.glGetError()
    if err != 0:
        print("*** GL ERROR:", hex(err))

    while not glfw.window_should_close(window):

        # RED background so we know frame is drawing
        gl.glClearColor(1.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        graphics.link_buffer_to_shader_program(
            pipeline.program_shape2d,
            vertex_buffer.buffer_index,
        )

        # Solid color (reddish) using Color object
        triangle_color = Color(1.0, 0.3, 0.2, 1.0)

        # Solid white color
        loc_color = pipeline.program_shape2d.uniform_location_modulate_color
        if loc_color != -1:
            gl.glUniform4f(loc_color, 1.0, 0.0, 1.0, 1.0)

        # Draw 3 vertices from the VBO
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        

        #gl.glDisableVertexAttribArray(loc_pos)
        graphics.unlink_buffer_from_shader_program(pipeline.program_shape2d)

        """
        projection = Matrix()
        projection.ortho(0.0, width, height, 0.0, 0.0, 1024.0)

        model_view = Matrix()
        model_view.translate(0.5, 0.5, 0.0)


        

        # Apply vertex + fragment uniforms via your Uniforms classes
        uniforms_vertex.link(graphics, pipeline.program_shape2d)
        uniforms_fragment.link(graphics, pipeline.program_shape2d)

        #graphics.uniforms_projection_matrix_set(pipeline.program_shape2d, projection)
        #graphics.uniforms_model_view_matrix_set(pipeline.program_shape2d, model_view)
        #graphics.uniforms_modulate_color_set(pipeline.program_shape2d, 1, 1, 1, 1)


        # Link buffer to shader program (sets up Positions attribute)
        graphics.link_buffer_to_shader_program(pipeline.program_shape2d, vertex_buffer.buffer_index)
        

        # Draw the triangle using your GraphicsLibrary helper
        graphics.draw_triangles(indices, 3)

        # Clean up attribute state
        graphics.unlink_buffer_from_shader_program(pipeline.program_shape2d)
        """

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
