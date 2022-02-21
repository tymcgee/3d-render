# Tynan McGee
# 9/1/2021
# 3d engine using opengl

# resources:
# help with GLSL operations:
# https://en.wikibooks.org/wiki/GLSL_Programming/Vector_and_Matrix_Operations
# help with 3D projection in openGL:
# https://learnopengl.com/Getting-started/Coordinate-Systems
# help with normals in regard to lighting:
# https://learnopengl.com/Lighting/Basic-Lighting
# help getting started with moderngl-window:
# https://moderngl-window.readthedocs.io/en/latest/guide/basic_usage.html?highlight=self.load_scene#resource-loading
# help getting started with moderngl:
# https://moderngl.readthedocs.io/en/stable/the_guide/index.html
# moderngl examples:
# https://github.com/moderngl/moderngl/tree/master/examples/#readme
# opengl implementation of perspective projection matrix:
# https://www.khronos.org/registry/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
# opengl implementation of lookat matrix:
# https://www.geertarien.com/blog/2017/07/30/breakdown-of-the-lookAt-function-in-OpenGL/


import moderngl_window as mglw
import numpy as np
import moderngl
import os

def normalize(vec):
    """ normalizes vector. """
    norm = np.linalg.norm(vec)
    if norm != 0:
        return vec / norm
    raise ValueError("divided by zero when normalizing a vector.")

def make_projection(fov, aspect, znear, zfar):
    """ creates perspective projection matrix and returns it. """
    fov = np.radians(fov)
    f = 1 / np.tan(fov * 0.5)
    q = znear - zfar
    return np.array([
        [f / aspect, 0,                      0,  0],
        [         0, f,                      0,  0],
        [         0, 0,     (zfar + znear) / q, -1],
        [         0, 0, (2 * zfar * znear) / q,  0]
    ], dtype='f4')

def make_lookat(eye, target, up):
    """ creates lookat matrix and returns it. """
    eye = np.array(eye)
    target = np.array(target)
    up = np.array(up)
    zaxis = normalize(target - eye)
    xaxis = normalize(np.cross(zaxis, up))
    yaxis = np.cross(xaxis, zaxis)
    zaxis = -zaxis

    return np.array([
        [           xaxis[0],            yaxis[0],            zaxis[0], 0],
        [           xaxis[1],            yaxis[1],            zaxis[1], 0],
        [           xaxis[2],            yaxis[2],            zaxis[2], 0],
        [-np.dot(xaxis, eye), -np.dot(yaxis, eye), -np.dot(zaxis, eye), 1]
    ], dtype='f4')

def make_xrot(ang):
    """ creates rotation matrix about the x axis and returns it. """
    return np.array([
        [1,           0,            0, 0],
        [0, np.cos(ang), -np.sin(ang), 0],
        [0, np.sin(ang),  np.cos(ang), 0],
        [0,           0,            0, 1]
    ], dtype='f4')

def make_zrot(ang):
    """ creates rotation matrix about the z axis and returns it. """
    return np.array([
        [np.cos(ang), -np.sin(ang), 0, 0],
        [np.sin(ang),  np.cos(ang), 0, 0],
        [           0,           0, 1, 0],
        [           0,           0, 0, 1]
    ], dtype='f4')


class View(mglw.WindowConfig):
    gl_version = (3, 3)
    window_size = (700, 500)
    title = "3D Graphics Engine"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # initialization here
        slash = '\\'
        if os.name == "posix":
            slash = '/'
        print('available object files:')
        for o in os.listdir('objects'):
            if o.endswith('.obj'):
                print(o)
        filename = os.getcwd() + slash + "objects" + slash + input("choose obj filename (without .obj): ") + ".obj"
        self.obj = self.load_scene(filename)
        self.theta = 0
        
        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform mat4 proj;
            uniform mat4 model; // rotations but not view or projection

            in vec3 in_position;
            in vec3 in_normal;

            out vec3 v_norm;

            void main() {
                v_norm = vec3(model * vec4(in_normal, 1.0));
                gl_Position = proj * vec4(in_position, 1.0);
            }
            """,
            fragment_shader="""
            #version 330

            in vec3 v_norm;

            out vec4 f_color;

            vec3 light_dir = vec3(0, 0, 1);

            void main() {
                float dp = dot(normalize(v_norm), normalize(light_dir));
                dp = max(dp, 0.0);
                f_color = vec4(dp, dp, dp, 1.0);
            }
            """
        )
        self.proj = self.prog['proj']
        self.model = self.prog['model']

        self.proj_mat = make_projection(60.0, self.aspect_ratio, 0.1, 1000)
        self.vao = self.obj.root_nodes[0].mesh.vao.instance(self.prog)

        self.distance = 4
        self.rotation_amount = 0.01

        self.proj.write(self.proj_mat)
        
    def render(self, time, frametime):
        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.lookat_mat = make_lookat(
            (0, 0, self.distance),
            (0, 0, 0),
            (0, 1, 0)
        )

        x_rot = make_xrot(self.theta / 2)
        z_rot = make_zrot(self.theta)
        rotation_transform = z_rot @ x_rot

        self.model.write(rotation_transform)
        self.proj.write(rotation_transform @ self.lookat_mat @ self.proj_mat)

        self.theta += self.rotation_amount 
        self.vao.render()


    def key_event(self, key, action, modifiers):
        # key presses
        if action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.RIGHT:
                self.rotation_amount += 0.005
            elif key == self.wnd.keys.LEFT:
                self.rotation_amount = max(0.0, self.rotation_amount - 0.005)
            elif key == self.wnd.keys.UP:
                self.distance -= 0.5
            elif key == self.wnd.keys.DOWN:
                self.distance += 0.5

        elif action == self.wnd.keys.ACTION_RELEASE:
            pass


if __name__ == '__main__':
    View.run()
