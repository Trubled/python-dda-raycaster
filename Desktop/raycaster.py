import pygame
import math
import numpy as np

# Initialize Pygame 
pygame.init()
WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Neural Raycaster Engine - Optimized")
clock = pygame.time.Clock()

# Lock and hide the mouse for look controls
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# 1. Expanded 16x16 World Map (0 = Empty, 1-4 = Different Wall Types)
world_map = np.array([
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 2, 2, 0, 3, 3, 3, 0, 4, 0, 1, 0, 2, 0, 1],
    [1, 0, 2, 0, 0, 0, 0, 3, 0, 4, 0, 1, 0, 2, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 1],
    [1, 0, 3, 3, 0, 1, 0, 0, 0, 4, 4, 4, 0, 3, 3, 1],
    [1, 0, 3, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 3, 0, 1],
    [1, 0, 0, 0, 0, 0, 1, 0, 0, 2, 2, 2, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1, 0, 0, 2, 0, 2, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 1],
    [1, 0, 4, 4, 4, 0, 1, 1, 1, 0, 0, 0, 1, 4, 0, 1],
    [1, 0, 4, 0, 0, 0, 1, 0, 0, 0, 3, 0, 1, 4, 0, 1],
    [1, 0, 4, 0, 2, 0, 1, 0, 0, 0, 3, 0, 1, 4, 4, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
])

# Player Position and Camera Vectors
pos_x, pos_y = 3.5, 3.5
dir_x, dir_y = -1.0, 0.0
plane_x, plane_y = 0.0, 0.66

# Define Wall Colors based on map ID (RGB)
wall_colors = {
    1: np.array([200, 50, 50]),   # Red Brick
    2: np.array([50, 200, 50]),   # Green Plant
    3: np.array([50, 50, 200]),   # Blue Stone
    4: np.array([200, 200, 50])   # Yellow Gold
}

# Entities / Sprites (x, y, type/color)
sprites = [
    {"x": 7.5, "y": 7.5, "color": np.array([255, 0, 255])},  # Enemy / Powerup
    {"x": 12.5, "y": 3.5, "color": np.array([0, 255, 255])}, # Decoration
]

