import pygame
import random
import sys
from multiprocessing import Process, Queue

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH, SCREEN_HEIGHT = 300, 600
GRID_SIZE = 30
BOARD_WIDTH, BOARD_HEIGHT = SCREEN_WIDTH // GRID_SIZE, SCREEN_HEIGHT // GRID_SIZE
WHITE, BLACK, RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, ORANGE = (255, 255, 255), (0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0), (255, 165, 0)

# Define Tetromino shapes
TETROMINOS = {
    'I': [(1, 1, 1, 1)],
    'O': [(1, 1), (1, 1)],
    'T': [(0, 1, 0), (1, 1, 1)],
    'S': [(0, 1, 1), (1, 1, 0)],
    'Z': [(1, 1, 0), (0, 1, 1)],
    'J': [(1, 0, 0), (1, 1, 1)],
    'L': [(0, 0, 1), (1, 1, 1)]
}

# Colors for each Tetromino
TETROMINO_COLORS = {
    'I': CYAN,
    'O': YELLOW,
    'T': MAGENTA,
    'S': GREEN,
    'Z': RED,
    'J': BLUE,
    'L': ORANGE
}

# Create the board
def create_board():
    return [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

# Draw the board and score
def draw_board(screen, board, piece=None, offset=(0, 0), piece_color=None, score=0, high_score=0):
    screen.fill(BLACK)
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if board[y][x] != 0:
                pygame.draw.rect(screen, board[y][x], (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    if piece:
        px, py = offset
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, piece_color, ((px + x) * GRID_SIZE, (py + y) * GRID_SIZE, GRID_SIZE, GRID_SIZE))
    # Draw the score
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (10, 50))
    pygame.display.flip()

# Check if a position is valid for a piece
def is_valid_position(board, piece, offset):
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                bx, by = px + x, py + y
                if bx < 0 or bx >= BOARD_WIDTH or by >= BOARD_HEIGHT or (by >= 0 and board[by][bx]):
                    return False
    return True

# Merge the piece into the board
def merge_piece(board, piece, offset, color):
    px, py = offset
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                board[py + y][px + x] = color

# Clear full lines and return the number of lines cleared
def clear_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    lines_cleared = BOARD_HEIGHT - len(new_board)
    new_board = [[0] * BOARD_WIDTH for _ in range(lines_cleared)] + new_board
    return new_board, lines_cleared

# Rotate the piece
def rotate_piece(piece):
    return [list(row) for row in zip(*piece[::-1])]

# Get a new piece
def get_new_piece():
    shape = random.choice(list(TETROMINOS.keys()))
    return TETROMINOS[shape], TETROMINO_COLORS[shape], shape

# Reset the game
def reset_game():
    board = create_board()
    piece, color, piece_type = get_new_piece()
    piece_x, piece_y = BOARD_WIDTH // 2 - len(piece[0]) // 2, 0
    return board, piece, color, piece_type, piece_x, piece_y, 0

# Evaluate board using heuristics
def evaluate_board(board):
    lines_cleared, holes, height = 0, 0, 0
    for y in range(BOARD_HEIGHT):
        if all(board[y]):
            lines_cleared += 1
    for x in range(BOARD_WIDTH):
        column_holes, column_height = 0, 0
        block_found = False
        for y in range(BOARD_HEIGHT):
            if board[y][x]:
                block_found = True
                column_height = BOARD_HEIGHT - y
            elif block_found:
                column_holes += 1
        holes += column_holes
        height = max(height, column_height)
    return lines_cleared * 10 - holes * 1 - height * 0.5

# Get the best move for the AI
def get_best_move(board, piece, piece_color, queue):
    best_score, best_move = -float('inf'), None
    for rotation in range(4):
        rotated_piece = piece
        for _ in range(rotation):
            rotated_piece = rotate_piece(rotated_piece)
        for x in range(BOARD_WIDTH - len(rotated_piece[0]) + 1):
            y = 0
            while is_valid_position(board, rotated_piece, (x, y)):
                y += 1
            y -= 1
            if y < 0:
                continue
            temp_board = [row[:] for row in board]
            merge_piece(temp_board, rotated_piece, (x, y), piece_color)
            temp_board, lines_cleared = clear_lines(temp_board)
            score = evaluate_board(temp_board)
            if score > best_score:
                best_score = score
                best_move = (rotated_piece, x, y)
    queue.put(best_move)

# Main game loop
def game_loop(window_id):
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"Tetris - Window {window_id}")
    
    board, piece, color, piece_type, piece_x, piece_y, score = reset_game()
    high_score = 0
    falling_speed = 500
    last_fall_time = pygame.time.get_ticks()

    queue = Queue()
    best_move_process = None

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        if current_time - last_fall_time >= falling_speed:
            piece_y += 1
            if not is_valid_position(board, piece, (piece_x, piece_y)):
                piece_y -= 1
                merge_piece(board, piece, (piece_x, piece_y), color)
                board, lines_cleared = clear_lines(board)
                score += lines_cleared * 100  # Update score based on lines cleared
                if score > high_score:
                    high_score = score  # Update high score if current score is higher
                piece, color, piece_type = get_new_piece()
                piece_x, piece_y = BOARD_WIDTH // 2 - len(piece[0]) // 2, 0
                if not is_valid_position(board, piece, (piece_x, piece_y)):
                    board, piece, color, piece_type, piece_x, piece_y, score = reset_game()
            last_fall_time = current_time

            # AI makes a move
            if best_move_process is None or not best_move_process.is_alive():
                if not queue.empty():
                    best_move = queue.get()
                    if best_move:
                        piece, piece_x, piece_y = best_move

                best_move_process = Process(target=get_best_move, args=(board, piece, color, queue))
                best_move_process.start()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if is_valid_position(board, piece, (piece_x - 1, piece_y)):
                        piece_x -= 1
                elif event.key == pygame.K_RIGHT:
                    if is_valid_position(board, piece, (piece_x + 1, piece_y)):
                        piece_x += 1
                elif event.key == pygame.K_DOWN:
                    if is_valid_position(board, piece, (piece_x, piece_y + 1)):
                        piece_y += 1
                elif event.key == pygame.K_UP:
                    rotated_piece = rotate_piece(piece)
                    if is_valid_position(board, rotated_piece, (piece_x, piece_y)):
                        piece = rotated_piece

        draw_board(screen, board, piece, (piece_x, piece_y), color, score, high_score)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    processes = []
    for i in range(4):
        p = Process(target=game_loop, args=(i + 1,))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()
