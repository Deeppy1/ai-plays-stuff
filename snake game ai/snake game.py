import pygame
import random

# Initialize the pygame library
pygame.init()

# Set up display
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Snake Game')

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
blue = (50, 153, 213)

# Clock to control game speed
clock = pygame.time.Clock()
snake_block = 10
snake_speed = 15

font_style = pygame.font.SysFont(None, 50)
score_font = pygame.font.SysFont(None, 35)

def Your_score(score):
    value = score_font.render(f"Score: {score}", True, white)
    window.blit(value, [width - 120, 10])

def gameLoop():
    while True:
        # Initialize game state
        x1 = width / 2
        y1 = height / 2
        x1_change = 0
        y1_change = 0
        snake_List = []
        Length_of_snake = 1
        score = 0
        foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
        foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

        game_over = False

        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        x1_change = -snake_block
                        y1_change = 0
                    elif event.key == pygame.K_RIGHT:
                        x1_change = snake_block
                        y1_change = 0
                    elif event.key == pygame.K_UP:
                        y1_change = -snake_block
                        x1_change = 0
                    elif event.key == pygame.K_DOWN:
                        y1_change = snake_block
                        x1_change = 0

            if x1 >= width or x1 < 0 or y1 >= height or y1 < 0:
                game_over = True

            x1 += x1_change
            y1 += y1_change
            window.fill(blue)
            pygame.draw.rect(window, green, [foodx, foody, snake_block, snake_block])
            snake_Head = [x1, y1]
            snake_List.append(snake_Head)
            if len(snake_List) > Length_of_snake:
                del snake_List[0]

            for segment in snake_List[:-1]:
                if segment == snake_Head:
                    game_over = True
                    break

            for segment in snake_List:
                pygame.draw.rect(window, black, [segment[0], segment[1], snake_block, snake_block])

            Your_score(score)
            pygame.display.update()

            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
                foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
                Length_of_snake += 1
                score += 1

            clock.tick(snake_speed)

        # Game over handling
        while game_over:
            window.fill(blue)
            message = font_style.render("You Lost! Press C-Play Again or Q-Quit", white)
            window.blit(message, [width / 6, height / 3])
            Your_score(score)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        quit()
                    if event.key == pygame.K_c:
                        break  # Exit the game_over loop to restart the game

gameLoop()
