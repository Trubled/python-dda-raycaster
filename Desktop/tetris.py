import os
import random
import time
import msvcrt

# Board dimensions
WIDTH, HEIGHT = 10, 20

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],                 # I
    [[1, 1], [1, 1]],               # O
    [[0, 1, 0], [1, 1, 1]],         # T
    [[1, 1, 0], [0, 1, 1]],         # S
    [[0, 1, 1], [1, 1, 0]],         # Z
    [[1, 0, 0], [1, 1, 1]],         # J
    [[0, 0, 1], [1, 1, 1]]          # L
]

class Tetris:
    def __init__(self):
        self.board = [[0 * WIDTH for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.current_piece = self.new_piece()
        self.piece_x = WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        self.game_over = False
        self.score = 0

    def new_piece(self):
        return random.choice(SHAPES)

    def rotate(self, piece):
        return [list(row) for row in zip(*piece[::-1])]

    def check_collision(self, px, py, piece):
        for r_idx, row in enumerate(piece):
            for c_idx, val in enumerate(row):
                if val:
                    nx, ny = px + c_idx, py + r_idx
                    if nx < 0 or nx >= WIDTH or ny >= HEIGHT:
                        return True
                    if ny >= 0 and self.board[ny][nx]:
                        return True
        return False

    def merge_piece(self):
        for r_idx, row in enumerate(self.current_piece):
            for c_idx, val in enumerate(row):
                if val:
                    ny, nx = self.piece_y + r_idx, self.piece_x + c_idx
                    if 0 <= ny < HEIGHT and 0 <= nx < WIDTH:
                        self.board[ny][nx] = 1
        self.clear_lines()
        self.current_piece = self.new_piece()
        self.piece_x = WIDTH // 2 - len(self.current_piece[0]) // 2
        self.piece_y = 0
        if self.check_collision(self.piece_x, self.piece_y, self.current_piece):
            self.game_over = True

    def clear_lines(self):
        lines_to_clear = [i for i, row in enumerate(self.board) if all(row)]
        for i in lines_to_clear:
            del self.board[i]
            self.board.insert(0, [0] * WIDTH) # inserts empty row at top
            self.score += 100

    def run(self):
        fall_time = time.time()
        fall_speed = 0.4
        
        try:
            while not self.game_over:
                # Handle non-blocking keyboard input
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == 'a' and not self.check_collision(self.piece_x - 1, self.piece_y, self.current_piece):
                        self.piece_x -= 1
                    elif key == 'd' and not self.check_collision(self.piece_x + 1, self.piece_y, self.current_piece):
                        self.piece_x += 1
                    elif key == 's' and not self.check_collision(self.piece_x, self.piece_y + 1, self.current_piece):
                        self.piece_y += 1
                    elif key == 'w':
                        rotated = self.rotate(self.current_piece)
                        if not self.check_collision(self.piece_x, self.piece_y, rotated):
                            self.current_piece = rotated

                # Gravity fall timer
                if time.time() - fall_time > fall_speed:
                    if not self.check_collision(self.piece_x, self.piece_y + 1, self.current_piece):
                        self.piece_y += 1
                    else:
                        self.merge_piece()
                    fall_time = time.time()

                # Render frame
                output = ["=== TERMINAL TETRIS ===", f"Score: {self.score}"]
                
                # Build temporary display grid including active piece
                display_board = [row[:] for row in self.board]
                for r_idx, row in enumerate(self.current_piece):
                    for c_idx, val in enumerate(row):
                        if val:
                            ny, nx = self.piece_y + r_idx, self.piece_x + c_idx
                            if 0 <= ny < HEIGHT and 0 <= nx < WIDTH:
                                display_board[ny][nx] = 2

                for row in display_board:
                    line = "".join(["[]" if cell == 2 else "[]" if cell == 1 else " ." for cell in row])
                    output.append(line)
                
                output.append("Controls: A/D (Move) | S (Drop) | W (Rotate)")
                
                os.system('cls' if os.name == 'nt' else 'clear')
                print("\n".join(output))
                time.sleep(0.03)

            print(f"\nGame Over! Final Score: {self.score}")
            
        except KeyboardInterrupt:
            print("\nTetris session ended.")

if __name__ == "__main__":
    game = Tetris()
    game.run()
