import os
import random
import pygame

pygame.init()

WIDTH, HEIGHT = 400, 600
FPS = 60
GROUND_HEIGHT = 100

GRAVITY = 0.45
FLAP_STRENGTH = -7.5
PIPE_WIDTH = 70
PIPE_GAP = 170
PIPE_SPEED = 2.5
PIPE_INTERVAL = 1500

BIRD_X = 90
BEST_SCORE_FILE = "best_score.txt"


def load_best_score():
    if os.path.exists(BEST_SCORE_FILE):
        try:
            with open(BEST_SCORE_FILE, "r") as f:
                return int(f.read().strip())
        except ValueError:
            pass
    return 0


def save_best_score(score):
    with open(BEST_SCORE_FILE, "w") as f:
        f.write(str(score))


class Bird:
    def __init__(self):
        self.x = BIRD_X
        self.y = HEIGHT // 2
        self.radius = 15
        self.velocity = 0
        self.rotation = 0

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rotation = max(-25, min(90, self.velocity * 4))

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 220, 80), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x + 5), int(self.y - 5)), 4)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x + 6), int(self.y - 5)), 2)
        pygame.draw.polygon(
            screen,
            (255, 153, 51),
            [
                (int(self.x + 12), int(self.y)),
                (int(self.x + 22), int(self.y - 4)),
                (int(self.x + 22), int(self.y + 4)),
            ],
        )
        pygame.draw.circle(
            screen,
            (255, 180, 0),
            (int(self.x - 2), int(self.y + 5)),
            self.radius - 6,
        )

    def reset(self):
        self.y = HEIGHT // 2
        self.velocity = 0
        self.rotation = 0


class Pipe:
    def __init__(self):
        self.width = PIPE_WIDTH
        self.x = WIDTH + 50
        self.gap_top = random.randint(120, HEIGHT - GROUND_HEIGHT - 120 - PIPE_GAP)
        self.gap_size = PIPE_GAP
        self.scored = False

    @property
    def gap_bottom(self):
        return self.gap_top + self.gap_size

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        top_height = self.gap_top
        pygame.draw.rect(screen, (50, 170, 60), (self.x, 0, self.width, top_height), 0)
        pygame.draw.rect(screen, (60, 200, 80), (self.x - 5, top_height - 20, self.width + 10, 20), 0)

        bottom_y = self.gap_bottom
        bottom_height = HEIGHT - GROUND_HEIGHT - bottom_y
        pygame.draw.rect(screen, (50, 170, 60), (self.x, bottom_y, self.width, bottom_height), 0)
        pygame.draw.rect(screen, (60, 200, 80), (self.x - 5, bottom_y, self.width + 10, 20), 0)

    def collides_with(self, bird):
        left = self.x
        right = self.x + self.width
        bird_left = bird.x - bird.radius
        bird_right = bird.x + bird.radius
        bird_top = bird.y - bird.radius
        bird_bottom = bird.y + bird.radius

        if bird_right < left or bird_left > right:
            return False

        if bird_top < self.gap_top or bird_bottom > self.gap_bottom:
            return True

        return False


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 28)

        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.best_score = load_best_score()
        self.state = "ready"
        self.last_pipe_time = 0
        self.background_color = (135, 206, 235)

    def reset_game(self):
        self.bird.reset()
        self.pipes = []
        self.score = 0
        self.state = "ready"
        self.last_pipe_time = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_UP):
                    if self.state == "ready":
                        self.state = "playing"
                    elif self.state == "game_over":
                        self.reset_game()
                        self.state = "playing"

                    self.bird.flap()

                if event.key == pygame.K_RETURN and self.state == "game_over":
                    self.reset_game()

        return True

    def spawn_pipe(self):
        self.pipes.append(Pipe())

    def update(self):
        if self.state == "playing":
            self.bird.update()

            now = pygame.time.get_ticks()
            if now - self.last_pipe_time > PIPE_INTERVAL:
                self.spawn_pipe()
                self.last_pipe_time = now

            for pipe in self.pipes:
                pipe.update()

                if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                    pipe.scored = True
                    self.score += 1
                    if self.score > self.best_score:
                        self.best_score = self.score
                        save_best_score(self.best_score)

                if pipe.collides_with(self.bird):
                    self.state = "game_over"

            if self.bird.y + self.bird.radius >= HEIGHT - GROUND_HEIGHT:
                self.state = "game_over"

            if self.bird.y - self.bird.radius <= 0:
                self.state = "game_over"

            self.pipes = [pipe for pipe in self.pipes if pipe.x + pipe.width > -10]

    def draw(self):
        self.screen.fill(self.background_color)

        pygame.draw.circle(self.screen, (255, 232, 120), (330, 70), 28)

        for x in [50, 140, 270, 340]:
            pygame.draw.circle(self.screen, (255, 255, 255), (x, 70), 18)
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 18, 62), 18)
            pygame.draw.circle(self.screen, (255, 255, 255), (x + 36, 70), 18)

        for pipe in self.pipes:
            pipe.draw(self.screen)

        self.bird.draw(self.screen)

        pygame.draw.rect(self.screen, (120, 200, 80), (0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(self.screen, (210, 180, 70), (0, HEIGHT - GROUND_HEIGHT, WIDTH, 10))

        score_text = self.font.render(str(self.score), True, (255, 255, 255))
        self.screen.blit(score_text, (WIDTH // 2 - 12, 30))

        if self.state == "ready":
            ready_text = self.font.render("Ready!", True, (255, 255, 255))
            self.screen.blit(ready_text, (150, 200))

            prompt = self.small_font.render("Press SPACE to start", True, (255, 255, 255))
            self.screen.blit(prompt, (105, 250))

        if self.state == "game_over":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 110))
            self.screen.blit(overlay, (0, 0))

            game_over = self.font.render("Game Over", True, (255, 255, 255))
            self.screen.blit(game_over, (100, 180))

            score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (120, 240))

            best_text = self.font.render(f"Best: {self.best_score}", True, (255, 255, 255))
            self.screen.blit(best_text, (125, 280))

            restart_text = self.small_font.render("Press SPACE or ENTER to restart", True, (255, 255, 255))
            self.screen.blit(restart_text, (75, 330))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()










































































    































































































































































































































































































































file










































































































































































































































































































n








































































































			




























































































































n

















n

















