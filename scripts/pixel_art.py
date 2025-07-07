import sys
import math
import pygame
from PIL import Image, ImageOps
import numpy as np

# --- Configurable parameters ---
IMAGE_PATHS = [
    "C:/Users/SHAMBHAVI/Desktop/shantanu_files/code_projects/random_projects/pixelart/photo.jpeg"
]
BG_COLOR = (156, 204, 101)
SQUARE_COLOR = (0, 0, 0)
GRID_SIZE = 170
PIXEL_SIZE = 1
DITHER_THRESHOLD = 60
ROTATION_SPEED = 1  # Set this >0 for animation

def floyd_steinberg_dither(img, threshold=127):
    arr = np.array(img, dtype=np.float32)
    h, w = arr.shape
    out = np.zeros_like(arr)
    for y in range(h):
        for x in range(w):
            old = arr[y, x]
            new = 0 if old < threshold else 255
            out[y, x] = new
            quant_error = old - new
            if x+1 < w:
                arr[y, x+1] += quant_error * 7/16
            if y+1 < h and x > 0:
                arr[y+1, x-1] += quant_error * 3/16
            if y+1 < h:
                arr[y+1, x] += quant_error * 5/16
            if y+1 < h and x+1 < w:
                arr[y+1, x+1] += quant_error * 1/16
    return (out < threshold).astype(np.uint8)

def load_and_dither_image(path, size, threshold=DITHER_THRESHOLD):
    image = Image.open(path)
    image = ImageOps.grayscale(image)
    image = image.resize((size, size), Image.LANCZOS)
    dithered = floyd_steinberg_dither(image, threshold)
    return dithered

def draw_rotated_grid_3d(screen, grid, angle_deg, pixel_size, bg_color, square_color, offset=(0,0)):
    """
    Visual illusion: rotates the grid around the Y-axis with perspective, 
    so it looks like a 3D card flip, but is still just the dithered 2D grid.
    """
    h, w = grid.shape
    cx, cy = w // 2, h // 2
    angle_rad = math.radians(angle_deg)
    screen.fill(bg_color)

    # Perspective and camera settings
    perspective = 450  # Higher = less perspective
    viewer_distance = 2.5 * w  # Controls how close the camera is

    for y in range(h):
        for x in range(w):
            if grid[y, x]:
                # Center grid at (0,0,0)
                rel_x = x - cx
                rel_y = y - cy
                rel_z = 0

                # Y-axis rotation (side-to-side)
                rot_x = rel_x * math.cos(angle_rad) + rel_z * math.sin(angle_rad)
                rot_z = -rel_x * math.sin(angle_rad) + rel_z * math.cos(angle_rad)
                rot_y = rel_y

                # Perspective projection
                z = rot_z + viewer_distance
                if z == 0: z = 0.01  # Avoid division by zero
                proj_x = int(rot_x * perspective / z + screen.get_width() // 2 + offset[0])
                proj_y = int(rot_y * perspective / z + screen.get_height() // 2 + offset[1])

                s = max(1, int(pixel_size * perspective / z))
                pygame.draw.rect(
                    screen,
                    square_color,
                    (proj_x, proj_y, s, s)
                )

def main():
    pygame.init()
    image_idx = 0
    threshold = DITHER_THRESHOLD

    # Preload dithered images
    grids = [load_and_dither_image(path, GRID_SIZE, threshold) for path in IMAGE_PATHS]
    grid = grids[image_idx]

    win_size = (GRID_SIZE * PIXEL_SIZE, GRID_SIZE * PIXEL_SIZE)
    screen = pygame.display.set_mode(win_size)
    pygame.display.set_caption("Dithered Grid Visual Illusion (3D Y-rotation)")

    clock = pygame.time.Clock()
    running = True
    angle = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    image_idx = (image_idx + 1) % len(IMAGE_PATHS)
                    grid = load_and_dither_image(IMAGE_PATHS[image_idx], GRID_SIZE, threshold)
                if event.key == pygame.K_UP:
                    threshold = min(255, threshold + 8)
                    grid = load_and_dither_image(IMAGE_PATHS[image_idx], GRID_SIZE, threshold)
                if event.key == pygame.K_DOWN:
                    threshold = max(0, threshold - 8)
                    grid = load_and_dither_image(IMAGE_PATHS[image_idx], GRID_SIZE, threshold)

        draw_rotated_grid_3d(screen, grid, angle, PIXEL_SIZE, BG_COLOR, SQUARE_COLOR)
        pygame.display.flip()
        angle = (angle + ROTATION_SPEED) % 360
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()