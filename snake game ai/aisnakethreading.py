import pygame
import random
import time
from multiprocessing import Process

# Initialize Pygame
pygame.init()

# Window dimensions
width, height = 800, 600
snake_block = 10
snake_speed = 10000

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
blue = (50, 153, 213)

# Font settings
font_style = pygame.font.SysFont(None, 50)
score_font = pygame.font.SysFont(None, 35)

def Your_score(window, score, high_score):
    score_value = score_font.render(f"Score: {score}", True, white)
    window.blit(score_value, [10, 10])
    high_score_value = score_font.render(f"High Score: {high_score}", True, white)
    window.blit(high_score_value, [width - high_score_value.get_width() - 10, 10])

def distance(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)

def ai_move(snake_Head, foodx, foody, x1_change, y1_change):
    directions = [(0, snake_block), (0, -snake_block), (snake_block, 0), (-snake_block, 0)]
    min_dist = float('inf')
    best_move = (x1_change, y1_change)
    
    for direction in directions:
        new_x = snake_Head[0] + direction[0]
        new_y = snake_Head[1] + direction[1]
        dist = distance(new_x, new_y, foodx, foody)
        
        if new_x < 0 or new_x >= width or new_y < 0 or new_y >= height:
            continue
        
        if direction[0] == -x1_change and direction[1] == -y1_change:
            continue
        
        if dist < min_dist:
            min_dist = dist
            best_move = direction
    
    return best_move

def display_message(window, message, color, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        window.fill(blue)
        rendered_message = font_style.render(message, True, color)
        window.blit(rendered_message, [width / 6, height / 3])
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

def gameLoop(window):
    clock = pygame.time.Clock()
    high_score = 0
    
    while True:
        game_over = False
        
        # Initialize game state
        x1 = width / 2
        y1 = height / 2
        x1_change = 0
        y1_change = 0
        snake_List = []
        Length_of_snake = 1
        score = 0
        
        # Randomly initialize food position
        foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
        foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0

        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            x1_change, y1_change = ai_move([x1, y1], foodx, foody, x1_change, y1_change)

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

            Your_score(window, score, high_score)
            pygame.display.update()

            if x1 == foodx and y1 == foody:
                foodx = round(random.randrange(0, width - snake_block) / 10.0) * 10.0
                foody = round(random.randrange(0, height - snake_block) / 10.0) * 10.0
                Length_of_snake += 1
                score += 1

            clock.tick(snake_speed)

        # Update high score
        if score > high_score:
            high_score = score

        # Game over handling
        display_message(window, f"Your Score: {score}", white, 0)

def run_game(window_id):
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption(f'Snake Game - Window {window_id}')
    gameLoop(window)

def main():
    processes = []
    for i in range(10):
        process = Process(target=run_game, args=(i + 1,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

if __name__ == "__main__":
    main()
