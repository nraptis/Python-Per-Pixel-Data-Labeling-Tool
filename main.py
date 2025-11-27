# main.py
import sys
import ctypes
from pathlib import Path

import glfw
import numpy as np
from OpenGL import GL as gl
from PIL import Image

from graphics_pipeline import GraphicsPipeline


# ----------------------------------------------------------------------
# Main: Textured triangle using vanilla OpenGL + your sprite_2d shaders
# ----------------------------------------------------------------------
def main():
    # --------------------------------------------------------------
    # Initialize GLFW and create a window / context
    # --------------------------------------------------------------
    if not glfw.init():
        print("Failed to initialize GLFW")
        sys.exit(1)

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
    image_path = base_dir / "images/image.png"

    # --------------------------------------------------------------
    # Load shaders via your pipeline (we'll use sprite_2d only)
    # --------------------------------------------------------------
    pipeline = GraphicsPipeline(shader_path)
    sprite_prog = pipeline.program_sprite2d

    print("sprite_2d attrib/uni locations:")
    print("  position =", sprite_prog.attribute_location_position)
    print("  texcoord =", sprite_prog.attribute_location_texture_coordinates)
    print("  Texture  =", sprite_prog.uniform_location_texture)
    print("  ModColor =", sprite_prog.uniform_location_modulate_color)

    # --------------------------------------------------------------
    # Vanilla texture loading with PIL + PyOpenGL
    # --------------------------------------------------------------
    image = Image.open(image_path).convert("RGBA")
    tex_width, tex_height = image.size
    print(f"Loaded image: {tex_width} x {tex_height}")

    image_data = np.array(image, dtype=np.uint8)
    print("Image data shape:", image_data.shape, "dtype:", image_data.dtype)

    tex = gl.glGenTextures(1)
    if isinstance(tex, (list, tuple, np.ndarray)):
        tex = int(tex[0])
    else:
        tex = int(tex)

    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)

    gl.glTexImage2D(
        gl.GL_TEXTURE_2D,
        0,
        gl.GL_RGBA,
        tex_width,
        tex_height,
        0,
        gl.GL_RGBA,
        gl.GL_UNSIGNED_BYTE,
        image_data,
    )

    print("Created GL texture id:", tex)

    # --------------------------------------------------------------
    # Create a VBO with interleaved position (x,y) + uv (u,v)
    # --------------------------------------------------------------
    # Positions in clip-space, UVs in [0,1]
    # v is flipped so that v=0 is top of image (common for PNGs)
    vertices = np.array([
        #   x,     y,    u,   v
        -0.8, -0.8,   0.0, 1.0,   # bottom-left
         0.8, -0.8,   1.0, 1.0,   # bottom-right
         0.0,  0.8,   0.5, 0.0,   # top-center
    ], dtype=np.float32)

    vbo = gl.glGenBuffers(1)
    if isinstance(vbo, (list, tuple, np.ndarray)):
        vbo = int(vbo[0])
    else:
        vbo = int(vbo)

    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, gl.GL_STATIC_DRAW)

    gl.glDisable(gl.GL_DEPTH_TEST)
    gl.glDisable(gl.GL_CULL_FACE)

    print("GL VERSION:", gl.glGetString(gl.GL_VERSION))
    print("GLSL VERSION:", gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION))
    print("VENDOR:", gl.glGetString(gl.GL_VENDOR))

    # --------------------------------------------------------------
    # Main loop
    # --------------------------------------------------------------
    while not glfw.window_should_close(window):

        gl.glClearColor(1.0, 0.0, 0.0, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # Use sprite_2d program
        gl.glUseProgram(sprite_prog.program)

        # Bind VBO
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)

        stride = 4 * 4  # 4 floats per vertex (x,y,u,v) * 4 bytes

        # Position attribute
        loc_pos = sprite_prog.attribute_location_position
        if loc_pos != -1:
            gl.glEnableVertexAttribArray(loc_pos)
            gl.glVertexAttribPointer(
                loc_pos,
                2,                      # vec2
                gl.GL_FLOAT,
                False,
                stride,
                ctypes.c_void_p(0),     # offset 0
            )

        # Texcoord attribute
        loc_uv = sprite_prog.attribute_location_texture_coordinates
        if loc_uv != -1:
            gl.glEnableVertexAttribArray(loc_uv)
            gl.glVertexAttribPointer(
                loc_uv,
                2,                      # vec2
                gl.GL_FLOAT,
                False,
                stride,
                ctypes.c_void_p(8),     # 2 floats * 4 bytes
            )

        # Bind texture to unit 0 and set sampler uniform
        gl.glActiveTexture(gl.GL_TEXTURE0)
        gl.glBindTexture(gl.GL_TEXTURE_2D, tex)

        loc_tex = sprite_prog.uniform_location_texture
        if loc_tex != -1:
            gl.glUniform1i(loc_tex, 0)

        # ModulateColor = white (no tint)
        loc_color = sprite_prog.uniform_location_modulate_color
        if loc_color != -1:
            gl.glUniform4f(loc_color, 1.0, 1.0, 1.0, 1.0)

        # Draw triangle
        gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)

        # Disable attribs
        if loc_uv != -1:
            gl.glDisableVertexAttribArray(loc_uv)
        if loc_pos != -1:
            gl.glDisableVertexAttribArray(loc_pos)

        glfw.swap_buffers(window)
        glfw.poll_events()

    # Cleanup
    gl.glDeleteTextures([tex])
    gl.glDeleteBuffers(1, [vbo])
    glfw.terminate()


if __name__ == "__main__":
    main()
