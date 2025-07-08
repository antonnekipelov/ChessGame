import pygame
from constants import *
from board import ChessBoard
from move import Move


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.board = ChessBoard()
        self.pieces = self.load_pieces()
        self.selected_square = ()
        self.player_clicks = []
        self.valid_moves = []
        self.game_over = False
    
    def load_pieces(self):
        pieces = {}
        colors = ['w', 'b']
        piece_names = ['p', 'R', 'N', 'B', 'Q', 'K']  # p - пешка, r - ладья, n - конь, b - слон, q - ферзь, k - король
        
        for color in colors:
            for name in piece_names:
                key = color + name
                try:
                    # Пытаемся загрузить изображение из папки assets
                    image = pygame.image.load(f'assets/{key}.png')
                    pieces[key] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
                except Exception as e:
                    print(f"Не удалось загрузить изображение для {key}: {e}")
                    # Создаем простую фигуру в качестве запасного варианта
                    surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    
                    # Разные фигуры будем рисовать по-разному
                    if name == 'p':  # Пешка
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                    elif name == 'r':  # Ладья
                        pygame.draw.rect(surf, WHITE if color == 'w' else BLACK,
                                        (SQUARE_SIZE//4, SQUARE_SIZE//4, 
                                        SQUARE_SIZE//2, SQUARE_SIZE//2))
                    elif name == 'n':  # Конь
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE//2),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE//2)])
                    elif name == 'b':  # Слон
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE*3//4)])
                    elif name == 'q':  # Ферзь
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE//2),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE//2)])
                    elif name == 'k':  # Король
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                        pygame.draw.rect(surf, WHITE if color == 'w' else BLACK,
                                        (SQUARE_SIZE//2-2, SQUARE_SIZE//4, 
                                        4, SQUARE_SIZE//4))
                    
                    pieces[key] = surf
        
        return pieces
    
    def draw_board(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                pygame.draw.rect(self.screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_pieces(self):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board.board[row][col]
                if piece != '--':
                    self.screen.blit(self.pieces[piece], 
                              (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    def draw_highlights(self):
        if self.selected_square:
            row, col = self.selected_square
            if self.board.board[row][col][0] == ('w' if self.board.white_to_move else 'b'):
                # Подсвечиваем выбранную клетку
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT)
                self.screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                # Подсвечиваем возможные ходы
                for move in self.valid_moves:
                    if move.start_row == row and move.start_col == col:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        s.fill(MOVE_HIGHLIGHT)
                        self.screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
    
    def draw_game_state(self):
        self.draw_board()
        self.draw_highlights()
        self.draw_pieces()
        
        if self.board.checkmate:
            font = pygame.font.SysFont('Arial', 32)
            if self.board.white_to_move:
                text = font.render('Черные выиграли! Мат!', True, RED)
            else:
                text = font.render('Белые выиграли! Мат!', True, RED)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            self.game_over = True
        elif self.board.stalemate:
            font = pygame.font.SysFont('Arial', 32)
            text = font.render('Пат! Ничья!', True, RED)
            self.screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            self.game_over = True
    
    def handle_click(self, row, col):
        if self.game_over:
            return
        
        if self.selected_square == (row, col):  # Отмена выбора
            self.selected_square = ()
            self.player_clicks = []
        else:
            self.selected_square = (row, col)
            self.player_clicks.append(self.selected_square)
        
        if len(self.player_clicks) == 2:  # После второго клика делаем ход
            move = Move(self.player_clicks[0], self.player_clicks[1], self.board.board)
            
            for valid_move in self.valid_moves:
                if move == valid_move:
                    self.board.make_move(valid_move)
                    self.selected_square = ()
                    self.player_clicks = []
                    self.valid_moves = []
                    return
            
            # Если ход недействителен, сбрасываем выбор
            self.player_clicks = [self.selected_square]
        
        # Обновляем список возможных ходов
        if len(self.player_clicks) == 1:
            self.valid_moves = []
            row, col = self.player_clicks[0]
            piece = self.board.board[row][col]
            if piece != '--' and piece[0] == ('w' if self.board.white_to_move else 'b'):
                for move in self.board.get_valid_moves():
                    if move.start_row == row and move.start_col == col:
                        self.valid_moves.append(move)