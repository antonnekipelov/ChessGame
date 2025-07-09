# Импорт необходимых модулей
import pygame
from constants import *  # Импорт констант из файла constants.py
from board import ChessBoard  # Импорт класса шахматной доски
from move import Move  # Импорт класса хода

class Game:
    # Конструктор класса, инициализирующий игру
    def __init__(self, screen):
        # Экран для отрисовки
        self.screen = screen
        # Создаем экземпляр шахматной доски
        self.board = ChessBoard()
        # Загружаем изображения шахматных фигур
        self.pieces = self.load_pieces()
        # Выбранная клетка (пока ни одна не выбрана)
        self.selected_square = ()
        # Список кликов игрока (максимум 2 - откуда и куда)
        self.player_clicks = []
        # Список допустимых ходов для выбранной фигуры
        self.valid_moves = []
        # Флаг окончания игры
        self.game_over = False
        # История ходов
        self.move_history = []
        # Шрифт для текста
        self.font = pygame.font.SysFont('Arial', 16)
        # Шрифт для заголовков
        self.title_font = pygame.font.SysFont('Arial', 20)
        # Позиция прокрутки истории ходов
        self.scroll_y = 0
        # Прямоугольник полосы прокрутки
        self.scroll_bar_rect = None
        # Флаг перетаскивания полосы прокрутки
        self.scroll_bar_dragging = False
        # Флаг наведения на полосу прокрутки
        self.scroll_bar_hovered = False
    
    # Метод загрузки изображений шахматных фигур
    def load_pieces(self):
        # Словарь для хранения изображений фигур
        pieces = {}
        # Цвета фигур (белые и черные)
        colors = ['w', 'b']
        # Типы фигур
        piece_names = ['p', 'R', 'N', 'B', 'Q', 'K']
        
        # Перебираем все комбинации цветов и типов фигур
        for color in colors:
            for name in piece_names:
                # Ключ для словаря (например, 'wp' - белая пешка)
                key = color + name
                try:
                    # Пытаемся загрузить изображение из файла
                    image = pygame.image.load(f'assets/{key}.png')
                    # Масштабируем изображение под размер клетки
                    pieces[key] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
                except Exception as e:
                    # Если изображение не найдено, создаем простую графику
                    print(f"Не удалось загрузить изображение для {key}: {e}")
                    # Создаем поверхность с прозрачностью
                    surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    
                    # Рисуем фигуры в зависимости от типа
                    if name == 'p':  # Пешка
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                    elif name == 'R':  # Ладья
                        pygame.draw.rect(surf, WHITE if color == 'w' else BLACK,
                                        (SQUARE_SIZE//4, SQUARE_SIZE//4, 
                                        SQUARE_SIZE//2, SQUARE_SIZE//2))
                    elif name == 'N':  # Конь
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE//2),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE//2)])
                    elif name == 'B':  # Слон
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE*3//4)])
                    elif name == 'Q':  # Ферзь
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                        pygame.draw.polygon(surf, WHITE if color == 'w' else BLACK,
                                        [(SQUARE_SIZE//2, SQUARE_SIZE//4),
                                        (SQUARE_SIZE*3//4, SQUARE_SIZE//2),
                                        (SQUARE_SIZE//2, SQUARE_SIZE*3//4),
                                        (SQUARE_SIZE//4, SQUARE_SIZE//2)])
                    elif name == 'K':  # Король
                        pygame.draw.circle(surf, WHITE if color == 'w' else BLACK, 
                                        (SQUARE_SIZE//2, SQUARE_SIZE//2), SQUARE_SIZE//3)
                        pygame.draw.rect(surf, WHITE if color == 'w' else BLACK,
                                        (SQUARE_SIZE//2-2, SQUARE_SIZE//4, 
                                        4, SQUARE_SIZE//4))
                    
                    # Сохраняем созданное изображение
                    pieces[key] = surf
        
        # Возвращаем словарь с изображениями фигур
        return pieces
    
    # Метод отрисовки шахматной доски
    def draw_board(self):
        # Перебираем все клетки доски
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Определяем цвет клетки (светлая/темная)
                color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
                # Рисуем клетку
                pygame.draw.rect(self.screen, color, 
                               (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Метод отрисовки фигур на доске
    def draw_pieces(self):
        # Перебираем все клетки доски
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                # Получаем фигуру на текущей клетке
                piece = self.board.board[row][col]
                # Если клетка не пустая
                if piece != '--':
                    # Рисуем фигуру на клетке
                    self.screen.blit(self.pieces[piece], 
                                   (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    
    # Метод отрисовки подсветки выбранной клетки и возможных ходов
    def draw_highlights(self):
        # Если есть выбранная клетка
        if self.selected_square:
            row, col = self.selected_square
            # Проверяем, что фигура принадлежит текущему игроку
            if self.board.board[row][col][0] == ('w' if self.board.white_to_move else 'b'):
                # Создаем полупрозрачную поверхность для подсветки
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                s.fill(HIGHLIGHT)
                # Рисуем подсветку на выбранной клетке
                self.screen.blit(s, (col * SQUARE_SIZE, row * SQUARE_SIZE))
                
                # Подсвечиваем все возможные ходы для выбранной фигуры
                for move in self.valid_moves:
                    if move.start_row == row and move.start_col == col:
                        s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        s.fill(MOVE_HIGHLIGHT)
                        self.screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))
    
    # Метод отрисовки истории ходов
    def draw_move_history(self):
        # Ширина панели истории (без полосы прокрутки)
        history_panel_width = INFO_WIDTH - SCROLL_BAR_WIDTH
        # Рисуем фон панели истории
        pygame.draw.rect(self.screen, INFO_BG, (BOARD_WIDTH, 0, INFO_WIDTH, HEIGHT))
        
        # Рисуем заголовок
        title = self.title_font.render("История ходов", True, TEXT_COLOR)
        self.screen.blit(title, (BOARD_WIDTH + 10, 10))
        
        # Создаем поверхность для истории ходов с прозрачностью
        history_surface = pygame.Surface((history_panel_width - 20, HEIGHT - 50), pygame.SRCALPHA)
        history_surface.fill((240, 240, 240, 0))
        
        # Рендерим все ходы с учетом прокрутки
        y_offset = 0
        for i, move in enumerate(self.move_history):
            text = self.font.render(move, True, TEXT_COLOR)
            history_surface.blit(text, (0, y_offset - self.scroll_y))
            y_offset += 20
        
        # Применяем маску для обрезки текста за пределами области
        mask = pygame.Surface((history_panel_width - 20, HEIGHT - 50), pygame.SRCALPHA)
        mask.fill((240, 240, 240, 255))
        history_surface.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Отображаем область с историей
        self.screen.blit(history_surface, (BOARD_WIDTH + 10, 50))
        
        # Рисуем полосу прокрутки, если контент не помещается
        total_content_height = len(self.move_history) * 20
        visible_height = HEIGHT - 50
        if total_content_height > visible_height:
            # Рассчитываем размер и положение полосы прокрутки
            scrollbar_height = max(30, visible_height * visible_height / total_content_height)
            scrollbar_pos = (self.scroll_y / total_content_height) * (visible_height - scrollbar_height)
            
            # Позиция и размер полосы прокрутки
            scroll_bar_x = BOARD_WIDTH + INFO_WIDTH - SCROLL_BAR_WIDTH + 2
            self.scroll_bar_rect = pygame.Rect(
                scroll_bar_x, 
                50 + scrollbar_pos, 
                SCROLL_BAR_WIDTH - 4, 
                scrollbar_height
            )
            
            # Цвет полосы прокрутки (меняется при наведении)
            color = SCROLL_BAR_HOVER_COLOR if self.scroll_bar_hovered or self.scroll_bar_dragging else SCROLL_BAR_COLOR
            # Рисуем полосу прокрутки с закругленными углами
            pygame.draw.rect(self.screen, color, self.scroll_bar_rect, border_radius=5)
    
    # Метод обработки событий прокрутки
    def handle_scroll(self, event):
        # Нажатие кнопки мыши
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Колесо мыши вверх
            if event.button == 4:
                self.scroll_y = max(0, self.scroll_y - 20)
            # Колесо мыши вниз
            elif event.button == 5:
                total_content_height = len(self.move_history) * 20
                visible_height = HEIGHT - 50
                self.scroll_y = min(total_content_height - visible_height, self.scroll_y + 20)
            # Нажатие на полосу прокрутки
            elif event.button == 1 and self.scroll_bar_rect and self.scroll_bar_rect.collidepoint(event.pos):
                self.scroll_bar_dragging = True
                self.drag_start_y = event.pos[1]
                self.drag_start_scroll = self.scroll_y
        
        # Отпускание кнопки мыши
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.scroll_bar_dragging = False
        
        # Движение мыши
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
    
    # Метод отрисовки всего игрового состояния
    def draw_game_state(self):
        # Рисуем доску
        self.draw_board()
        # Рисуем подсветки
        self.draw_highlights()
        # Рисуем фигуры
        self.draw_pieces()
        # Рисуем историю ходов
        self.draw_move_history()
        
        # Проверяем состояние мата
        if self.board.checkmate:
            font = pygame.font.SysFont('Arial', 32)
            # Определяем победителя
            if self.board.white_to_move:
                text = font.render('Черные выиграли! Мат!', True, RED)
            else:
                text = font.render('Белые выиграли! Мат!', True, RED)
            # Рисуем сообщение о победе по центру доски
            self.screen.blit(text, (BOARD_WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            self.game_over = True
        # Проверяем состояние пата
        elif self.board.stalemate:
            font = pygame.font.SysFont('Arial', 32)
            text = font.render('Пат! Ничья!', True, RED)
            # Рисуем сообщение о ничьей по центру доски
            self.screen.blit(text, (BOARD_WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            self.game_over = True
    
    # Метод обработки кликов мыши
    def handle_click(self, row, col):
        # Если игра окончена, игнорируем клики
        if self.game_over:
            return
        
        # Если кликнули на уже выбранную клетку - снимаем выделение
        if self.selected_square == (row, col):
            self.selected_square = ()
            self.player_clicks = []
        else:
            # Иначе запоминаем выбранную клетку
            self.selected_square = (row, col)
            self.player_clicks.append(self.selected_square)
        
        # Если сделано 2 клика (откуда и куда)
        if len(self.player_clicks) == 2:
            # Создаем объект хода
            move = Move(self.player_clicks[0], self.player_clicks[1], self.board.board)
            
            # Проверяем, есть ли такой ход в списке допустимых
            for valid_move in self.valid_moves:
                if move == valid_move:
                    # Выполняем ход
                    self.board.make_move(valid_move)
                    # Получаем нотацию хода
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
                    
                    # Сбрасываем выбранную клетку и клики
                    self.selected_square = ()
                    self.player_clicks = []
                    self.valid_moves = []
                    return
            
            # Если ход недопустимый, оставляем только первый клик
            self.player_clicks = [self.selected_square]
        
        # Если сделан только один клик
        if len(self.player_clicks) == 1:
            self.valid_moves = []
            row, col = self.player_clicks[0]
            piece = self.board.board[row][col]
            # Если на клетке есть фигура текущего игрока
            if piece != '--' and piece[0] == ('w' if self.board.white_to_move else 'b'):
                # Получаем все допустимые ходы для этой фигуры
                for move in self.board.get_valid_moves():
                    if move.start_row == row and move.start_col == col:
                        self.valid_moves.append(move)