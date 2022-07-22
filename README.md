# 3d-render
Render 3D graphics in pygame or openGL

This project was heavily inspired by parts of the video series by javid9x [here](https://youtu.be/ih20l3pJoeU). While I didn't _completely_ copy his code, I figure it's safe for me to attribute it here [(part 1)](https://github.com/OneLoneCoder/videos/blob/master/OneLoneCoder_olcEngine3D_Part1.cpp) and here [(part 2)](https://github.com/OneLoneCoder/videos/blob/master/OneLoneCoder_olcEngine3D_Part2.cpp).

This was my first attempt to make a 3D graphics engine and I learned a lot while creating it, including
- A lot about how to use both `pygame` and `opengl` (through `moderngl_window`)
- The difference between "row major" and "column major" systems of doing matrix math (which was an endless source of frustration)
- How much of the inner-workings of 3D graphics rendering works, at least on a basic level

As it stands I don't think I'll update this project, but I'll certainly revisit it whenever I need to remember how some of this stuff works!

# Requirements
To run `with_pygame.py`, you need `pygame` and `numpy`:
```
pip install pygame numpy
```

To run `with_opengl.py`, you need `moderngl_window`, `pywavefront`, and `numpy`:
```
pip install moderngl_window pywavefront numpy
```
