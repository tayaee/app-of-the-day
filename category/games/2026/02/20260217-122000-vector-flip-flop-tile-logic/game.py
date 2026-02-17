"""Main game class for Vector Flip Flop Tile Logic."""

import pygame
import random
from enum import Enum
from config import *
from grid import Grid


class GameState(Enum):
    """Game states."""
    IDLE = "idle"
    PLAYING = "playing"
    SOLVED = "solved"


class Game:
    """Main game class managing the Lights Out puzzle."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Flip Flop Tile Logic")
        self.clock = pygame.time.Clock()
        self.running = True

        # Game state
        self.state = GameState.IDLE
        self.grid = Grid()
        self.moves = 0
        self.score = 0
        self.high_score = 0

        # Grid position tracking
        self.tile_rects = self._create_tile_rects()

        # Fonts
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.status_font = pygame.font.Font(None, STATUS_FONT_SIZE)
        self.instruction_font = pygame.font.Font(None, INSTRUCTION_FONT_SIZE)

    def _create_tile_rects(self):
        """Create collision rectangles for each tile."""
        rects = {}
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * (TILE_SIZE + TILE_GAP)
                y = GRID_OFFSET_Y + row * (TILE_SIZE + TILE_GAP)
                rects[(row, col)] = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        return rects

    def reset_game(self):
        """Reset and generate a new solvable puzzle."""
        self.grid = Grid()
        self.moves = 0
        self.score = 0
        self.state = GameState.PLAYING
        self._generate_solvable_puzzle()

    def _generate_solvable_puzzle(self):
        """Generate a solvable puzzle by starting from solved and applying moves."""
        solved_grid = Grid()

        # Generate 5-15 random moves to create the puzzle
        num_moves = random.randint(5, 15)
        moves_made = []

        for _ in range(num_moves):
            row = random.randint(0, GRID_SIZE - 1)
            col = random.randint(0, GRID_SIZE - 1)
            solved_grid.flip(row, col)
            moves_made.append((row, col))

        # Set the grid to this state
        self.grid.tiles = solved_grid.tiles.copy()

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_click(event.pos)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.reset_game()

    def _handle_mouse_click(self, pos):
        """Handle mouse click on the grid."""
        if self.state == GameState.PLAYING or self.state == GameState.IDLE:
            grid_pos = self.grid.get_position(
                pos[0], pos[1], TILE_SIZE, TILE_GAP,
                GRID_OFFSET_X, GRID_OFFSET_Y
            )
            if grid_pos:
                row, col = grid_pos
                self.grid.flip(row, col)
                self.moves += 1
                self._update_score()

                if self.grid.is_solved():
                    self._on_solved()

    def _update_score(self):
        """Update the current score based on moves made."""
        self.score = max(MIN_SCORE, SCORE_BASE - self.moves * SCORE_PER_MOVE)

    def _on_solved(self):
        """Handle puzzle solved state."""
        self.state = GameState.SOLVED
        if self.score > self.high_score:
            self.high_score = self.score

    def render(self):
        """Render the game."""
        self.screen.fill(BACKGROUND)

        # Draw title
        title_text = self.title_font.render("Flip Flop Tile Logic", True, TEXT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        self.screen.blit(title_text, title_rect)

        # Draw grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                self._draw_tile(row, col)

        # Draw score
        score_text = self.score_font.render(str(self.score), True, TEXT_COLOR)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, GRID_OFFSET_Y + GRID_HEIGHT + 60))
        self.screen.blit(score_text, score_rect)

        # Draw moves
        moves_text = self.status_font.render(f"Moves: {self.moves}", True, (180, 180, 180))
        moves_rect = moves_text.get_rect(center=(SCREEN_WIDTH // 2, GRID_OFFSET_Y + GRID_HEIGHT + 100))
        self.screen.blit(moves_text, moves_rect)

        # Draw high score
        high_score_text = self.instruction_font.render(f"Best: {self.high_score}", True, ACCENT_COLOR)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, GRID_OFFSET_Y + GRID_HEIGHT + 130))
        self.screen.blit(high_score_text, high_score_rect)

        # Draw status messages
        if self.state == GameState.IDLE:
            msg = "Click any tile to start"
            msg_text = self.status_font.render(msg, True, TEXT_COLOR)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)
        elif self.state == GameState.SOLVED:
            msg = "Solved! Press R for new puzzle"
            msg_text = self.status_font.render(msg, True, (100, 200, 100))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)
        else:
            # Playing state
            msg = "Turn all tiles black. R to reset"
            msg_text = self.instruction_font.render(msg, True, (120, 120, 120))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60))
            self.screen.blit(msg_text, msg_rect)

        pygame.display.flip()

    def _draw_tile(self, row, col):
        """Draw a single tile."""
        x = GRID_OFFSET_X + col * (TILE_SIZE + TILE_GAP)
        y = GRID_OFFSET_Y + row * (TILE_SIZE + TILE_GAP)
        rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)

        if self.grid.is_on(row, col):
            color = TILE_ON
        else:
            color = TILE_OFF

        pygame.draw.rect(self.screen, color, rect, border_radius=4)
        pygame.draw.rect(self.screen, TILE_BORDER, rect, width=2, border_radius=4)

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0-24 corresponding to grid positions (row * 5 + col)

        Returns:
            (observation, reward, done)
        """
        if self.state == GameState.IDLE:
            self.state = GameState.PLAYING

        row = action // GRID_SIZE
        col = action % GRID_SIZE

        was_solved = self.grid.is_solved()
        self.grid.flip(row, col)
        self.moves += 1
        self._update_score()

        reward = 0
        done = False

        if self.grid.is_solved() and not was_solved:
            reward = REWARD_SOLVED
            done = True
            self.state = GameState.SOLVED
            if self.score > self.high_score:
                self.high_score = self.score
        else:
            # Calculate progress reward based on how many tiles are off
            off_count = sum(1 for tile in self.grid.get_state() if not tile)
            total_tiles = GRID_SIZE * GRID_SIZE
            progress_reward = off_count / total_tiles
            reward = progress_reward * REWARD_CORRECT

        return self.get_observation(), reward, done

    def get_observation(self):
        """Return current game state for AI."""
        return {
            "grid_state": self.grid.get_state(),
            "moves": self.moves,
            "score": self.score,
            "is_solved": self.grid.is_solved(),
            "state": self.state.value,
            "high_score": self.high_score
        }

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
