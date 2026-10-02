import math
import os
import time
import msvcrt

vertices = [
    [ 0,  0,  3.5],  # 0: Sharp nose cone (front)
    [ 0,  0.8, -1],  # 1: Top ridge (cockpit)
    [-2.5, -0.5, -1], # 2: Left wing tip
    [ 2.5, -0.5, -1], # 3: Right wing tip
    [ 0, -1.0, -1],  # 4: Bottom keel
    [-1,  0.5, -2],  # 5: Top-back-left
    [ 1,  0.5, -2],  # 6: Top-back-right
    [-1, -0.5, -2],  # 7: Bottom-back-left
    [ 1, -0.5, -2]   # 8: Bottom-back-right
]

faces = [
    (0, 1, 2),  # Top-left hull
    (0, 3, 1),  # Top-right hull
    (0, 2, 4),  # Bottom-left hull
    (0, 4, 3),  # Bottom-right hull
    (1, 5, 6),  # Top back plate
    (2, 7, 5),  # Left engine block
    (3, 6, 8),  # Right engine block
    (4, 8, 7),  # Bottom back plate
    (5, 7, 8),  # Back wall left
    (5, 8, 6)   # Back wall right
]

def rotate_x(x, y, z, angle):
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return x, y * cos_a - z * sin_a, y * sin_a + z * cos_a

def rotate_y(x, y, z, angle):
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return x * cos_a + z * sin_a, y, -x * sin_a + z * cos_a

def rotate_z(x, y, z, angle):
    rad = math.radians(angle)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return x * cos_a - y * sin_a, x * sin_a + y * cos_a, z

def draw_wireframe():
    angle_x = 0
    angle_y = 0
    angle_z = 0
    width, height = 60, 25
    
    try:
        while True:
            # Check for non-blocking keyboard input (Windows msvcrt)
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                if key == 'w': angle_x -= 5
                elif key == 's': angle_x += 5
                elif key == 'a': angle_y -= 5
                elif key == 'd': angle_y += 5
                elif key == 'q': angle_z -= 5
                elif key == 'e': angle_z += 5
            
            screen = [[" " for _ in range(width)] for _ in range(height)]
            
            rotated_vertices = []
            projected_points = []
            
            for vertex in vertices:
                x, y, z = rotate_x(vertex[0], vertex[1], vertex[2], angle_x)
                x, y, z = rotate_y(x, y, z, angle_y)
                x, y, z = rotate_z(x, y, z, angle_z)
                rotated_vertices.append((x, y, z))
                
                distance = 5
                factor = 20 / (z + distance)
                proj_x = int(width / 2 + x * factor * 2)
                proj_y = int(height / 2 + y * factor)
                projected_points.append((proj_x, proj_y))
            
            for face in faces:
                p0 = rotated_vertices[face[0]]
                p1 = rotated_vertices[face[1]]
                p2 = rotated_vertices[face[2]]
                
                ax, ay, az = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
                bx, by, bz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
                
                normal_z = ax * by - ay * bx
                
                if normal_z > 0:
                    face_edges = [
                        (face[0], face[1]),
                        (face[1], face[2]),
                        (face[2], face[0])
                    ]
                    
                    for edge in face_edges:
                        pt1 = projected_points[edge[0]]
                        pt2 = projected_points[edge[1]]
                        
                        steps = max(abs(pt1[0] - pt2[0]), abs(pt1[1] - pt2[1]), 1)
                        for i in range(steps + 1):
                            ix = int(pt1[0] + (pt2[0] - pt1[0]) * i / steps)
                            iy = int(pt1[1] + (pt2[1] - pt1[1]) * i / steps)
                            
                            if 0 <= ix < width and 0 <= iy < height:
                                screen[iy][ix] = "."

            os.system('cls' if os.name == 'nt' else 'clear')
            print("=== ELITE 3D: MANUAL FLIGHT MODE ===")
            print("Controls: W/S (Pitch) | A/D (Yaw) | Q/E (Roll)")
            print("\n".join(["".join(row) for row in screen]))
            print("Press Ctrl+C to exit.")
            
            time.sleep(0.03)
            
    except KeyboardInterrupt:
        print("\nFlight simulation ended.")

if __name__ == "__main__":
    draw_wireframe()
