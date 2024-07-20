import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dino Game")

# Load assets
dino_image = pygame.Surface((50, 50))
dino_image.fill(BLACK)
obstacle_image = pygame.Surface((20, 50))
obstacle_image.fill(GRAY)

# Dinosaur class
class Dinosaur:
    def __init__(self):
        self.image = dino_image
        self.rect = self.image.get_rect()
        self.rect.x = 50
        self.rect.y = SCREEN_HEIGHT - 100
        self.is_jumping = False
        self.jump_velocity = 25  # Increased jump velocity
        self.gravity = 1

    def update(self):
        if self.is_jumping:
            self.rect.y -= self.jump_velocity
            self.jump_velocity -= self.gravity
            if self.jump_velocity < -25:  # Adjust to match the new jump velocity
                self.is_jumping = False
                self.jump_velocity = 25
        if self.rect.y >= SCREEN_HEIGHT - 100:
            self.rect.y = SCREEN_HEIGHT - 100

    def draw(self):
        screen.blit(self.image, self.rect)

# Obstacle class
class Obstacle:
    def __init__(self, x_position):
        self.image = obstacle_image
        self.rect = self.image.get_rect()
        self.rect.x = x_position
        self.rect.y = SCREEN_HEIGHT - 100

    def update(self):
        self.rect.x -= 5
        if self.rect.x < -20:
            self.rect.x = SCREEN_WIDTH
            self.rect.y = SCREEN_HEIGHT - 100

    def draw(self):
        screen.blit(self.image, self.rect)

def game_loop():
    clock = pygame.time.Clock()

    def reset_game():
        return Dinosaur(), [], 0

    def show_game_over():
        font = pygame.font.SysFont(None, 72)
        text = font.render("Game Over", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(text, text_rect)
        pygame.display.flip()

    dino, obstacles, score = reset_game()

    last_obstacle_time = pygame.time.get_ticks()
    min_obstacle_interval = 2000  # Minimum interval between obstacles in milliseconds (2 seconds)

    running = True
    game_over = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if game_over:
                    dino, obstacles, score = reset_game()
                    last_obstacle_time = pygame.time.get_ticks()
                    game_over = False
                elif event.key == pygame.K_SPACE and not dino.is_jumping:
                    dino.is_jumping = True

        if not game_over:
            # Update game objects
            dino.update()
            for obstacle in obstacles:
                obstacle.update()
                if dino.rect.colliderect(obstacle.rect):
                    game_over = True

            # Check if it's time to add a new obstacle
            current_time = pygame.time.get_ticks()
            if current_time - last_obstacle_time > min_obstacle_interval:
                # Add a new obstacle at a random position
                x_position = SCREEN_WIDTH + random.randint(200, 800)  # Ensures some variety in spacing
                obstacles.append(Obstacle(x_position))
                last_obstacle_time = current_time

            # Remove obstacles that are off-screen
            obstacles = [obstacle for obstacle in obstacles if obstacle.rect.x > -20]

            # Draw everything
            screen.fill(WHITE)
            dino.draw()
            for obstacle in obstacles:
                obstacle.draw()

            # Display the score
            score += 0.5
            font = pygame.font.SysFont(None, 36)
            text = font.render(f'Score: {int(score)}', True, BLACK)
            screen.blit(text, (10, 10))

        else:
            show_game_over()

        # Refresh the screen
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# Start the game
game_loop()
