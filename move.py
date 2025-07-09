class Move:
    # Словарь для преобразования шахматных обозначений рядов в индексы строк матрицы
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                    '5': 3, '6': 2, '7': 1, '8': 0}
    
    # Обратный словарь для преобразования индексов строк в шахматные обозначения
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    
    # Словарь для преобразования шахматных обозначений колонок в индексы столбцов матрицы
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                    'e': 4, 'f': 5, 'g': 6, 'h': 7}
    
    # Обратный словарь для преобразования индексов столбцов в шахматные обозначения
    cols_to_files = {v: k for k, v in files_to_cols.items()}
    
    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        # Начальная позиция (строка и столбец)
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        
        # Конечная позиция (строка и столбец)
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        
        # Фигура, которая делает ход (берется из начальной позиции на доске)
        self.piece_moved = board[self.start_row][self.start_col]
        
        # Фигура, которая была взята (если есть) (берется из конечной позиции на доске)
        self.piece_captured = board[self.end_row][self.end_col]
        
        # Флаг превращения пешки (True, если пешка дошла до последней горизонтали)
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or \
                                (self.piece_moved == 'bp' and self.end_row == 7)
        
        # Флаг взятия на проходе (передается извне)
        self.is_enpassant_move = is_enpassant_move
        
        # Если это взятие на проходе, корректируем информацию о взятой фигуре
        if self.is_enpassant_move:
            self.piece_captured = 'bp' if self.piece_moved == 'wp' else 'wp'
        
        # Флаг рокировки (передается извне)
        self.is_castle_move = is_castle_move
        
        # Уникальный идентификатор хода для сравнения
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    
    # Метод сравнения ходов (по их идентификаторам)
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    
    # Метод получения шахматной нотации хода
    def get_chess_notation(self):
        # Тип фигуры (без учета цвета)
        piece = self.piece_moved[1]
        
        # Буквенное обозначение конечной колонки (a-h)
        end_file = self.cols_to_files[self.end_col]
        
        # Цифровое обозначение конечного ряда (1-8)
        end_rank = self.rows_to_ranks[self.end_row]
        
        # Обработка рокировки
        if self.is_castle_move:
            # Короткая рокировка (в сторону королевского фланга)
            if self.end_col > self.start_col:
                return 'O-O'
            # Длинная рокировка (в сторону ферзевого фланга)
            else:
                return 'O-O-O'
        
        # Обработка превращения пешки
        if self.is_pawn_promotion:
            return f"{end_file}{end_rank}=Q"  # Всегда превращаем в ферзя
        
        # Обработка взятия на проходе
        if self.is_enpassant_move:
            return f"{self.cols_to_files[self.start_col]}x{end_file}{end_rank} e.p."
        
        # Для всех остальных ходов:
        
        # Символ фигуры (пустая строка для пешки)
        piece_symbol = '' if piece == 'p' else 'KQRBN'['KQRBN'.index(piece)]
        
        # Символ взятия (x если была взята фигура)
        capture = 'x' if self.piece_captured != '--' else ''
        
        # Особый случай для пешки при взятии - указываем исходную колонку
        if piece == 'p' and self.piece_captured != '--':
            return f"{self.cols_to_files[self.start_col]}x{end_file}{end_rank}"
        
        # Стандартная нотация: [фигура][взятие][конечная позиция]
        return f"{piece_symbol}{capture}{end_file}{end_rank}"
    
    # Вспомогательный метод для получения шахматных координат по индексам матрицы
    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]