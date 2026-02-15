"""Vector Klotski Block Escape - Game implementation."""

import sys
import pygame
from config import *


class Block:
    """Represents a single block in the puzzle."""

    def __init__(self, block_type, grid_x, grid_y):
        """Initialize a block."""
        self.block_type = block_type
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.selected = False

        # Determine size based on type
        if block_type == KING_2x2:
            self.width = 2
            self.height = 2
        elif block_type == VERTICAL_1x2:
            self.width = 1
            self.height = 2
        elif block_type == HORIZONTAL_2x1:
            self.width = 2
            self.height = 1
        else:  # SMALL_1x1
            self.width = 1
            self.height = 1

    def get_cells(self):
        """Get all grid cells occupied by this block."""
        cells = []
        for dy in range(self.height):
            for dx in range(self.width):
                cells.append((self.grid_x + dx, self.grid_y + dy))
        return cells

    def get_color(self):
        """Get the block's color."""
        if self.block_type == KING_2x2:
            return COLOR_KING_BLOCK, COLOR_KING_BORDER
        elif self.block_type == VERTICAL_1x2:
            return COLOR_VERTICAL_BLOCK, COLOR_VERTICAL_BORDER
        elif self.block_type == HORIZONTAL_2x1:
            return COLOR_HORIZONTAL_BLOCK, COLOR_HORIZONTAL_BORDER
        else:
            return COLOR_SMALL_BLOCK, COLOR_SMALL_BORDER


