import os
import random
import time
import msvcrt

WORLD_WIDTH = 140
VIEW_WIDTH = 50
HEIGHT = 17

class Platformer:
    def __init__(self):
        self.x = 3.0
        self.y = float(HEIGHT - 3)
        self.vx = 0.0
        self.vy = 0.0
        self.is_grounded = False
        self.facing = 1  # 1 for right, -1 for left
        
        # States
        self.power_state = 0  # 0 = Normal, 1 = Super, 2 = Fire Flower
        self.fire_timer = 0   
        self.is_running = False  
        self.has_mount = False   
        
        self.score = 0
        self.game_over = False
        self.won = False
        
        self.platforms, self.moving_platforms, self.blocks, self.coins, self.enemies, self.fireballs, self.flag_x = self.generate_level()

    def generate_level(self):
        platforms = []
        moving_platforms = []
        blocks = []
        coins = []
        enemies = []
        fireballs = []
        
        # Starting ground
        platforms.append((0, 22, HEIGHT - 2))
        
        current_x = 26
        while current_x < WORLD_WIDTH - 25:
            p_width = random.randint(9, 15)
            p_y = random.randint(HEIGHT - 7, HEIGHT - 4)
            p_end = current_x + p_width
            
            if random.random() < 0.2 and current_x > 30:
                mp_y = float(p_y)
                moving_platforms.append({
                    "x1": float(current_x), 
                    "x2": float(p_end), 
                    "y": mp_y, 
                    "x": float(current_x), 
                    "dir": 0.2
                })
            else:
                platforms.append((current_x, p_end, p_y))
            
            # Mystery blocks
            if random.random() < 0.7:
                blocks.append({
                    "x": current_x + p_width // 2, 
                    "y": p_y - 3, 
                    "hit": False, 
                    "type": random.choice(["flower", "mushroom", "mount", "coin"])
                })
            
            # Coins
            if random.random() < 0.65:
                coins.append({"x": current_x + 3, "y": p_y - 2, "collected": False})
            
            # Enemies
            if p_width >= 8 and random.random() < 0.45:
                enemies.append({
                    "x": float(current_x + 2), 
                    "y": float(p_y - 1), 
                    "min_x": float(current_x + 1), 
                    "max_x": float(p_end - 1), 
                    "dir": 0.15, 
                    "alive": True
                })
            
            current_x = p_end + random.randint(4, 7)
            
        flag_x = WORLD_WIDTH - 12
        platforms.append((flag_x - 4, WORLD_WIDTH - 2, HEIGHT - 2))
        
        return platforms, moving_platforms, blocks, coins, enemies, fireballs, flag_x

    def update(self, key):
        if key == 'e':
            self.is_running = not self.is_running

        # Increased speeds for expansive lateral movement
        max_speed = 4.2 if self.is_running else 2.8
        accel = 0.55 if self.is_running else 0.4

        # Responsive horizontal control & facing tracking
        if key == 'a':
            self.vx = max(-max_speed, self.vx - accel)
            self.facing = -1
        elif key == 'd':
            self.vx = min(max_speed, self.vx + accel)
            self.facing = 1

        if self.is_grounded:
            if key not in ('a', 'd'):
                self.vx *= 0.35
                if abs(self.vx) < 0.05:
                    self.vx = 0.0
        else:
            # Minimal air friction to allow wide, sweeping jumps across gaps
            self.vx *= 0.999

        # Jump physics
        if key == 'w' and self.is_grounded:
            run_boost = 0.35 if self.is_running else 0.0
            if self.has_mount:
                self.vy = -3.6
            elif self.power_state > 0:
                self.vy = -3.1 - run_boost
            else:
                self.vy = -2.8 - run_boost
            self.is_grounded = False

        if self.power_state == 2:
            self.fire_timer -= 1
            if self.fire_timer <= 0:
                self.power_state = 1  

        # Shoot Bouncing Fireball with instant point-blank check and correct facing direction
        if key == 'f' and self.power_state == 2:
            fire_x = self.x + (1.0 * self.facing)
            new_fb = {
                "x": fire_x, 
                "y": self.y, 
                "vx": 1.4 * self.facing, 
                "vy": -0.8
            }
            
            hit_enemy = False
            for enemy in self.enemies:
                if enemy["alive"] and abs(enemy["x"] - new_fb["x"]) <= 1.2 and abs(enemy["y"] - new_fb["y"]) <= 1.2:
                    enemy["alive"] = False
                    hit_enemy = True
                    self.score += 150
                    break
            
            if not hit_enemy:
                self.fireballs.append(new_fb)

        # Gravity
        self.vy += 0.40
        self.x += self.vx
        self.y += self.vy

        if self.x < 0:
            self.x = 0
            self.vx = 0
        if self.x >= WORLD_WIDTH - 2:
            self.x = WORLD_WIDTH - 2
            self.vx = 0

        p_left = int(round(self.x))
        p_right = p_left if (self.power_state == 0 and not self.has_mount) else p_left + 1
        p_top = int(round(self.y))
        p_bottom = p_top if (self.power_state == 0 and not self.has_mount) else p_top + 1

        for mp in self.moving_platforms:
            mp["x"] += mp["dir"]
            if mp["x"] <= mp["x1"] or mp["x"] >= mp["x2"]:
                mp["dir"] *= -1

        # Check Mystery Block hits from underneath
        for block in self.blocks:
            if not block["hit"]:
                if (block["x"] - 1 <= p_right and p_left <= block["x"] + 1) and (block["y"] <= p_top <= block["y"] + 2) and self.vy < 0:
                    block["hit"] = True
                    self.vy = 0.5
                    if block["type"] == "flower":
                        self.power_state = 2
                        self.fire_timer = 220  
                        self.score += 1000
                    elif block["type"] == "mushroom":
                        self.power_state = max(1, self.power_state)
                        self.score += 500
                    elif block["type"] == "mount":
                        self.has_mount = True
                        self.score += 800
                    else:
                        self.score += 200

        # Check Coin pickups
        for coin in self.coins:
            if not coin["collected"]:
                if (p_left - 1 <= coin["x"] <= p_right + 1) and (p_top - 1 <= coin["y"] <= p_bottom + 1):
                    coin["collected"] = True
                    self.score += 100

        # Platform Collisions
        self.is_grounded = False
        floor_offset = 1 if (self.power_state == 0 and not self.has_mount) else 2
        
        for p_start, p_end, p_y in self.platforms:
            if p_start <= p_right and p_left <= p_end:
                if abs(p_bottom - p_y) <= 1 and self.vy >= 0:
                    self.y = float(p_y - floor_offset)
                    self.vy = 0.0
                    self.is_grounded = True
                    break

        for mp in self.moving_platforms:
            mp_int_x = int(round(mp["x"]))
            if mp_int_x <= p_right and p_left <= mp_int_x + 3:
                if abs(p_bottom - mp["y"]) <= 1 and self.vy >= 0:
                    self.y = float(mp["y"] - floor_offset)
                    self.vy = 0.0
                    self.is_grounded = True
                    self.x += mp["dir"]
                    break

        # Update Bouncing Fireballs & Collision Checks
        for fb in self.fireballs[:]:
            fb["x"] += fb["vx"]
            fb["vy"] += 0.35  # Fireball gravity
            fb["y"] += fb["vy"]
            
            fb_ix = int(round(fb["x"]))
            fb_iy = int(round(fb["y"]))
            
            # Bounce off platforms/ground
            for p_start, p_end, p_y in self.platforms:
                if p_start <= fb_ix <= p_end and abs(fb_iy - p_y) <= 1 and fb["vy"] > 0:
                    fb["y"] = float(p_y - 1)
                    fb["vy"] = -1.2  # Bounce upward!
                    break

            # Check enemy hits using a reliable proximity range
            hit_enemy = False
            for enemy in self.enemies:
                if enemy["alive"] and abs(enemy["x"] - fb["x"]) <= 1.2 and abs(enemy["y"] - fb["y"]) <= 1.2:
                    enemy["alive"] = False
                    hit_enemy = True
                    self.score += 150
                    break

            if hit_enemy or fb_ix < 0 or fb_ix >= WORLD_WIDTH or fb["y"] >= HEIGHT:
                self.fireballs.remove(fb)

        # Enemy Collisions & Stomping (Works for Small Mario too!)
        for enemy in self.enemies:
            if not enemy["alive"]:
                continue
                
            enemy["x"] += enemy["dir"]
            if enemy["x"] <= enemy["min_x"] or enemy["x"] >= enemy["max_x"]:
                enemy["dir"] *= -1

            ex = int(round(enemy["x"]))
            ey = int(round(enemy["y"]))

            if (p_left <= ex <= p_right) and (p_top <= ey <= p_bottom or (self.vy > 0 and self.y <= enemy["y"])):
                if self.vy > 0:
                    enemy["alive"] = False
                    self.vy = -2.4  # Bounce off enemy
                    self.score += 200
                else:
                    if self.has_mount:
                        self.has_mount = False
                        self.vy = -1.5
                        enemy["alive"] = False
                    elif self.power_state > 0:
                        self.power_state = 0  
                        self.fire_timer = 0
                        self.vy = -1.5
                        enemy["alive"] = False
                    else:
                        self.game_over = True

        if int(round(self.x)) >= self.flag_x:
            self.won = True

        if self.y >= HEIGHT:
            self.game_over = True

    def render(self):
        cam_x = int(self.x) - VIEW_WIDTH // 2
        if cam_x < 0:
            cam_x = 0
        if cam_x > WORLD_WIDTH - VIEW_WIDTH:
            cam_x = WORLD_WIDTH - VIEW_WIDTH

        screen = [[" " for _ in range(VIEW_WIDTH)] for _ in range(HEIGHT)]

        bg_cam_x = cam_x // 2
        for bx in range(WORLD_WIDTH * 2):
            screen_x = bx - bg_cam_x
            if 0 <= screen_x < VIEW_WIDTH:
                if bx % 12 == 0:
                    screen[0][screen_x] = "^"
                elif bx % 7 == 0:
                    screen[1][screen_x] = "~"

        for p_start, p_end, p_y in self.platforms:
            for wx in range(p_start, p_end + 1):
                screen_x = wx - cam_x
                if 0 <= screen_x < VIEW_WIDTH and 0 <= p_y < HEIGHT:
                    screen[p_y][screen_x] = "#"

        for mp in self.moving_platforms:
            mp_x = int(round(mp["x"]))
            for dx in range(4):
                screen_x = mp_x + dx - cam_x
                if 0 <= screen_x < VIEW_WIDTH and 0 <= mp["y"] < HEIGHT:
                    screen[int(mp["y"])][screen_x] = "="

        for block in self.blocks:
            bx = block["x"] - cam_x
            by = block["y"]
            if 0 <= bx < VIEW_WIDTH and 0 <= by < HEIGHT:
                screen[by][bx] = "?" if not block["hit"] else "-"

        for coin in self.coins:
            if not coin["collected"]:
                cx = coin["x"] - cam_x
                cy = coin["y"]
                if 0 <= cx < VIEW_WIDTH and 0 <= cy < HEIGHT:
                    screen[cy][cx] = "o"

        flag_screen_x = self.flag_x - cam_x
        if 0 <= flag_screen_x < VIEW_WIDTH:
            for fy in range(HEIGHT - 6, HEIGHT - 2):
                if 0 <= fy < HEIGHT:
                    screen[fy][flag_screen_x] = "P"

        for enemy in self.enemies:
            if enemy["alive"]:
                ex = int(round(enemy["x"])) - cam_x
                ey = int(round(enemy["y"]))
                if 0 <= ex < VIEW_WIDTH and 0 <= ey < HEIGHT:
                    screen[ey][ex] = "G"

        for fb in self.fireballs:
            fx = int(round(fb["x"])) - cam_x
            fy = int(round(fb["y"]))
            if 0 <= fx < VIEW_WIDTH and 0 <= fy < HEIGHT:
                screen[fy][fx] = "*"

        px = int(round(self.x)) - cam_x
        py = int(round(self.y))
        
        if self.power_state == 0 and not self.has_mount:
            if 0 <= px < VIEW_WIDTH and 0 <= py < HEIGHT:
                screen[py][px] = "m"
        else:
            char_set = "M"
            if self.power_state == 1: char_set = "S"
            elif self.power_state == 2: char_set = "F"
            
            sprite = [["Y", "Y"], [char_set, char_set]] if self.has_mount else [[char_set, char_set], [char_set, char_set]]
            for dy in range(2):
                for dx in range(2):
                    draw_y = py + dy
                    draw_x = px + dx
                    if 0 <= draw_x < VIEW_WIDTH and 0 <= draw_y < HEIGHT:
                        screen[draw_y][draw_x] = sprite[dy][dx]

        status_names = ["Small (m)", "Super (S)", f"Fire (F: {self.fire_timer})"]
        run_status = "ON" if self.is_running else "OFF"
        mount_status = "Yes" if self.has_mount else "No"
        
        output = [
            f"=== MARIO | Score: {self.score} | Form: {status_names[self.power_state]} | Run [E]: {run_status} | Mount: {mount_status} ===",
            "Controls: A/D (Move) | E (Sprint) | W (Jump) | F (Fireball) | Ctrl+C to Exit"
        ]
        for row in screen:
            output.append("".join(row))
        return "\n".join(output)

def run_game():
    game = Platformer()
    try:
        while not game.game_over and not game.won:
            key = ''
            if msvcrt.kbhit():
                key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
            
            game.update(key)
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print(game.render())
            
            time.sleep(0.04)
            
        os.system('cls' if os.name == 'nt' else 'clear')
        if game.won:
            print(f"VICTORY! Final Score: {game.score}")
        else:
            print("Game Over!")
            
    except KeyboardInterrupt:
        print("\nPlatformer session ended.")

if __name__ == "__main__":
    run_game()
