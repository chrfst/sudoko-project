import pygame, sys
from sudoku_generator import SudokuGenerator

# --- CONSTANTS ---
WIDTH = 630
HEIGHT = 700
CELL_SIZE = 70

# Colors
BG_COLOR = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)

# Fonts
TITLE_FONT_SIZE = 70
BUTTON_FONT_SIZE = 30
NUM_FONT_SIZE = 40
GAME_OVER_FONT_SIZE = 60


class Cell:
    def __init__(self, value, row, col, screen):
        self.value = value
        self.row = row
        self.col = col
        self.screen = screen
        self.sketched_value = 0
        self.selected = False

    def set_cell_value(self, value):
        self.value = value

    def set_sketched_value(self, value):
        self.sketched_value = value

    def draw(self):
        x = self.col * CELL_SIZE
        y = self.row * CELL_SIZE

        if self.value != 0:
            # Draw official value (Permanent)
            font = pygame.font.Font(None, NUM_FONT_SIZE)
            text = font.render(str(self.value), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            self.screen.blit(text, text_rect)
        elif self.sketched_value != 0:
            # Draw sketched value (User Draft)
            font = pygame.font.Font(None, NUM_FONT_SIZE)
            text = font.render(str(self.sketched_value), True, BLACK)
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            self.screen.blit(text, text_rect)

        if self.selected:
            pygame.draw.rect(self.screen, RED, (x, y, CELL_SIZE, CELL_SIZE), 3)


class Board:
    def __init__(self, width, height, screen, difficulty):
        self.width = width
        self.height = height
        self.screen = screen
        self.difficulty = difficulty
        self.selected_cell = None

        if self.difficulty == "easy":
            self.removed_cells = 30
        elif self.difficulty == "medium":
            self.removed_cells = 40
        else:
            self.removed_cells = 50

        # --- GENERATION LOGIC ---
        # Ensures valid board is created
        while True:
            self.generator = SudokuGenerator(9, self.removed_cells)
            self.generator.fill_values()

            valid_gen = True
            for row in self.generator.get_board():
                if 0 in row:
                    valid_gen = False
                    break
            if valid_gen:
                break

                # 1. Save the Solution
        self.solution_board = [row[:] for row in self.generator.get_board()]

        # 2. Remove cells to create the puzzle
        self.generator.remove_cells()

        # 3. Create the Puzzle Board (Has 0s and Pre-filled numbers)
        self.puzzle_board = [row[:] for row in self.generator.get_board()]
        self.original_board = [row[:] for row in self.puzzle_board]

        # 4. Initialize Visual Cells
        # Note: If puzzle_board has a number, Cell.value gets that number immediately.
        # This ensures pre-filled numbers are counted as "Values", not "Sketches".
        self.cells = [
            [Cell(self.puzzle_board[r][c], r, c, self.screen) for c in range(9)]
            for r in range(9)
        ]

    def draw(self):
        for i in range(10):
            thick = 4 if i % 3 == 0 else 1
            pygame.draw.line(self.screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thick)
            pygame.draw.line(self.screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, 9 * CELL_SIZE), thick)

        for row in self.cells:
            for cell in row:
                cell.draw()

    def select(self, row, col):
        for r in range(9):
            for c in range(9):
                self.cells[r][c].selected = False
        self.cells[row][col].selected = True
        self.selected_cell = (row, col)

    def click(self, x, y):
        if x <= WIDTH and y <= 9 * CELL_SIZE:
            return y // CELL_SIZE, x // CELL_SIZE
        return None

    def clear(self):
        if self.selected_cell:
            row, col = self.selected_cell
            if self.original_board[row][col] == 0:
                self.cells[row][col].set_cell_value(0)
                self.cells[row][col].set_sketched_value(0)
                self.update_board()

    def sketch(self, value):
        if self.selected_cell:
            row, col = self.selected_cell
            if self.original_board[row][col] == 0:
                self.cells[row][col].set_sketched_value(value)

    def place_number(self, value):
        if self.selected_cell:
            row, col = self.selected_cell
            if self.original_board[row][col] == 0:
                self.cells[row][col].set_cell_value(value)
                self.update_board()

    def reset_to_original(self):
        for r in range(9):
            for c in range(9):
                val = self.original_board[r][c]
                self.cells[r][c].set_cell_value(val)
                self.cells[r][c].set_sketched_value(0)
        self.update_board()

    def update_board(self):
        # Syncs visuals to internal data logic
        # This captures both Pre-filled values AND User Filled values
        self.puzzle_board = [[self.cells[r][c].value for c in range(9)] for r in range(9)]

    def is_full(self):
        # Ensure we are looking at the latest data
        self.update_board()

        # Check for empty spots (0s)
        for row in self.puzzle_board:
            for val in row:
                if val == 0:
                    return False
        return True

    def check_board(self):
        self.update_board()
        for r in range(9):
            for c in range(9):
                # Compare current board vs solution
                if self.puzzle_board[r][c] != self.solution_board[r][c]:
                    return False
        return True