class KlotskiGame:
    """Main Klotski game class."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Klotski Block Escape")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.blocks = []
        self.selected_block = None
        self.moves = 0
        self.game_won = False
        self.use_easy_layout = False
        self.animating = False
        self.animation_data = None

        self._init_blocks()

    def _init_blocks(self):
        """Initialize blocks from layout."""
        layout = EASY_LAYOUT if self.use_easy_layout else STARTING_LAYOUT
        self.blocks = []

        # Process layout row by row, creating blocks
        processed = [[False for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                if processed[row][col]:
                    continue

                cell_type = layout[row][col]
                if cell_type == EMPTY:
                    continue

                # Determine block size and create it
                block_type = cell_type
                width = height = 1

                if block_type == KING_2x2:
                    width, height = 2, 2
                elif block_type == VERTICAL_1x2:
                    width, height = 1, 2
                elif block_type == HORIZONTAL_2x1:
                    width, height = 2, 1

                # Mark cells as processed
                for dy in range(height):
                    for dx in range(width):
                        if row + dy < GRID_ROWS and col + dx < GRID_COLS:
                            processed[row + dy][col + dx] = True

                self.blocks.append(Block(block_type, col, row))

    def is_valid_position(self, block, new_x, new_y):
        """Check if a block can be placed at the given position."""
        # Check bounds
        if new_x < 0 or new_y < 0:
            return False
        if new_x + block.width > GRID_COLS or new_y + block.height > GRID_ROWS:
            return False

        # Check collision with other blocks
        for other in self.blocks:
            if other is block:
                continue

            # Check if any cell would overlap
            for dy in range(block.height):
                for dx in range(block.width):
                    check_x = new_x + dx
                    check_y = new_y + dy
                    if (other.grid_x <= check_x < other.grid_x + other.width and
                            other.grid_y <= check_y < other.grid_y + other.height):
                        return False

        return True

    def can_move(self, block, direction):
        """Check if a block can move in the given direction."""
        dx, dy = direction
        new_x = block.grid_x + dx
        new_y = block.grid_y + dy
        return self.is_valid_position(block, new_x, new_y)

    def move_block(self, block, direction):
        """Move a block in the given direction."""
        if not self.can_move(block, direction):
            return False

        dx, dy = direction
        new_x = block.grid_x + dx
        new_y = block.grid_y + dy

        # Set up animation
        self.animating = True
        self.animation_data = {
            'block': block,
            'start_x': block.grid_x,
            'start_y': block.grid_y,
            'end_x': new_x,
            'end_y': new_y,
            'progress': 0
        }

        block.grid_x = new_x
        block.grid_y = new_y
        self.moves += 1

        # Check win condition (King block at bottom center)
        if (block.block_type == KING_2x2 and
                block.grid_x == 1 and block.grid_y == 3):
            self.game_won = True

        return True

    def get_block_at(self, grid_x, grid_y):
        """Get the block at the given grid position."""
        for block in self.blocks:
            if (block.grid_x <= grid_x < block.grid_x + block.width and
                    block.grid_y <= grid_y < block.grid_y + block.height):
                return block
        return None

    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

            if event.key == pygame.K_r:
                self.reset_game()
                return True

            if event.key == pygame.K_e:
                self.use_easy_layout = not self.use_easy_layout
                self.reset_game()
                return True

            # Move selected block with arrow keys
            if self.selected_block and not self.animating and not self.game_won:
                if event.key == pygame.K_UP:
                    self.move_block(self.selected_block, UP)
                elif event.key == pygame.K_DOWN:
                    self.move_block(self.selected_block, DOWN)
                elif event.key == pygame.K_LEFT:
                    self.move_block(self.selected_block, LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.move_block(self.selected_block, RIGHT)

        if event.type == pygame.MOUSEBUTTONDOWN and not self.animating:
            if event.button == 1:  # Left click
                mouse_x, mouse_y = event.pos
                grid_x = (mouse_x - GRID_OFFSET_X) // CELL_SIZE
                grid_y = (mouse_y - GRID_OFFSET_Y) // CELL_SIZE

                # Check if click is within grid
                if 0 <= grid_x < GRID_COLS and 0 <= grid_y < GRID_ROWS:
                    clicked_block = self.get_block_at(grid_x, grid_y)
                    if clicked_block:
                        # Deselect previous
                        if self.selected_block:
                            self.selected_block.selected = False
                        # Select new
                        self.selected_block = clicked_block
                        clicked_block.selected = True
                    else:
                        # Deselect if clicked empty space
                        if self.selected_block:
                            self.selected_block.selected = False
                            self.selected_block = None

        return True

    def update(self):
        """Update game state."""
        if self.animating and self.animation_data:
            anim = self.animation_data
            anim['progress'] += MOVE_SPEED

            distance = max(
                abs(anim['end_x'] - anim['start_x']),
                abs(anim['end_y'] - anim['start_y'])
            ) * CELL_SIZE

            if anim['progress'] >= distance:
                self.animating = False
                self.animation_data = None

    def _draw_grid(self):
        """Draw the game grid."""
        # Draw background grid
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE

                # Bottom center is the exit
                if col == 1 and row == 4:
                    pygame.draw.rect(self.screen, COLOR_EXIT,
                                   (x, y, CELL_SIZE * 2, CELL_SIZE))
                    pygame.draw.rect(self.screen, COLOR_EXIT_BORDER,
                                   (x, y, CELL_SIZE * 2, CELL_SIZE), 2)
                else:
                    pygame.draw.rect(self.screen, COLOR_EMPTY,
                                   (x, y, CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, COLOR_GRID,
                                   (x, y, CELL_SIZE, CELL_SIZE), 1)

        # Draw border around grid
        border_rect = (
            GRID_OFFSET_X - 2,
            GRID_OFFSET_Y - 2,
            GRID_COLS * CELL_SIZE + 4,
            GRID_ROWS * CELL_SIZE + 4
        )
        pygame.draw.rect(self.screen, COLOR_GRID, border_rect, 2)

        # Draw exit indicator below grid
        exit_x = GRID_OFFSET_X + 1 * CELL_SIZE
        exit_y = GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE + 5
        pygame.draw.polygon(self.screen, COLOR_EXIT_BORDER, [
            (exit_x, exit_y),
            (exit_x + CELL_SIZE * 2, exit_y),
            (exit_x + CELL_SIZE, exit_y + 10)
        ])

    def _draw_blocks(self):
        """Draw all blocks."""
        for block in self.blocks:
            # Calculate position
            x = GRID_OFFSET_X + block.grid_x * CELL_SIZE
            y = GRID_OFFSET_Y + block.grid_y * CELL_SIZE
            width = block.width * CELL_SIZE
            height = block.height * CELL_SIZE

            # Apply animation offset
            if self.animating and self.animation_data['block'] is block:
                anim = self.animation_data
                dx = anim['end_x'] - anim['start_x']
                dy = anim['end_y'] - anim['start_y']
                progress = min(anim['progress'] / (CELL_SIZE * max(abs(dx), abs(dy))), 1.0)
                x += dx * progress * CELL_SIZE
                y += dy * progress * CELL_SIZE

            # Get colors
            fill_color, border_color = block.get_color()

            # Draw block with padding
            padding = 3
            pygame.draw.rect(self.screen, fill_color,
                           (x + padding, y + padding,
                            width - padding * 2, height - padding * 2),
                           border_radius=5)

            # Draw border (thicker if selected)
            border_width = 4 if block.selected else 2
            border_color = COLOR_SELECTED if block.selected else border_color
            pygame.draw.rect(self.screen, border_color,
                           (x + padding, y + padding,
                            width - padding * 2, height - padding * 2),
                           border_width, border_radius=5)

            # Draw crown symbol on king block
            if block.block_type == KING_2x2:
                center_x = x + width // 2
                center_y = y + height // 2
                # Simple crown shape
                points = [
                    (center_x - 12, center_y + 5),
                    (center_x - 8, center_y - 5),
                    (center_x - 4, center_y),
                    (center_x, center_y - 10),
                    (center_x + 4, center_y),
                    (center_x + 8, center_y - 5),
                    (center_x + 12, center_y + 5),
                ]
                pygame.draw.polygon(self.screen, (255, 255, 255), points)

    def draw(self):
        """Draw everything."""
        self.screen.fill(COLOR_BG)

        # Draw title
        title = self.font_large.render("KLOTSKI", True, COLOR_HIGHLIGHT)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

        # Draw grid and blocks
        self._draw_grid()
        self._draw_blocks()

        # Draw panel
        panel_y = GRID_OFFSET_Y + GRID_ROWS * CELL_SIZE + 30

        # Draw stats
        moves_text = self.font_medium.render(f"MOVES: {self.moves}", True, COLOR_TEXT)
        self.screen.blit(moves_text, (GRID_OFFSET_X, panel_y))

        # Draw controls
        controls = [
            "CLICK: Select block",
            "ARROWS: Move selected",
            "R: Reset | E: Easy mode",
        ]
        for i, text in enumerate(controls):
            control_surf = self.font_small.render(text, True, (150, 150, 170))
            self.screen.blit(control_surf, (GRID_OFFSET_X + GRID_COLS * CELL_SIZE + 30,
                                         GRID_OFFSET_Y + 100 + i * 25))

        # Draw goal indicator
        goal_text = self.font_small.render("GOAL: Red block to exit", True, COLOR_KING_BLOCK)
        self.screen.blit(goal_text, (GRID_OFFSET_X + GRID_COLS * CELL_SIZE + 30,
                                     GRID_OFFSET_Y + 180))

        # Draw game won message
        if self.game_won:
            score = max(1, 10000 // self.moves)
            win_text = self.font_large.render("ESCAPED!", True, COLOR_HIGHLIGHT)
            score_text = self.font_medium.render(f"Score: {score}", True, COLOR_HIGHLIGHT)
            reset_text = self.font_small.render("Press R to play again", True, COLOR_TEXT)

            self.screen.blit(win_text,
                           (SCREEN_WIDTH // 2 - win_text.get_width() // 2, panel_y))
            self.screen.blit(score_text,
                           (SCREEN_WIDTH // 2 - score_text.get_width() // 2, panel_y + 40))
            self.screen.blit(reset_text,
                           (SCREEN_WIDTH // 2 - reset_text.get_width() // 2, panel_y + 70))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# Alias for consistency
Game = KlotskiGame
