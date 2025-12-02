import pygame
pygame.init()
# sudoku = SudokuGenerator(9, 40)  # 40 cells removed
# sudoku.fill_values()
# board = sudoku.get_board()
class Cell:
    def __init__(self, row, col, width, height, number = 0):
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.color = "beige"
        self.number = number
        self.rect = pygame.Rect(col * width, row * height, width, height)
        self.font = pygame.font.SysFont(None, 40)
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, width = 1)
        if self.number != 0:
            text = self.font.render(str(self.number), True, "black")
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
    def draw_outline(self, screen, color="red"):
        pygame.draw.rect(screen, color, self.rect, width = 2)
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
screen = pygame.display.set_mode((800, 800), pygame.RESIZABLE)
running = True
grid = []
swidth, sheight = screen.get_size()
cell_w = swidth / 9
cell_h = sheight / 9
for row in range(9):
    grid_row = []
    for col in range(9):
        grid_row.append(Cell(row, col, cell_w, cell_h, board[row][col]))
    grid.append(grid_row)
selected_cell = None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            for row in grid:
                for cell in row:
                    if cell.is_clicked((mx, my)):
                        selected_cell = cell
                        selected_row, selected_col = cell.row, cell.col
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                selected_row = min(8, selected_row + 1)
            elif event.key == pygame.K_UP:
                selected_row = max(0, selected_row - 1)
            elif event.key == pygame.K_LEFT:
                selected_col = max(0, selected_col - 1)
            elif event.key == pygame.K_RIGHT:
                selected_col = min(8, selected_col + 1)
            selected_cell = grid[selected_row][selected_col]
    swidth, sheight = screen.get_size()
    cell_w = swidth / 9
    cell_h = sheight / 9
    for row in grid:
        for cell in row:
            cell.width = cell_w
            cell.height = cell_h
            cell.rect = pygame.Rect(cell.col * cell_w, cell.row * cell_h, cell_w, cell_h)
    screen.fill("beige")
    for row in grid:
        for cell in row:
            cell.draw(screen)
    for i in range(10):
        width = 2 if i % 3 == 0 else 1
        pygame.draw.line(screen, "black", (i*cell_w, 0), (i*cell_w, sheight), width=width)
        pygame.draw.line(screen, "black", (0, i*cell_h), (swidth, i*cell_h), width=width)
    if selected_cell:
        selected_cell.draw_outline(screen)
    pygame.display.flip()
pygame.quit()
