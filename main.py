# main.py
import sys
import ctypes
from pathlib import Path
from random import random

import glfw
import numpy as np
from OpenGL import GL as gl
from PIL import Image

from graphics_pipeline import GraphicsPipeline
from graphics_library import GraphicsLibrary
from primitives import Sprite2DVertex
from graphics_array_buffer import GraphicsArrayBuffer
from graphics_texture import GraphicsTexture
from graphics_sprite import GraphicsSprite

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

    width, height = 1280, 960
    window = glfw.create_window(width, height, "Hello Shape2D (Your Stack)", None, None)
    if not window:
        print("Failed to create GLFW window")
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)

    base_dir = Path(__file__).resolve().parent
    shader_path = base_dir / "shaders"
    image_path = base_dir / "images/image.png"

    pipeline = GraphicsPipeline(shader_path)
    graphics = GraphicsLibrary(width=width, height=height)
    
    texture = GraphicsTexture(graphics=graphics, file_name=image_path)
    texture.print()

    sprite = GraphicsSprite()
    sprite.load(graphics=graphics, texture=texture)
    sprite.print()

    sprite_prog = pipeline.program_sprite2d

    sprite_vertices = [
        Sprite2DVertex(x=-0.9, y=-0.9, u=0.0, v=1.0),
        Sprite2DVertex(x=0.9,  y=-0.9, u=1.0, v=1.0),
        Sprite2DVertex(x=0.0, y=0.9, u=0.5, v=0.0)
    ]

    sprite_vertex_buffer = GraphicsArrayBuffer[Sprite2DVertex]()
    sprite_vertex_buffer.load(graphics, sprite_vertices)

    sprite_indices = [0, 1, 2]
    sprite_index_buffer = graphics.buffer_index_generate_from_int_array(sprite_indices)

    print("sprite_2d attrib/uni locations:")
    print("  position =", sprite_prog.attribute_location_position)
    print("  texcoord =", sprite_prog.attribute_location_texture_coordinates)
    print("  Texture  =", sprite_prog.uniform_location_texture)
    print("  ModColor =", sprite_prog.uniform_location_modulate_color)

    print("GL VERSION:", gl.glGetString(gl.GL_VERSION))
    print("GLSL VERSION:", gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION))
    print("VENDOR:", gl.glGetString(gl.GL_VENDOR))

    # --------------------------------------------------------------
    # Main loop
    # --------------------------------------------------------------
    while not glfw.window_should_close(window):

        graphics.clear_rgb(0.22, 0.22, 0.28)
        graphics.link_buffer_to_shader_program_array_buffer(sprite_prog, sprite_vertex_buffer)
        graphics.blend_set_alpha()
        graphics.uniforms_texture_set_sprite(program=sprite_prog, sprite=sprite)
        graphics.uniforms_modulate_color_set(sprite_prog, r=1.0, g=1.0, b=0.5, a=0.5)
        graphics.draw_primitives(index_buffer=sprite_index_buffer, primitive_type=gl.GL_TRIANGLES, count=3)
        graphics.unlink_buffer_from_shader_program(sprite_prog)

        glfw.swap_buffers(window)
        glfw.poll_events()

    # Cleanup
    #gl.glDeleteTextures([tex])

    glfw.terminate()


if __name__ == "__main__":
    main()