# Main loop
running = True
while running:
    # 1. Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 2. Mouse Look and WASD Movement
    mouse_rel = pygame.mouse.get_rel()
    rot_speed = mouse_rel[0] * 0.003  # Scale mouse movement to rotation
    
    # Apply mouse rotation
    old_dir_x = dir_x
    dir_x = dir_x * math.cos(rot_speed) - dir_y * math.sin(rot_speed)
    dir_y = old_dir_x * math.sin(rot_speed) + dir_y * math.cos(rot_speed)
    old_plane_x = plane_x
    plane_x = plane_x * math.cos(rot_speed) - plane_y * math.sin(rot_speed)
    plane_y = old_plane_x * math.sin(rot_speed) + plane_y * math.cos(rot_speed)

    keys = pygame.key.get_pressed()
    move_speed = 0.05

    # Keyboard Movement vectors
    dx = dir_x * move_speed
    dy = dir_y * move_speed
    px = plane_x * move_speed
    py = plane_y * move_speed

    if keys[pygame.K_w]:
        if world_map[int(pos_x + dx)][int(pos_y)] == 0: pos_x += dx
        if world_map[int(pos_x)][int(pos_y + dy)] == 0: pos_y += dy
    if keys[pygame.K_s]:
        if world_map[int(pos_x - dx)][int(pos_y)] == 0: pos_x -= dx
        if world_map[int(pos_x)][int(pos_y - dy)] == 0: pos_y -= dy
    if keys[pygame.K_a]:
        if world_map[int(pos_x - py)][int(pos_y)] == 0: pos_x -= py
        if world_map[int(pos_x)][int(pos_y + px)] == 0: pos_y += px
    if keys[pygame.K_d]:
        if world_map[int(pos_x + py)][int(pos_y)] == 0: pos_x += py
        if world_map[int(pos_x)][int(pos_y - px)] == 0: pos_y -= px

    # 3. Access Raw Screen Pixel Array via Surfarray for Extreme Speed
    screen_array = pygame.surfarray.pixels3d(screen)
    
    # Fill Ceiling & Floor with basic vertical gradients (Atmospheric styling)
    screen_array[:, :HEIGHT // 2] = [40, 40, 60]   # Sky / Ceiling
    screen_array[:, HEIGHT // 2:] = [60, 60, 60]   # Ground / Floor

    # Keep track of depth buffer for sprite rendering
    z_buffer = np.zeros(WIDTH)

    # 4. Raycasting Engine Loop (Column by Column)
    for x in range(WIDTH):
        camera_x = 2.0 * x / WIDTH - 1.0
        ray_dir_x = dir_x + plane_x * camera_x
        ray_dir_y = dir_y + plane_y * camera_x

        map_x = int(pos_x)
        map_y = int(pos_y)

        delta_dist_x = abs(1.0 / ray_dir_x) if ray_dir_x != 0 else 1e30
        delta_dist_y = abs(1.0 / ray_dir_y) if ray_dir_y != 0 else 1e30

        hit = 0
        side = 0

        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (pos_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - pos_x) * delta_dist_x

        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (pos_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - pos_y) * delta_dist_y

        # DDA Loop
        while hit == 0:
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            if world_map[map_x][map_y] > 0:
                hit = 1

        # Calculate Perpendicular Distance (Fish-eye correction)
        if side == 0:
            perp_wall_dist = (side_dist_x - delta_dist_x)
        else:
            perp_wall_dist = (side_dist_y - delta_dist_y)
        
        z_buffer[x] = perp_wall_dist

        # Wall Rendering
        line_height = int(HEIGHT / (perp_wall_dist if perp_wall_dist != 0 else 1e-30))
        draw_start = max(0, -line_height // 2 + HEIGHT // 2)
        draw_end = min(HEIGHT, line_height // 2 + HEIGHT // 2)

        # Retrieve base color from map data ID
        wall_id = world_map[map_x][map_y]
        base_color = wall_colors.get(wall_id, np.array([200, 200, 200]))

        # Apply shading / lighting attenuation (Fog effect based on distance)
        shading_factor = max(0.1, 1.0 - (perp_wall_dist / 15.0))
        if side == 1:
            shading_factor *= 0.7  # Darken side walls for 3D depth perception
        
        final_color = (base_color * shading_factor).astype(np.uint8)

        # Write directly into the pixel array column
        if draw_start < draw_end:
            screen_array[x, draw_start:draw_end] = final_color

    # 5. Billboard Sprite Rendering
    for sprite in sprites:
        # Translate sprite position relative to camera
        sprite_x = sprite["x"] - pos_x
        sprite_y = sprite["y"] - pos_y

        # Transform with inverse camera matrix
        inv_det = 1.0 / (plane_x * dir_y - dir_x * plane_y)
        transform_x = inv_det * (dir_y * sprite_x - dir_x * sprite_y)
        transform_y = inv_det * (-plane_y * sprite_x + plane_x * sprite_y)  # Depth (Z)

        if transform_y > 0:  # Only render if in front of camera
            sprite_screen_x = int((WIDTH / 2) * (1.0 + transform_x / transform_y))
            
            # Calculate dynamic dimensions on screen
            sprite_height = abs(int(HEIGHT / (transform_y if transform_y != 0 else 1e-30)))
            draw_start_y = max(0, -sprite_height // 2 + HEIGHT // 2)
            draw_end_y = min(HEIGHT, sprite_height // 2 + HEIGHT // 2)

            sprite_width = abs(int(HEIGHT / (transform_y if transform_y != 0 else 1e-30)))
            draw_start_x = max(0, -sprite_width // 2 + sprite_screen_x)
            draw_end_x = min(WIDTH, sprite_width // 2 + sprite_screen_x)

            # Draw simple block-billboard with z-buffering checks
            for stripe in range(draw_start_x, draw_end_x):
                if transform_y < z_buffer[stripe]:
                    screen_array[stripe, draw_start_y:draw_end_y] = (sprite["color"] * max(0.2, 1.0 - transform_y / 12.0)).astype(np.uint8)

    # Release Surfarray lock before updating display
    del screen_array

    pygame.display.flip()
    clock.tick(60)

pygame.quit() 
