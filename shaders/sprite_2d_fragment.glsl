// sprite_2d_fragment.glsl

#ifdef GL_ES
precision mediump float;
#endif

uniform vec4 ModulateColor;
varying vec2 TextureCoordinatesOut;
uniform sampler2D Texture;

void main(void) {
    gl_FragColor = ModulateColor * texture2D(Texture, TextureCoordinatesOut);
}
