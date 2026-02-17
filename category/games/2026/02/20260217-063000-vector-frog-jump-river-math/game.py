import pygame
import random
import sys
from config import *
from entities import Frog, LilyPad, MathProblem

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Frog Jump River Math")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.reset()

    def reset(self):
        self.frog = Frog()
        self.math_problem = MathProblem()
        self.lily_pads = []
        self.score = 0
        self.game_over = False
        self.won = False
        self.difficulty_level = 0
        self.successful_jumps = 0
        self.generate_lily_pads()

    def generate_lily_pads(self):
        self.lily_pads = []
        for row in range(1, GRID_ROWS - 1):
            speed = BASE_LILY_SPEED + (self.difficulty_level * SPEED_INCREMENT)
            if row % 2 == 0:
                speed = -speed

            num_pads = random.randint(2, 4)
            spacing = SCREEN_WIDTH // num_pads

            correct_pad_index = random.randint(0, num_pads - 1)

            for i in range(num_pads):
                x = i * spacing + random.randint(0, spacing // 2)
                is_correct = (i == correct_pad_index)

                if is_correct:
                    value = self.math_problem.answer
                else:
                    wrong_answer = self.math_problem.answer + random.randint(-5, 5)
                    while wrong_answer == self.math_problem.answer or wrong_answer < 0:
                        wrong_answer = self.math_problem.answer + random.randint(-5, 5)
                    value = wrong_answer

                self.lily_pads.append(LilyPad(x, row, speed, value, is_correct))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE:
                        self.reset()
                else:
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    elif event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1

                    if dx != 0 or dy != 0:
                        old_y = self.frog.grid_y
                        if self.frog.move(dx, dy):
                            if self.frog.grid_y != old_y and self.frog.grid_y == 0:
                                self.won = True
                                self.score += POINTS_GOAL
                            self.check_collision()
        return True

    def check_collision(self):
        frog_x, frog_y = self.frog.get_pos()
        frog_rect = pygame.Rect(frog_x - 15, frog_y - 15, 30, 30)

        self.frog.on_lily_pad = None

        for pad in self.lily_pads:
            pad_rect = pygame.Rect(pad.get_rect())
            if frog_rect.colliderect(pad_rect):
                self.frog.on_lily_pad = pad

                if pad.is_correct:
                    self.score += POINTS_CORRECT_JUMP
                    self.successful_jumps += 1

                    if self.successful_jumps % DIFFICULTY_JUMP_THRESHOLD == 0:
                        self.difficulty_level += 1
                        self.math_problem.increase_difficulty()

                    self.generate_lily_pads()
                else:
                    self.frog.sink()
                    self.game_over = True
                return

        if self.frog.grid_y not in [0, GRID_ROWS - 1]:
            self.frog.sink()
            self.game_over = True

    def update(self):
        if not self.game_over and not self.won:
            for pad in self.lily_pads:
                pad.update()

            if self.frog.on_lily_pad:
                frog_x, frog_y = self.frog.get_pos()
                if frog_x < -GRID_SIZE or frog_x > SCREEN_WIDTH + GRID_SIZE:
                    self.game_over = True
                    self.frog.alive = False

    def draw(self):
        self.screen.fill(COLOR_WATER)

        for row in range(GRID_ROWS):
            if row == 0:
                y = row * GRID_SIZE
                pygame.draw.rect(self.screen, (40, 140, 220), (0, y, SCREEN_WIDTH, GRID_SIZE))
                goal_text = self.font_large.render("GOAL", True, COLOR_TEXT)
                goal_rect = goal_text.get_rect(center=(SCREEN_WIDTH // 2, y + GRID_SIZE // 2))
                self.screen.blit(goal_text, goal_rect)
            elif row == GRID_ROWS - 1:
                y = row * GRID_SIZE
                pygame.draw.rect(self.screen, (34, 139, 34), (0, y, SCREEN_WIDTH, GRID_SIZE))
                start_text = self.font_large.render("START", True, COLOR_TEXT)
                start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, y + GRID_SIZE // 2))
                self.screen.blit(start_text, start_rect)

        for pad in self.lily_pads:
            pad.draw(self.screen, self.font_medium)

        self.frog.draw(self.screen)

        problem_text = self.font_large.render(str(self.math_problem), True, COLOR_TEXT)
        problem_rect = problem_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(self.screen, (0, 0, 0, 128), (problem_rect.x - 20, problem_rect.y - 10, problem_rect.width + 40, problem_rect.height + 20))
        self.screen.blit(problem_text, problem_rect)

        score_text = self.font_small.render(f"Score: {self.score}", True, COLOR_SCORE)
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font_large.render("GAME OVER", True, COLOR_GAME_OVER)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(game_over_text, game_over_rect)

            score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(score_text, score_rect)

            restart_text = self.font_small.render("Press SPACE to restart", True, COLOR_TEXT)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)

        elif self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            win_text = self.font_large.render("YOU REACHED THE GOAL!", True, (100, 255, 100))
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(win_text, win_rect)

            score_text = self.font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            self.screen.blit(score_text, score_rect)

            continue_text = self.font_small.render("Press SPACE to play again", True, COLOR_TEXT)
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.screen.blit(continue_text, continue_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()
