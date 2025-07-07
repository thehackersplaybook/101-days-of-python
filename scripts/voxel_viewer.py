import trimesh
import numpy as np
import moderngl
import moderngl_window as mglw
from pyrr import Matrix44
import sys
from datetime import datetime

class VoxelViewer(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "ModernGL Voxel Viewer"
    window_size = (400, 400)
    aspect_ratio = None
    resizable = True
    resource_dir = '.'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Hardcoded OBJ file path
        obj_path = r"C:\Users\SHAMBHAVI\Desktop\shantanu_files\code_projects\random_projects\pixelart\shareModel.obj"

        try:
            mesh = trimesh.load(obj_path)
        except Exception as e:
            print(f"❌ Failed to load OBJ file: {e}")
            sys.exit(1)

        # --- Debug: Print mesh bounds ---
        print(f"Mesh bounds: {mesh.bounds}")

        # --- Scale mesh if too small ---
        mesh.apply_scale(10.0)  # Scale 10x to ensure sufficient voxelization

        voxelized = mesh.voxelized(pitch=0.025)  # Higher resolution
        self.voxels = voxelized.points.astype('f4')

        # --- Debug: Print voxel count and bounds ---
        print(f"✅ Loaded {len(self.voxels)} voxels")
        print(f"Voxel bounds: {np.ptp(self.voxels, axis=0)}")

        # --- Warn if voxel count is high ---
        if len(self.voxels) > 100000:
            print(f"⚠️ Warning: {len(self.voxels)} voxels may impact performance!")

        # --- Center and scale voxel cloud ---
        self.voxels -= self.voxels.mean(axis=0)  # Center it
        self.voxels *= 2.0  # Scale up

        # --- Generate per-voxel colors (uniform color #0f1b0e) ---
        self.voxel_color = np.array([12/255, 21/255, 11/255], dtype='f4')  # RGB for #0f1b0e

        # --- Upload to GPU ---
        self.vbo = self.ctx.buffer(self.voxels.tobytes())
        self.color_vbo = self.ctx.buffer(np.tile(self.voxel_color, (len(self.voxels), 1)).tobytes())

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                uniform mat4 mvp;
                in vec3 in_position;
                in vec3 in_color;
                out vec3 v_color;
                void main() {
                    gl_Position = mvp * vec4(in_position, 1.0);
                    gl_PointSize = 6.0;
                    v_color = in_color;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_color;
                out vec4 fragColor;
                void main() {
                    fragColor = vec4(v_color, 1.0);
                }
            '''
        )

        self.vao = self.ctx.vertex_array(
            self.prog,
            [(self.vbo, '3f', 'in_position'), (self.color_vbo, '3f', 'in_color')]
        )

        # --- Dynamic camera positioning ---
        bounds = np.ptp(self.voxels, axis=0)
        max_extent = np.max(bounds)
        self.camera_pos = np.array([0.0, 0.0, max(-max_extent * 2.0, -10.0)])

        # --- Camera and rotation setup ---
        self.projection = Matrix44.perspective_projection(
            45.0, self.wnd.aspect_ratio or (self.window_size[0] / self.window_size[1]), 0.1, 1000.0
        )
        self.rotation = Matrix44.identity()
        self.angle = 0.0  # For continuous rotation

    def on_render(self, time: float, frame_time: float):
        self.ctx.clear(149/255, 193/255, 115/255)  # Background color #95c173
        self.ctx.enable(moderngl.DEPTH_TEST)

        # --- Continuous rotation ---
        self.angle += 0.02  # Adjust speed as needed
        model = Matrix44.from_y_rotation(self.angle) * self.rotation
        view = Matrix44.from_translation(self.camera_pos)
        mvp = self.projection * view * model

        self.prog['mvp'].write(mvp.astype('f4').tobytes())
        self.vao.render(mode=moderngl.POINTS)

    def resize(self, width: int, height: int):
        """Update projection matrix on window resize."""
        self.projection = Matrix44.perspective_projection(
            45.0, width / height, 0.1, 1000.0
        )

    def mouse_drag_event(self, x, y, dx, dy):
        """Rotate the model based on mouse drag."""
        rx = Matrix44.from_x_rotation(dy * 0.01)
        ry = Matrix44.from_y_rotation(dx * 0.01)
        self.rotation = rx * ry * self.rotation

    def key_event(self, key, action, modifiers):
        """Zoom in/out with W/S keys."""
        if action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.W:
                self.camera_pos[2] += 5.0
            elif key == self.wnd.keys.S:
                self.camera_pos[2] -= 5.0

    def on_key_press(self, key, modifiers):
        """Start recording video on 'R' key press."""
        if key == self.wnd.keys.R:
            self.wnd.start_recording(
                filename=f"spinning_voxel_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                fps=30,
                duration=10.0  # Record for 10 seconds
            )
            print(f"Started recording to spinning_voxel_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

    def on_key_release(self, key, modifiers):
        """Stop recording on 'R' key release (optional)."""
        if key == self.wnd.keys.R:
            self.wnd.stop_recording()
            print("Stopped recording")

if __name__ == '__main__':
    mglw.run_window_config(VoxelViewer)