def draw_start_screen(screen):
    screen.fill(BG_COLOR)
    title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
    title_surface = title_font.render("Welcome to Sudoku", True, BLACK)
    screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 100))

    subtitle_font = pygame.font.Font(None, NUM_FONT_SIZE)
    subtitle_surface = subtitle_font.render("Select Game Mode:", True, BLACK)
    screen.blit(subtitle_surface, (WIDTH // 2 - subtitle_surface.get_width() // 2, 300))

    button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)

    easy_text = button_font.render("EASY", True, WHITE)
    easy_surface = pygame.Surface((120, 50))
    easy_surface.fill(ORANGE)
    easy_rect = easy_surface.get_rect(center=(WIDTH // 2 - 150, 450))
    easy_surface.blit(easy_text, (60 - easy_text.get_width() // 2, 25 - easy_text.get_height() // 2))
    screen.blit(easy_surface, easy_rect)

    medium_text = button_font.render("MEDIUM", True, WHITE)
    medium_surface = pygame.Surface((120, 50))
    medium_surface.fill(ORANGE)
    medium_rect = medium_surface.get_rect(center=(WIDTH // 2, 450))
    medium_surface.blit(medium_text, (60 - medium_text.get_width() // 2, 25 - medium_text.get_height() // 2))
    screen.blit(medium_surface, medium_rect)

    hard_text = button_font.render("HARD", True, WHITE)
    hard_surface = pygame.Surface((120, 50))
    hard_surface.fill(ORANGE)
    hard_rect = hard_surface.get_rect(center=(WIDTH // 2 + 150, 450))
    hard_surface.blit(hard_text, (60 - hard_text.get_width() // 2, 25 - hard_text.get_height() // 2))
    screen.blit(hard_surface, hard_rect)

    return easy_rect, medium_rect, hard_rect


def draw_game_over(screen):
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
    text = font.render("Game Over :(", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))

    button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)
    restart_text = button_font.render("RESTART", True, WHITE)
    restart_surface = pygame.Surface((120, 50))
    restart_surface.fill(ORANGE)
    restart_rect = restart_surface.get_rect(center=(WIDTH // 2, 400))
    restart_surface.blit(restart_text, (60 - restart_text.get_width() // 2, 25 - restart_text.get_height() // 2))
    screen.blit(restart_surface, restart_rect)
    return restart_rect


def draw_game_won(screen):
    screen.fill(BG_COLOR)
    font = pygame.font.Font(None, GAME_OVER_FONT_SIZE)
    text = font.render("Game Won!", True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 200))

    button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)
    exit_text = button_font.render("EXIT", True, WHITE)
    exit_surface = pygame.Surface((120, 50))
    exit_surface.fill(ORANGE)
    exit_rect = exit_surface.get_rect(center=(WIDTH // 2, 400))
    exit_surface.blit(exit_text, (60 - exit_text.get_width() // 2, 25 - exit_text.get_height() // 2))
    screen.blit(exit_surface, exit_rect)
    return exit_rect


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sudoku")

    game_state = "START"
    difficulty = None
    board = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "START":
                    easy_rect, medium_rect, hard_rect = draw_start_screen(screen)
                    x, y = event.pos
                    if easy_rect.collidepoint(x, y):
                        difficulty = "easy"
                        game_state = "GAME"
                        board = Board(WIDTH, HEIGHT, screen, difficulty)
                    elif medium_rect.collidepoint(x, y):
                        difficulty = "medium"
                        game_state = "GAME"
                        board = Board(WIDTH, HEIGHT, screen, difficulty)
                    elif hard_rect.collidepoint(x, y):
                        difficulty = "hard"
                        game_state = "GAME"
                        board = Board(WIDTH, HEIGHT, screen, difficulty)

                elif game_state == "GAME":
                    x, y = event.pos
                    clicked_cell = board.click(x, y)
                    if clicked_cell:
                        board.select(clicked_cell[0], clicked_cell[1])

                    reset_rect = pygame.Rect(WIDTH // 4 - 60, HEIGHT - 60, 120, 50)
                    if reset_rect.collidepoint(x, y):
                        board.reset_to_original()
                    restart_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT - 60, 120, 50)
                    if restart_rect.collidepoint(x, y):
                        game_state = "START"
                    exit_rect = pygame.Rect(3 * WIDTH // 4 - 60, HEIGHT - 60, 120, 50)
                    if exit_rect.collidepoint(x, y):
                        running = False
                        sys.exit()

                elif game_state == "LOSE":
                    restart_rect = draw_game_over(screen)
                    x, y = event.pos
                    if restart_rect.collidepoint(x, y):
                        game_state = "START"

                elif game_state == "WIN":
                    exit_rect = draw_game_won(screen)
                    x, y = event.pos
                    if exit_rect.collidepoint(x, y):
                        running = False
                        sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_state == "GAME":
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1: board.sketch(1)
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2: board.sketch(2)
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3: board.sketch(3)
                    if event.key == pygame.K_4 or event.key == pygame.K_KP4: board.sketch(4)
                    if event.key == pygame.K_5 or event.key == pygame.K_KP5: board.sketch(5)
                    if event.key == pygame.K_6 or event.key == pygame.K_KP6: board.sketch(6)
                    if event.key == pygame.K_7 or event.key == pygame.K_KP7: board.sketch(7)
                    if event.key == pygame.K_8 or event.key == pygame.K_KP8: board.sketch(8)
                    if event.key == pygame.K_9 or event.key == pygame.K_KP9: board.sketch(9)

                    if event.key == pygame.K_LEFT and board.selected_cell:
                        r, c = board.selected_cell
                        if c > 0: board.select(r, c - 1)
                    if event.key == pygame.K_RIGHT and board.selected_cell:
                        r, c = board.selected_cell
                        if c < 8: board.select(r, c + 1)
                    if event.key == pygame.K_UP and board.selected_cell:
                        r, c = board.selected_cell
                        if r > 0: board.select(r - 1, c)
                    if event.key == pygame.K_DOWN and board.selected_cell:
                        r, c = board.selected_cell
                        if r < 8: board.select(r + 1, c)

                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        board.clear()

                    # --- ENTER KEY LOGIC ---
                    if event.key == pygame.K_RETURN:
                        # 1. Commit ALL sketched numbers to permanent values
                        # This includes any sketches you made but didn't press enter on individually
                        for r in range(9):
                            for c in range(9):
                                cell = board.cells[r][c]
                                if cell.sketched_value != 0 and cell.value == 0:
                                    cell.value = cell.sketched_value
                                    cell.sketched_value = 0

                        # 2. Update the internal board with the visuals
                        board.update_board()

                        # 3. Check for Win/Loss
                        if board.is_full():
                            if board.check_board():
                                game_state = "WIN"
                            else:
                                game_state = "LOSE"

        if game_state == "START":
            draw_start_screen(screen)

        elif game_state == "GAME":
            screen.fill(BG_COLOR)
            board.draw()

            button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)

            reset_surface = pygame.Surface((120, 50))
            reset_surface.fill(ORANGE)
            reset_text = button_font.render("RESET", True, WHITE)
            reset_surface.blit(reset_text, (60 - reset_text.get_width() // 2, 25 - reset_text.get_height() // 2))
            screen.blit(reset_surface, (WIDTH // 4 - 60, HEIGHT - 60))

            restart_surface = pygame.Surface((120, 50))
            restart_surface.fill(ORANGE)
            restart_text = button_font.render("RESTART", True, WHITE)
            restart_surface.blit(restart_text,
                                 (60 - restart_text.get_width() // 2, 25 - restart_text.get_height() // 2))
            screen.blit(restart_surface, (WIDTH // 2 - 60, HEIGHT - 60))

            exit_surface = pygame.Surface((120, 50))
            exit_surface.fill(ORANGE)
            exit_text = button_font.render("EXIT", True, WHITE)
            exit_surface.blit(exit_text, (60 - exit_text.get_width() // 2, 25 - exit_text.get_height() // 2))
            screen.blit(exit_surface, (3 * WIDTH // 4 - 60, HEIGHT - 60))

        elif game_state == "WIN":
            draw_game_won(screen)

        elif game_state == "LOSE":
            draw_game_over(screen)

        pygame.display.update()


if __name__ == "__main__":
    main()
