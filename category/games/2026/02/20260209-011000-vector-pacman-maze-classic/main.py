import pygame
import numpy as np
import sys
from enum import Enum
from typing import Tuple, List, Optional

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GRID_SIZE = 20
COLS = SCREEN_WIDTH // GRID_SIZE
ROWS = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 182, 193)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
FRIGHTENED_BLUE = (0, 50, 255)

# Grid Values
EMPTY = 0
WALL = 1
DOT = 2
POWER_PELLET = 3
PACMAN = 4
BLINKY = 5
PINKY = 6
INKY = 7
CLYDE = 8

# Points
DOT_POINTS = 10
POWER_PELLET_POINTS = 50
GHOST_POINTS = [200, 400, 800, 1600]

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

class GhostMode(Enum):
    CHASE = 0
    FRIGHTENED = 1

class Maze:
    # Classic Pac-Man maze layout adapted for 30 columns x 28 rows
    # 1 = wall, 0 = path, 2 = dot, 3 = power pellet
    LAYOUT = [
        "111111111111111111111111111111",
        "122222222122222222222112222221",
        "131111112111111111121111111131",
        "121111112111111111121111111121",
        "122222222222222222222222222221",
        "121111121111111211111111121121",
        "122222121111111222222221222221",
        "111111121111111211111111121111",
        "000000022222222222222222220000",
        "111111121111111211111111121111",
        "122222222222122222222122222221",
        "121111121111111211111111111121",
        "122212222222222000000222221221",
        "111212111111111111111111121111",
        "000212222222222222222222221000",
        "111212111111111111111111121111",
        "122212222222222211122222212221",
        "121111121111111211111111121121",
        "122222121111111222222221222221",
        "121111121111111211111111121121",
        "122222222222122222222122222221",
        "111111121111111211111111111121",
        "122222222222222222222222222221",
        "121111121111111211111111121121",
        "122222222122222222222112222221",
        "131111112111111111121111111131",
        "122222222222222222222222222221",
        "111111111111111111111111111111",
    ]

    def __init__(self):
        self.grid = np.zeros((ROWS, COLS), dtype=int)
        self._parse_layout()

    def _parse_layout(self):
        ghost_box_start_row = 12
        ghost_box_end_row = 16
        ghost_box_start_col = 13
        ghost_box_end_col = 17

        for r, row in enumerate(self.LAYOUT):
            for c, char in enumerate(row):
                if r >= ROWS:
                    break
                if char == '1':
                    self.grid[r, c] = WALL
                elif char == '0' or char == '2':
                    self.grid[r, c] = DOT
                elif char == '3':
                    self.grid[r, c] = POWER_PELLET
                elif char == ' ':
                    self.grid[r, c] = EMPTY

        # Create ghost box (walls around center)
        for r in range(ghost_box_start_row, ghost_box_end_row + 1):
            for c in range(ghost_box_start_col, ghost_box_end_col + 1):
                if r == ghost_box_start_row or r == ghost_box_end_row:
                    self.grid[r, c] = WALL
                elif c == ghost_box_start_col or c == ghost_box_end_col:
                    self.grid[r, c] = WALL
                else:
                    self.grid[r, c] = EMPTY
                    # Remove dots from ghost box
                    if self.grid[r, c] == DOT:
                        self.grid[r, c] = EMPTY

        # Ghost box door
        self.grid[ghost_box_start_row, 15:16] = DOT

    def is_wall(self, row: int, col: int) -> bool:
        return self.grid[row, col] == WALL

    def remove_dot(self, row: int, col: int) -> bool:
        if self.grid[row, col] in (DOT, POWER_PELLET):
            self.grid[row, col] = EMPTY
            return True
        return False

    def get_dot_count(self) -> int:
        return np.count_nonzero(self.grid == DOT)

    def get_power_pellet_count(self) -> int:
        return np.count_nonzero(self.grid == POWER_PELLET)

    def has_warp_tunnel(self, row: int, col: int) -> bool:
        return col == 0 or col == COLS - 1

