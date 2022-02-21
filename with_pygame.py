# Tynan McGee
# 8/16/2021

import pygame
import numpy as np
import sys
import os
from vector import *

def create_triangle_list(filename):
    """ using filename (which is a .obj file), construct triangles from
        vertices and return the list of triangle objects. """
    with open(filename, 'r') as f:
        verts = []  # list of temporary vertices
        tris = []  # final list of triangle objects
        for line in f:
            ln = line.strip()
            splt = ln.split(' ')
            if splt[0] == 'v':  # vertex
                verts.append(vec3d(float(splt[1]), float(splt[2]), float(splt[3])))
            elif splt[0] == 'f':  # face
                # splt[1-3] is made up of vertex indices from verts
                # we do splt[1][0] in case the object file contains normal data
                # then splt[1] looks like "5//1" and we only need the 5
                splt[1] = splt[1].split('//')
                splt[2] = splt[2].split('//')
                splt[3] = splt[3].split('//')
                p1 = verts[int(splt[1][0]) - 1]
                p2 = verts[int(splt[2][0]) - 1]
                p3 = verts[int(splt[3][0]) - 1]
                tris.append(tri(p1, p2, p3))
    return tris

def avg_z(triangle):
    """ finds average z value of triangle and returns it. """
    return (triangle.p1.z + triangle.p2.z + triangle.p3.z) / 3


if __name__ == "__main__":
    slash = '\\'
    if os.name == "posix":
        slash = '/'
    print('available object files:')
    for o in os.listdir('objects'):
        if o.endswith('.obj'):
            print(o)
    triangles = create_triangle_list("objects" + slash + input("Choose object filename (without .obj): ") + ".obj")
    SIZE = WIDTH, HEIGHT = 1920, 1080
    pygame.init()
    SCREEN = pygame.display.set_mode(SIZE)
    CLOCK = pygame.time.Clock()
    FONT = pygame.font.SysFont("Arial", 24)
    ROTATE = True
    pygame.display.set_caption("3D Engine")
    theta = 0
    to_rotate = 0.02  # num of radians to rotate by each frame
    zoom = 10
    camera = vec3d(0, 0, 0)

    ### make projection matrix
    projection_mat = make_projection(np.pi/2, HEIGHT / WIDTH, 0.1, 1000)

    while True:
        ### PYGAME EVENT HANDLING ###
        #############################
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.TEXTINPUT:
                ROTATE = not ROTATE
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_RIGHT:
                    to_rotate += 0.005
                elif event.key == pygame.K_LEFT:
                    to_rotate -= 0.005
                    to_rotate = max(to_rotate, 0.0)
                elif event.key == pygame.K_UP:
                    zoom -= 0.5
                elif event.key == pygame.K_DOWN:
                    zoom += 0.5
        #############################################


        SCREEN.fill('black')
        z_rot_mat = make_rot_z(theta)
        x_rot_mat = make_rot_x(theta * 0.5)
        translate_mat = make_translation(0, 0, zoom)
        # z rotation, then x rotation
        transform_mat = mat_mul(x_rot_mat, z_rot_mat)  # z rotation, then x rotation
        # then translate into screen
        transform_mat = mat_mul(translate_mat, transform_mat)

        triangles_to_draw = []
        for t in triangles:
            tri_transformed = transform(t, transform_mat)

            # use normal vectors of triangles to determine
            # whether we can see them or not
            line1 = vec_sub(tri_transformed.p2, tri_transformed.p1)
            line2 = vec_sub(tri_transformed.p3, tri_transformed.p1)

            # line1 cross line2 to get the normal vector.
            # orientation of triangles matter, points are in
            # clockwise order
            normal = cross_product(line1, line2)
            normal = normalize(normal)

            # only do the projection and rasterization if we can "see"
            # the triangle. this is done via the dot product of
            # the normal and the line from the "camera" to the triangle.
            sim = dot_product(normal, vec_sub(tri_transformed.p1, camera))

            if sim < 0:
                # illumination
                light_dir = vec3d(0, 0, -1)
                light_dir = normalize(light_dir)
                dp = dot_product(normal, light_dir)
                # choose grayscale color based on dot product
                n = max(int(np.floor(255 * dp)), 0)
                col = (n, n, n)

                # project triangles from 3D to 2D
                tri_projected = transform(tri_transformed, projection_mat)
                # scale the triangles into view using the z component which was
                # stored in w
                tri_projected.p1 = vec_div(tri_projected.p1, tri_projected.p1.w)
                tri_projected.p2 = vec_div(tri_projected.p2, tri_projected.p2.w)
                tri_projected.p3 = vec_div(tri_projected.p3, tri_projected.p3.w)

                # projection matrix gives results between -1 and 1.
                # scale into view by adding 1 to each component so 
                # their range is between 0 and 2 and then scale
                # it up based on the aspect ratio.
                # this moves it out of the corner and into the center,
                # and scales it up.
                final_translation = vec3d(1, 1, 0)
                tri_projected.p1 = vec_add(tri_projected.p1, final_translation)
                tri_projected.p2 = vec_add(tri_projected.p2, final_translation)
                tri_projected.p3 = vec_add(tri_projected.p3, final_translation)
                tri_projected.p1.x *= 0.5 * WIDTH
                tri_projected.p1.y *= 0.5 * HEIGHT
                tri_projected.p2.x *= 0.5 * WIDTH
                tri_projected.p2.y *= 0.5 * HEIGHT
                tri_projected.p3.x *= 0.5 * WIDTH
                tri_projected.p3.y *= 0.5 * HEIGHT

                # put completed 2d triangle into list
                tri_projected.color = col
                triangles_to_draw.append(tri_projected)

        # sort the triangles from back to front so they don't draw over each other
        triangles_to_draw.sort(reverse=True, key=avg_z)

        # draw the triangles now
        for t in triangles_to_draw:
            pts = [[t.p1.x, t.p1.y], [t.p2.x, t.p2.y], [t.p3.x, t.p3.y]]
            pygame.draw.polygon(SCREEN, t.color, pts, 0)
            ## draw wireframe vv
            # pygame.draw.polygon(SCREEN, 'white', pts, 3)
            ## draw wireframe ^^

        if ROTATE:
            theta += to_rotate
        CLOCK.tick(120)
        fps = CLOCK.get_fps()
        SCREEN.blit(FONT.render("fps: " + str(fps),1, 'white'), (10,0))
        SCREEN.blit(FONT.render("(esc to exit, space to pause, R/L keys to speed/slow rotation, U/D keys to inc/dec zoom)", 1, 'white'), (10, 30))
        SCREEN.blit(FONT.render("current rotation speed: " + str(to_rotate) + " radians per frame", 1, 'white'), (10, 60))
        SCREEN.blit(FONT.render("current rotation angle: " + str(theta) + " radians", 1, 'white'), (10, 90))
        SCREEN.blit(FONT.render("current zoom: " + str(1 / zoom), 1, 'white'), (10, 120))
        pygame.event.pump()
        pygame.display.update()
