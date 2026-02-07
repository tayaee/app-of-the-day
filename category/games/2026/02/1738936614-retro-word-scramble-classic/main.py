import random
import sys
from dataclasses import dataclass
from typing import List

try:
    import pygame
except ImportError:
    print("pygame is required. Install with: pip install pygame")
    sys.exit(1)


@dataclass
class GameState:
    score: int = 0
    lives: int = 3
    current_word: str = ""
    scrambled_word: str = ""
    user_input: str = ""
    hint_used: bool = False
    game_over: bool = False
    message: str = ""
    message_timer: int = 0


class WordScrambleGame:
    WORD_LIST = [
        "APPLE", "BANANA", "CHERRY", "DRAGON", "ELEPHANT",
        "FLOWER", "GUITAR", "HOUSE", "ISLAND", "JUNGLE",
        "KITCHEN", "LEMON", "MONKEY", "NATURE", "ORANGE",
        "PIANO", "QUEEN", "RIVER", "SNAKE", "TIGER",
        "UMBRELLA", "VILLAGE", "WATER", "XYLOPHONE", "YELLOW",
        "ZEBRA", "CASTLE", "DESERT", "FOREST", "GARDEN",
        "PLANET", "ROBOT", "SUMMER", "WINTER", "SPRING",
        "AUTUMN", "BRIDGE", "CLOUDY", "DREAMS", "EAGLES",
        "FAMILY", "GOLDEN", "HAPPY", "ISLANDS", "JOURNEY"
    ]

    COLORS = {
        "background": (30, 30, 40),
        "text": (240, 240, 240),
        "accent": (100, 200, 150),
        "hint": (200, 150, 100),
        "error": (220, 80, 80),
        "success": (80, 200, 120),
        "button": (70, 70, 90),
        "button_hover": (90, 90, 110)
    }

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Retro Word Scramble Classic")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        self.state = GameState()
        self.pick_new_word()

    def scramble_word(self, word: str) -> str:
        letters = list(word)
        while True:
            random.shuffle(letters)
            scrambled = "".join(letters)
            if scrambled != word:
                return scrambled

    def pick_new_word(self):
        self.state.current_word = random.choice(self.WORD_LIST)
        self.state.scrambled_word = self.scramble_word(self.state.current_word)
        self.state.user_input = ""
        self.state.hint_used = False

    def get_hint(self) -> str:
        hint = self.state.current_word[:len(self.state.user_input) + 1]
        return hint

    def show_message(self, text: str):
        self.state.message = text
        self.state.message_timer = 120

    def check_answer(self):
        if not self.state.user_input:
            return

        if self.state.user_input == self.state.current_word:
            points = len(self.state.current_word) * 10
            if self.state.hint_used:
                points //= 2
            self.state.score += points
            self.show_message(f"Correct! +{points} points")
            self.pick_new_word()
        else:
            self.state.lives -= 1
            self.show_message(f"Wrong! Lives: {self.state.lives}")
            if self.state.lives <= 0:
                self.state.game_over = True
                self.show_message("Game Over!")

    def draw_text_centered(self, text: str, font, y: int, color):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(400, y))
        self.screen.blit(surface, rect)

    def draw_button(self, text: str, rect: tuple, mouse_pos: tuple, clicked: bool) -> bool:
        x, y, w, h = rect
        is_hovered = x <= mouse_pos[0] <= x + w and y <= mouse_pos[1] <= y + h
        color = self.COLORS["button_hover"] if is_hovered else self.COLORS["button"]

        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, self.COLORS["accent"], rect, 2, border_radius=8)

        surface = self.font_small.render(text, True, self.COLORS["text"])
        text_rect = surface.get_rect(center=(x + w // 2, y + h // 2))
        self.screen.blit(surface, text_rect)

        return is_hovered and clicked

    def handle_input(self, event):
        if event.key == pygame.K_ESCAPE:
            return False

        if self.state.game_over:
            if event.key == pygame.K_r:
                self.state = GameState()
                self.pick_new_word()
            return True

        if event.key == pygame.K_BACKSPACE:
            self.state.user_input = self.state.user_input[:-1]
        elif event.key == pygame.K_RETURN:
            self.check_answer()
        elif event.key == pygame.K_TAB and not self.state.hint_used:
            self.state.user_input = self.get_hint()
            self.state.hint_used = True
        elif event.unicode.isalpha() and len(self.state.user_input) < len(self.state.current_word):
            self.state.user_input += event.unicode.upper()

        return True

    def update(self):
        if self.state.message_timer > 0:
            self.state.message_timer -= 1
        else:
            self.state.message = ""

    def draw(self):
        self.screen.fill(self.COLORS["background"])

        mouse_pos = pygame.mouse.get_pos()
        clicked = pygame.mouse.get_pressed()[0]

        if self.state.game_over:
            self.draw_text_centered("GAME OVER", self.font_large, 180, self.COLORS["error"])
            self.draw_text_centered(f"Final Score: {self.state.score}", self.font_medium, 260, self.COLORS["text"])
            self.draw_text_centered(f"The word was: {self.state.current_word}", self.font_medium, 320, self.COLORS["accent"])
            self.draw_text_centered("Press R to restart or ESC to quit", self.font_small, 420, self.COLORS["text"])
        else:
            self.draw_text_centered("WORD SCRAMBLE", self.font_medium, 60, self.COLORS["accent"])

            self.draw_text_centered(f"Score: {self.state.score}", self.font_small, 120, self.COLORS["text"])
            self.draw_text_centered(f"Lives: {self.state.lives}", self.font_small, 150, self.COLORS["text"])

            pygame.draw.rect(self.screen, self.COLORS["accent"], (200, 200, 400, 80), border_radius=10)
            self.draw_text_centered(self.state.scrambled_word, self.font_large, 240, self.COLORS["background"])

            input_color = self.COLORS["text"] if len(self.state.user_input) <= len(self.state.current_word) else self.COLORS["error"]
            pygame.draw.rect(self.screen, self.COLORS["button"], (250, 320, 300, 60), border_radius=8)
            self.draw_text_centered(self.state.user_input + "_", self.font_medium, 350, input_color)

            hint_color = self.COLORS["hint"] if not self.state.hint_used else self.COLORS["text"]
            self.draw_text_centered("[TAB] Hint" + (" (used)" if self.state.hint_used else ""), self.font_small, 400, hint_color)
            self.draw_text_centered("[ENTER] Submit", self.font_small, 440, self.COLORS["text"])

            if self.draw_button("HINT", (650, 400, 120, 50), mouse_pos, clicked) and not self.state.hint_used:
                self.state.user_input = self.get_hint()
                self.state.hint_used = True

            if self.state.message:
                message_color = self.COLORS["success"] if "Correct" in self.state.message else self.COLORS["error"]
                self.draw_text_centered(self.state.message, self.font_small, 520, message_color)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    running = self.handle_input(event)

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


def main():
    game = WordScrambleGame()
    game.run()


if __name__ == "__main__":
    main()