class Entity:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.direction = Direction.NONE

    def get_position(self) -> Tuple[int, int]:
        return (self.col * GRID_SIZE + GRID_SIZE // 2,
                self.row * GRID_SIZE + GRID_SIZE // 2)

    def get_grid_position(self) -> Tuple[int, int]:
        return (self.row, self.col)

class Ghost(Entity):
    def __init__(self, row: int, col: int, ghost_type: int, color: Tuple[int, int, int]):
        super().__init__(row, col)
        self.ghost_type = ghost_type
        self.color = color
        self.mode = GhostMode.CHASE
        self.frightened_timer = 0
        self.direction = Direction.LEFT
        self.start_row = row
        self.start_col = col

    def reset(self):
        self.row = self.start_row
        self.col = self.start_col
        self.mode = GhostMode.CHASE
        self.frightened_timer = 0
        self.direction = Direction.LEFT

    def set_frightened(self, duration: int):
        self.mode = GhostMode.FRIGHTENED
        self.frightened_timer = duration

    def update_frightened(self):
        if self.mode == GhostMode.FRIGHTENED:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.mode = GhostMode.CHASE

    def get_target(self, pacman: 'Pacman', blinky: Optional['Ghost']) -> Tuple[int, int]:
        pr, pc = pacman.get_grid_position()

        if self.mode == GhostMode.FRIGHTENED:
            # Random target when frightened
            return (np.random.randint(0, ROWS), np.random.randint(0, COLS))

        if self.ghost_type == BLINKY:
            # Target Pacman's current position
            return (pr, pc)
        elif self.ghost_type == PINKY:
            # Target 4 tiles ahead of Pacman
            dr, dc = pacman.direction.value
            return (max(0, min(ROWS - 1, pr + dr * 4)),
                    max(0, min(COLS - 1, pc + dc * 4)))
        elif self.ghost_type == INKY and blinky:
            # Use vector between Blinky and Pacman
            br, bc = blinky.get_grid_position()
            dr, dc = pacman.direction.value
            target_r = pr + dr * 2
            target_c = pc + dc * 2
            vector_r = target_r - br
            vector_c = target_c - bc
            return (max(0, min(ROWS - 1, int(br + vector_r * 2))),
                    max(0, min(COLS - 1, int(bc + vector_c * 2))))
        elif self.ghost_type == CLYDE:
            # Move randomly if too close to Pacman, otherwise target Pacman
            dist = abs(self.row - pr) + abs(self.col - pc)
            if dist < 8:
                return (np.random.randint(0, ROWS), np.random.randint(0, COLS))
            return (pr, pc)

        return (pr, pc)

    def move(self, maze: Maze, pacman: 'Pacman', blinky: Optional['Ghost']):
        target_row, target_col = self.get_target(pacman, blinky)

        # Get valid moves
        valid_moves = []
        for direction in Direction:
            if direction == Direction.NONE:
                continue
            dr, dc = direction.value
            new_row = self.row + dr
            new_col = self.col + dc

            # Handle warp tunnels
            if maze.has_warp_tunnel(self.row, self.col):
                if new_col < 0:
                    new_col = COLS - 1
                elif new_col >= COLS:
                    new_col = 0

            # Check if valid move (not wall, and not reversing if possible)
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if not maze.is_wall(new_row, new_col):
                    # Don't reverse direction unless necessary
                    reverse = (direction.value[0] == -self.direction.value[0] and
                              direction.value[1] == -self.direction.value[1])
                    if len(valid_moves) == 0 or not reverse:
                        valid_moves.append((direction, new_row, new_col))

        # If no valid moves (shouldn't happen in proper maze), allow reverse
        if not valid_moves:
            for direction in Direction:
                if direction == Direction.NONE:
                    continue
                dr, dc = direction.value
                new_row = self.row + dr
                new_col = self.col + dc
                if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                    if not maze.is_wall(new_row, new_col):
                        valid_moves.append((direction, new_row, new_col))

        if valid_moves:
            # Choose move that minimizes distance to target
            if self.mode == GhostMode.FRIGHTENED:
                # Maximize distance when frightened
                best_move = max(valid_moves,
                               key=lambda m: -((m[1] - target_row)**2 + (m[2] - target_col)**2))
            else:
                # Minimize distance when chasing
                best_move = min(valid_moves,
                               key=lambda m: (m[1] - target_row)**2 + (m[2] - target_col)**2)

            self.direction, self.row, self.col = best_move

class Pacman(Entity):
    def __init__(self, row: int, col: int):
        super().__init__(row, col)
        self.next_direction = Direction.NONE

    def set_direction(self, direction: Direction):
        self.next_direction = direction

    def move(self, maze: Maze):
        # Try to change to next direction
        if self.next_direction != Direction.NONE:
            dr, dc = self.next_direction.value
            new_row = self.row + dr
            new_col = self.col + dc

            # Handle warp tunnels
            if maze.has_warp_tunnel(self.row, self.col):
                if new_col < 0:
                    new_col = COLS - 1
                elif new_col >= COLS:
                    new_col = 0

            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if not maze.is_wall(new_row, new_col):
                    self.direction = self.next_direction

        # Move in current direction
        dr, dc = self.direction.value
        new_row = self.row + dr
        new_col = self.col + dc

        # Handle warp tunnels
        if maze.has_warp_tunnel(self.row, self.col):
            if new_col < 0:
                new_col = COLS - 1
            elif new_col >= COLS:
                new_col = 0

        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            if not maze.is_wall(new_row, new_col):
                self.row = new_row
                self.col = new_col

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Pac-Man Maze")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self):
        self.maze = Maze()
        self.pacman = Pacman(21, 14)  # Starting position (lower-middle)

        # Initialize ghosts
        self.blinky = Ghost(11, 14, BLINKY, RED)
        self.pinky = Ghost(14, 13, PINKY, PINK)
        self.inky = Ghost(14, 14, INKY, CYAN)
        self.clyde = Ghost(14, 15, CLYDE, ORANGE)

        self.ghosts = [self.blinky, self.pinky, self.inky, self.clyde]

        self.score = 0
        self.lives = 3
        self.game_over = False
        self.won = False
        self.ghost_eaten_count = 0
        self.power_pellet_timer = 0
        self.move_timer = 0
        self.move_delay = 8  # Frames between moves

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.pacman.set_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.pacman.set_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.pacman.set_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.set_direction(Direction.RIGHT)
                elif event.key == pygame.K_r and (self.game_over or self.won):
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    return False
        return True

    def update(self):
        if self.game_over or self.won:
            return

        self.move_timer += 1

        # Update frightened timer
        if self.power_pellet_timer > 0:
            self.power_pellet_timer -= 1
            if self.power_pellet_timer == 0:
                for ghost in self.ghosts:
                    ghost.mode = GhostMode.CHASE
                self.ghost_eaten_count = 0

        # Move entities at controlled pace
        if self.move_timer >= self.move_delay:
            self.move_timer = 0

            # Move Pacman
            self.pacman.move(self.maze)

            # Check dot/power pellet collision
            pr, pc = self.pacman.get_grid_position()
            if self.maze.grid[pr, pc] == DOT:
                self.maze.remove_dot(pr, pc)
                self.score += DOT_POINTS
            elif self.maze.grid[pr, pc] == POWER_PELLET:
                self.maze.remove_dot(pr, pc)
                self.score += POWER_PELLET_POINTS
                self.power_pellet_timer = 400  # ~7 seconds at 60 FPS
                self.ghost_eaten_count = 0
                for ghost in self.ghosts:
                    ghost.set_frightened(400)

            # Move ghosts
            for ghost in self.ghosts:
                ghost.update_frightened()
                ghost.move(self.maze, self.pacman, self.blinky)

            # Check ghost collision
            for ghost in self.ghosts:
                gr, gc = ghost.get_grid_position()
                if gr == pr and gc == pc:
                    if ghost.mode == GhostMode.FRIGHTENED:
                        # Eat ghost
                        self.score += GHOST_POINTS[min(self.ghost_eaten_count, 3)]
                        self.ghost_eaten_count += 1
                        ghost.row = 14  # Send back to ghost box
                        ghost.col = 14
                        ghost.mode = GhostMode.CHASE
                    else:
                        # Lose life
                        self.lives -= 1
                        if self.lives <= 0:
                            self.game_over = True
                        else:
                            # Reset positions
                            self.pacman.row = 21
                            self.pacman.col = 14
                            self.pacman.direction = Direction.NONE
                            self.pacman.next_direction = Direction.NONE
                            for g in self.ghosts:
                                g.reset()
                            self.power_pellet_timer = 0
                            self.ghost_eaten_count = 0

            # Check win condition
            if self.maze.get_dot_count() == 0 and self.maze.get_power_pellet_count() == 0:
                self.won = True

    def draw(self):
        self.screen.fill(BLACK)

        # Draw maze
        for r in range(ROWS):
            for c in range(COLS):
                x = c * GRID_SIZE
                y = r * GRID_SIZE

                if self.maze.is_wall(r, c):
                    pygame.draw.rect(self.screen, BLUE, (x, y, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, BLUE, (x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4), 2)
                elif self.maze.grid[r, c] == DOT:
                    pygame.draw.circle(self.screen, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 2)
                elif self.maze.grid[r, c] == POWER_PELLET:
                    pygame.draw.circle(self.screen, WHITE, (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 6)

        # Draw Pacman
        px, py = self.pacman.get_position()
        pygame.draw.circle(self.screen, YELLOW, (px, py), GRID_SIZE // 2 - 2)

        # Draw ghosts
        for ghost in self.ghosts:
            gx, gy = ghost.get_position()
            color = FRIGHTENED_BLUE if ghost.mode == GhostMode.FRIGHTENED else ghost.color
            pygame.draw.circle(self.screen, color, (gx, gy), GRID_SIZE // 2 - 2)
            # Eyes
            eye_offset_x = -4 if ghost.direction == Direction.LEFT else 4
            pygame.draw.circle(self.screen, WHITE, (gx + eye_offset_x - 2, gy - 2), 3)
            pygame.draw.circle(self.screen, WHITE, (gx + eye_offset_x + 2, gy - 2), 3)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))

        # Draw game over / win screen
        if self.game_over:
            text = self.big_font.render("GAME OVER", True, RED)
            subtext = self.font.render("Press R to restart", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            subrect = subtext.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(text, text_rect)
            self.screen.blit(subtext, subrect)
        elif self.won:
            text = self.big_font.render("YOU WIN!", True, YELLOW)
            subtext = self.font.render("Press R to restart", True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            subrect = subtext.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(text, text_rect)
            self.screen.blit(subtext, subrect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
