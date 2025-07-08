class Move:
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                    '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'a': 0, 'b': 1, 'c': 2, 'd': 3,
                    'e': 4, 'f': 5, 'g': 6, 'h': 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}
    
    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or \
                                (self.piece_moved == 'bp' and self.end_row == 7)
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = 'bp' if self.piece_moved == 'wp' else 'wp'
        self.is_castle_move = is_castle_move
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    
    def get_chess_notation(self):
        piece = self.piece_moved[1]
        end_file = self.cols_to_files[self.end_col]
        end_rank = self.rows_to_ranks[self.end_row]
        
        # Рокировка
        if self.is_castle_move:
            return 'O-O' if self.end_col > self.start_col else 'O-O-O'
        
        # Превращение пешки
        if self.is_pawn_promotion:
            return f"{end_file}{end_rank}=Q"
        
        # Взятие на проходе
        if self.is_enpassant_move:
            return f"{self.cols_to_files[self.start_col]}x{end_file}{end_rank} e.p."
        
        # Определяем нужные компоненты
        piece_symbol = '' if piece == 'p' else 'KQRBN'['KQRBN'.index(piece)]
        capture = 'x' if self.piece_captured != '--' else ''
        
        # Для пешек при взятии указываем исходную колонку
        if piece == 'p' and self.piece_captured != '--':
            return f"{self.cols_to_files[self.start_col]}x{end_file}{end_rank}"
        
        return f"{piece_symbol}{capture}{end_file}{end_rank}"
    
    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]