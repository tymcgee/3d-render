import numpy as np

class vec3d:
    def __init__(self, x=0, y=0, z=0, w=1):
        self.x = x
        self.y = y
        self.z = z
        self.w = w  # required for multiplication w/ 4x4 matrices
    
    
class tri:
    def __init__(self, p1=vec3d(), p2=vec3d(), p3=vec3d()):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.color = None


def vec_mat_mul(v, m):
    """ v is 4d, m is 4x4. returns new 4d vector. """
    result = vec3d()
    result.x = v.x*m[0][0] + v.y*m[0][1] + v.z*m[0][2] + v.w*m[0][3]
    result.y = v.x*m[1][0] + v.y*m[1][1] + v.z*m[1][2] + v.w*m[1][3]
    result.z = v.x*m[2][0] + v.y*m[2][1] + v.z*m[2][2] + v.w*m[2][3]
    result.w = v.x*m[3][0] + v.y*m[3][1] + v.z*m[3][2] + v.w*m[3][3]
    return result

def mat_mul(m1, m2):
    """ multiplies (4x4) m1 by m2 (m1 * m2, in that order). returns
        resulting 4x4 matrix. """
    # empty 4x4 matrix
    result = [[0 for _ in range(4)] for _ in range(4)]
    for row in range(4):
        for col in range(4):
            result[row][col] = m1[row][0]*m2[0][col] + m1[row][1]*m2[1][col] + m1[row][2]*m2[2][col] + m1[row][3]*m2[3][col]
    return result

def transform(triangle, matrix):
    """ transforms each point in triangle using the given transformation
        matrix. """
    result = tri()
    result.p1 = vec_mat_mul(triangle.p1, matrix)
    result.p2 = vec_mat_mul(triangle.p2, matrix)
    result.p3 = vec_mat_mul(triangle.p3, matrix)
    return result

def make_rot_x(ang):
    """ makes the 4d x-rotation matrix using angle ang and returns it. """
    return [
        [1,           0,            0, 0],
        [0, np.cos(ang), -np.sin(ang), 0],
        [0, np.sin(ang),  np.cos(ang), 0],
        [0,           0,            0, 1]
    ]

def make_rot_y(ang):
    """ makes the 4d y-rotation matrix using angle ang and returns it. """
    return [
        [ np.cos(ang), 0, np.sin(ang), 0],
        [           0, 1,           0, 0],
        [-np.sin(ang), 0, np.cos(ang), 0],
        [           0, 0,           0, 1]
    ]

def make_rot_z(ang):
    """ makes the 4d z-rotation matrix using angle ang and returns it. """
    return [
        [np.cos(ang), -np.sin(ang), 0, 0],
        [np.sin(ang),  np.cos(ang), 0, 0],
        [           0,           0, 1, 0],
        [           0,           0, 0, 1]
    ]

def make_translation(a, b, c):
    """ makes a translation matrix which adds a to x, b to y, c to z.
        only works if w component of vector is 1 (i think). """
    return [
        [1, 0, 0, a],
        [0, 1, 0, b],
        [0, 0, 1, c],
        [0, 0, 0, 1]
    ]

def make_projection(fov, aspect, z_near, z_far):
    """ makes projection matrix for projecting 3d vectors into 2d. 
        
        multiplying a 3d vector (with w component = 1) by this matrix
        will result in its projection into 2d coords. the resulting
        vector after multiplication should look like
        >>[a*f*x, f*y, z*q, n*q, z]

        where a=aspect ratio, f=fov, q=z_far / (z_far - z_near)
        and n=z_near.

        after multiplying a vector by this matrix, divide each component by
        z (which is the fourth component of the resulting vector).
        then the first two components are new (x,y) coords in 2d.
        third component has to do with the original z coord in 3d
        and the fourth component should just be 1 (after normalization by z).
        
        essentially the x component is scaled by the aspect ratio and the fov,
        the y component is scaled by the fov, and the z component is scaled by
        something to do with the depth of the screen/how far you want to see.
        then each component is divided by z to give it perspective. """
    fov = 1 / np.tan(fov / 2)
    q = z_far / (z_far - z_near)
    return [
        [aspect * fov,   0, 0,           0],
        [           0, fov, 0,           0],
        [           0,   0, q, -z_near * q],
        [           0,   0, 1,           0]
    ]




def vec_add(v1, v2):
    """ add two 3d vectors and return resulting vector. """
    return vec3d(v1.x + v2.x, v1.y + v2.y, v1.z + v2.z)

def vec_sub(v1, v2):
    """ subtract two 3d vectors and return resulting vector. """
    return vec3d(v1.x - v2.x, v1.y - v2.y, v1.z - v2.z)

def vec_mul(v1, k):
    """ multiply 3d vector by k and return resulting vector. """
    return vec3d(v1.x*k, v1.y*k, v1.z*k)

def vec_div(v1, k):
    """ divide 3d vector by k and return resulting vector. """
    return vec3d(v1.x/k, v1.y/k, v1.z/k)

def dot_product(v1, v2):
    """ return dot product of two 3d vectors. """
    return v1.x*v2.x + v1.y*v2.y + v1.z*v2.z

def cross_product(v1, v2):
    """ return cross product of two 3d vectors. """
    result = vec3d()
    result.x = v1.y*v2.z - v1.z*v2.y
    result.y = v1.z*v2.x - v1.x*v2.z
    result.z = v1.x*v2.y - v1.y*v2.x
    return result

def normalize(v):
    """ normalizes vector and returns resulting vector which points
        in the same direction but has magnitude 1. """
    result = vec3d()
    norm_len = np.sqrt(dot_product(v, v))
    result.x = v.x / norm_len
    result.y = v.y / norm_len
    result.z = v.z / norm_len
    return result
