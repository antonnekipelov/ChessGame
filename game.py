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
        self.move_history = []
        self.font = pygame.font.SysFont('Arial', 16)
        self.title_font = pygame.font.SysFont('Arial', 20)
        self.scroll_y = 0
        self.scroll_bar_rect = None
        self.scroll_bar_dragging = False
        self.scroll_bar_hovered = False
    
    def load_pieces(self):
        pieces = {}
        colors = ['w', 'b']
        piece_names = ['p', 'R', 'N', 'B', 'Q', 'K']
        
        for color in colors:
            for name in piece_names:
                key = color + name
                try:
                    image = pygame.image.load(f'assets/{key}.png')
                    pieces[key] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
                except Exception as e:
                    print(f"Не удалось загрузить изображение для {key}: {e}")
                    surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    
                    if name == 'p':
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                    elif name == 'R':
                        pygame.draw.rect(surf, WHITE if color == 'w' else BLACK,
                                        (SQUARE_SIZE//4, SQUARE_SIZE//4, 
                                        SQUARE_SIZE//2, SQUARE_SIZE//2))
                    elif name == 'N':
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE//2),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE//2)])
                    elif name == 'B':
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE*3//4)])
                    elif name == 'Q':
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE//2),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE//2)])
                    elif name == 'K':
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
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT)
                self.screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                for move in self.valid_moves:
                    if move.start_row == row and move.start_col == col:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        s.fill(MOVE_HIGHLIGHT)
                        self.screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
    
    def draw_move_history(self):
        history_panel_width = INFO_WIDTH - SCROLL_BAR_WIDTH
        pygame.draw.rect(self.screen, INFO_BG, (BOARD_WIDTH, 0, INFO_WIDTH, HEIGHT))
        
        # Заголовок
        title = self.title_font.render("История ходов", True, TEXT_COLOR)
        self.screen.blit(title, (BOARD_WIDTH + 10, 10))
        
        # Область для текста истории с маской
        history_surface = pygame.Surface((history_panel_width - 20, HEIGHT - 50), pygame.SRCALPHA)
        history_surface.fill((240, 240, 240, 0))
        
        # Рендерим все ходы
        y_offset = 0
        for i, move in enumerate(self.move_history):
            text = self.font.render(move, True, TEXT_COLOR)
            history_surface.blit(text, (0, y_offset - self.scroll_y))
            y_offset += 20
        
        # Применяем маску
        mask = pygame.Surface((history_panel_width - 20, HEIGHT - 50), pygame.SRCALPHA)
        mask.fill((240, 240, 240, 255))
        history_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Отображаем область с историей
        self.screen.blit(history_surface, (BOARD_WIDTH + 10, 50))
        
        # Полоса прокрутки
        total_content_height = len(self.move_history) * 20
        visible_height = HEIGHT - 50
        if total_content_height > visible_height:
            # Рассчитываем размер и положение полосы прокрутки
            scrollbar_height = max(30, visible_height * visible_height / total_content_height)
            scrollbar_pos = (self.scroll_y / total_content_height) * (visible_height - scrollbar_height)
            
            scroll_bar_x = BOARD_WIDTH + INFO_WIDTH - SCROLL_BAR_WIDTH + 2
            self.scroll_bar_rect = pygame.Rect(
                scroll_bar_x, 
                50 + scrollbar_pos, 
                SCROLL_BAR_WIDTH - 4, 
                scrollbar_height
            )
            
            # Рисуем полосу прокрутки
            color = SCROLL_BAR_HOVER_COLOR if self.scroll_bar_hovered or self.scroll_bar_dragging else SCROLL_BAR_COLOR
            pygame.draw.rect(self.screen, color, self.scroll_bar_rect, border_radius=5)
    
    def handle_scroll(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Прокрутка вверх
                self.scroll_y = max(0, self.scroll_y - 20)
            elif event.button == 5:  # Прокрутка вниз
                total_content_height = len(self.move_history) * 20
                visible_height = HEIGHT - 50
                self.scroll_y = min(total_content_height - visible_height, self.scroll_y + 20)
            elif event.button == 1 and self.scroll_bar_rect and self.scroll_bar_rect.collidepoint(event.pos):
                self.scroll_bar_dragging = True
                self.drag_start_y = event.pos[1]
                self.drag_start_scroll = self.scroll_y
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.scroll_bar_dragging = False
        
        elif event.type == pygame.MOUSEMOTION:
            # Проверка наведения на полосу прокрутки
            if self.scroll_bar_rect:
                self.scroll_bar_hovered = self.scroll_bar_rect.collidepoint(event.pos)
            
            # Перетаскивание полосы прокрутки
            if self.scroll_bar_dragging:
                total_content_height = len(self.move_history) * 20
                visible_height = HEIGHT - 50
                delta_y = event.pos[1] - self.drag_start_y
                scroll_delta = delta_y * (total_content_height / visible_height)
                self.scroll_y = max(0, min(total_content_height - visible_height, self.drag_start_scroll + scroll_delta))
    
    def draw_game_state(self):
        self.draw_board()
        self.draw_highlights()
        self.draw_pieces()
        self.draw_move_history()
        
        if self.board.checkmate:
            font = pygame.font.SysFont('Arial', 32)
            if self.board.white_to_move:
                text = font.render('Черные выиграли! Мат!', True, RED)
            else:
                text = font.render('Белые выиграли! Мат!', True, RED)
            self.screen.blit(text, (BOARD_WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            self.game_over = True
        elif self.board.stalemate:
            font = pygame.font.SysFont('Arial', 32)
            text = font.render('Пат! Ничья!', True, RED)
            self.screen.blit(text, (BOARD_WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            self.game_over = True
    
    def handle_click(self, row, col):
        if self.game_over:
            return
        
        if self.selected_square == (row, col):
            self.selected_square = ()
            self.player_clicks = []
        else:
            self.selected_square = (row, col)
            self.player_clicks.append(self.selected_square)
        
        if len(self.player_clicks) == 2:
            move = Move(self.player_clicks[0], self.player_clicks[1], self.board.board)
            
            for valid_move in self.valid_moves:
                if move == valid_move:
                    self.board.make_move(valid_move)
                    move_notation = valid_move.get_chess_notation()
                    
                    # Добавляем обозначение шаха или мата
                    if self.board.checkmate:
                        move_notation += '#'
                        # Добавляем сообщение о победе
                        winner = 'Белые' if not self.board.white_to_move else 'Черные'
                        self.move_history.append(f"{winner} выиграли: Мат!")
                    elif self.board.in_check():
                        move_notation += '+'
                    
                    # Форматируем историю ходов
                    if self.board.white_to_move:  # Черные только что сходили
                        if not self.move_history or len(self.move_history[-1].split()) >= 3:
                            self.move_history.append(f"{len(self.move_history)+1}. {move_notation}")
                        else:
                            self.move_history[-1] += f" {move_notation}"
                    else:  # Белые только что сходили
                        if self.move_history and len(self.move_history[-1].split()) < 3:
                            self.move_history[-1] += f" {move_notation}"
                        else:
                            self.move_history.append(f"{len(self.move_history)+1}... {move_notation}")
                    
                    self.selected_square = ()
                    self.player_clicks = []
                    self.valid_moves = []
                    return
            
            self.player_clicks = [self.selected_square]
        
        if len(self.player_clicks) == 1:
            self.valid_moves = []
            row, col = self.player_clicks[0]
            piece = self.board.board[row][col]
            if piece != '--' and piece[0] == ('w' if self.board.white_to_move else 'b'):
                for move in self.board.get_valid_moves():
                    if move.start_row == row and move.start_col == col:
                        self.valid_moves.append(move)