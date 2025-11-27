// shape_2d_vertex.glsl
attribute vec2 Positions;

void main(void) {
    gl_Position = vec4(Positions, 0.0, 1.0);
}
