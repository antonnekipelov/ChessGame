from move import Move
from castleRights import CastleRights


class ChessBoard:
    def __init__(self):
        self.board = self.create_starting_board()
        self.white_to_move = True
        self.move_log = []
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.enpassant_possible = ()  # координаты поля, где возможно взятие на проходе
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks,
                                               self.current_castling_rights.bks,
                                               self.current_castling_rights.wqs,
                                               self.current_castling_rights.bqs)]

    def create_starting_board(self):
        # Создаем начальную позицию
        board = [['--' for _ in range(8)] for _ in range(8)]

        # Расставляем черные фигуры
        board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        board[1] = ['bp'] * 8

        # Расставляем белые фигуры
        board[6] = ['wp'] * 8
        board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

        return board

    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move

        # Обновляем позицию короля, если он двигался
        if move.piece_moved == 'wK':
            self.white_king_pos = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.end_row, move.end_col)

        # Превращение пешки
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # Взятие на проходе
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'

        # Обновляем возможность взятия на проходе
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = (
                (move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        # Рокировка
        if move.is_castle_move:
            row = move.start_row
            if move.end_col > move.start_col:  # Короткая рокировка (kingside)
                # Перемещаем ладью
                self.board[row][move.end_col-1] = self.board[row][move.end_col+1]  # Ладья на f1/f8
                self.board[row][move.end_col+1] = '--'  # Очищаем h1/h8
            else:  # Длинная рокировка (queenside)
                # Перемещаем ладью
                self.board[row][move.end_col+1] = self.board[row][move.end_col-2]  # Ладья на d1/d8
                self.board[row][move.end_col-2] = '--'  # Очищаем a1/a8

        # Обновление прав на рокировку
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks,
                                                   self.current_castling_rights.bks,
                                                   self.current_castling_rights.wqs,
                                                   self.current_castling_rights.bqs))

    def undo_move(self):
        if len(self.move_log) == 0:
            return

        move = self.move_log.pop()
        self.board[move.start_row][move.start_col] = move.piece_moved
        self.board[move.end_row][move.end_col] = move.piece_captured
        self.white_to_move = not self.white_to_move

        # Обновляем позицию короля, если он двигался
        if move.piece_moved == 'wK':
            self.white_king_pos = (move.start_row, move.start_col)
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.start_row, move.start_col)

        # Отменяем взятие на проходе
        if move.is_enpassant_move:
            self.board[move.end_row][move.end_col] = '--'
            self.board[move.start_row][move.end_col] = move.piece_captured
            self.enpassant_possible = (move.end_row, move.end_col)

        # Отменяем двойной ход пешки
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ()

        # Отменяем рокировку
        if move.is_castle_move:
            row = move.start_row
            if move.end_col > move.start_col:  # Короткая рокировка
                # Возвращаем ладью
                self.board[row][move.end_col+1] = self.board[row][move.end_col-1]  # Ладья на h1/h8
                self.board[row][move.end_col-1] = '--'  # Очищаем f1/f8
            else:  # Длинная рокировка
                # Возвращаем ладью
                self.board[row][move.end_col-2] = self.board[row][move.end_col+1]  # Ладья на a1/a8
                self.board[row][move.end_col+1] = '--'  # Очищаем d1/d8

        # Восстанавливаем права на рокировку
        self.castle_rights_log.pop()
        self.current_castling_rights = self.castle_rights_log[-1]

        self.checkmate = False
        self.stalemate = False

    def update_castle_rights(self, move):
        # Если король или ладья двигались, теряем права на рокировку
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:
                    self.current_castling_rights.bks = False

        # Если ладья была взята, теряем права на рокировку
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:
                    self.current_castling_rights.bks = False

    def get_valid_moves(self):
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wks,
                                          self.current_castling_rights.bks,
                                          self.current_castling_rights.wqs,
                                          self.current_castling_rights.bqs)

        # 1. Генерируем все возможные ходы
        moves = self.get_all_possible_moves()

        # 2. Для каждого хода делаем ход
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            # 3. После хода проверяем, не под шахом ли наш король
            self.white_to_move = not self.white_to_move
            if self.in_check():
                # 4. Если под шахом, удаляем ход из списка разрешенных
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()

        # 5. Если нет разрешенных ходов, это мат или пат
        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # 6. Проверяем возможность рокировки
        if self.white_to_move:
            self.get_castle_moves(
                self.white_king_pos[0], self.white_king_pos[1], moves)
        else:
            self.get_castle_moves(
                self.black_king_pos[0], self.black_king_pos[1], moves)

        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_rights = temp_castle_rights
        return moves

    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_pos[0], self.white_king_pos[1])
        else:
            return self.square_under_attack(self.black_king_pos[0], self.black_king_pos[1])

    def square_under_attack(self, row, col):
        self.white_to_move = not self.white_to_move  # Переключаемся на ход противника
        opponent_moves = self.get_all_possible_moves()
        self.white_to_move = not self.white_to_move  # Возвращаем обратно

        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    def get_all_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[row][col][1]
                    if piece == 'p':
                        self.get_pawn_moves(row, col, moves)
                    elif piece == 'R':
                        self.get_rook_moves(row, col, moves)
                    elif piece == 'N':
                        self.get_knight_moves(row, col, moves)
                    elif piece == 'B':
                        self.get_bishop_moves(row, col, moves)
                    elif piece == 'Q':
                        self.get_queen_moves(row, col, moves)
                    elif piece == 'K':
                        self.get_king_moves(row, col, moves)
        return moves

    def get_pawn_moves(self, row, col, moves):
        if self.white_to_move:  # Ход белых пешек
            if self.board[row-1][col] == '--':  # Ход на 1 клетку вперед
                moves.append(Move((row, col), (row-1, col), self.board))
                # Ход на 2 клетки из начальной позиции
                if row == 6 and self.board[row-2][col] == '--':
                    moves.append(Move((row, col), (row-2, col), self.board))

            # Взятия
            if col-1 >= 0:  # Взятие влево
                if self.board[row-1][col-1][0] == 'b':
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row-1, col-1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row-1, col-1),
                                 self.board, is_enpassant_move=True))

            if col+1 <= 7:  # Взятие вправо
                if self.board[row-1][col+1][0] == 'b':
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row-1, col+1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row-1, col+1),
                                 self.board, is_enpassant_move=True))

        else:  # Ход черных пешек
            if self.board[row+1][col] == '--':  # Ход на 1 клетку вперед
                moves.append(Move((row, col), (row+1, col), self.board))
                # Ход на 2 клетки из начальной позиции
                if row == 1 and self.board[row+2][col] == '--':
                    moves.append(Move((row, col), (row+2, col), self.board))

            # Взятия
            if col-1 >= 0:  # Взятие влево
                if self.board[row+1][col-1][0] == 'w':
                    moves.append(Move((row, col), (row+1, col-1), self.board))
                elif (row+1, col-1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row+1, col-1),
                                 self.board, is_enpassant_move=True))

            if col+1 <= 7:  # Взятие вправо
                if self.board[row+1][col+1][0] == 'w':
                    moves.append(Move((row, col), (row+1, col+1), self.board))
                elif (row+1, col+1) == self.enpassant_possible:
                    moves.append(Move((row, col), (row+1, col+1),
                                 self.board, is_enpassant_move=True))

    def get_rook_moves(self, row, col, moves):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemy_color = 'b' if self.white_to_move else 'w'

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':  # Пустая клетка
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # Взятие вражеской фигуры
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                        break
                    else:  # Своя фигура
                        break
                else:  # За пределами доски
                    break

    def get_knight_moves(self, row, col, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = 'w' if self.white_to_move else 'b'

        for m in knight_moves:
            end_row = row + m[0]
            end_col = col + m[1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(
                        Move((row, col), (end_row, end_col), self.board))

    def get_bishop_moves(self, row, col, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.white_to_move else 'w'

        for d in directions:
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == '--':  # Пустая клетка
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:  # Взятие вражеской фигуры
                        moves.append(
                            Move((row, col), (end_row, end_col), self.board))
                        break
                    else:  # Своя фигура
                        break
                else:  # За пределами доски
                    break

    def get_queen_moves(self, row, col, moves):
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    def get_king_moves(self, row, col, moves):
        king_moves = ((-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1))
        ally_color = 'w' if self.white_to_move else 'b'

        for i in range(8):
            end_row = row + king_moves[i][0]
            end_col = col + king_moves[i][1]

            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color:
                    moves.append(
                        Move((row, col), (end_row, end_col), self.board))

    def get_castle_moves(self, row, col, moves):
        if self.square_under_attack(row, col):
            return  # Нельзя рокироваться под шахом
        
        # Короткая рокировка (kingside)
        if (self.white_to_move and self.current_castling_rights.wks) or \
        (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(row, col, moves)
        
        # Длинная рокировка (queenside)
        if (self.white_to_move and self.current_castling_rights.wqs) or \
        (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(row, col, moves)

    def get_kingside_castle_moves(self, row, col, moves):
        # Проверяем пустые клетки между королем и ладьей
        if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            # Проверяем, что король не проходит через битые поля
            if not self.square_under_attack(row, col+1) and not self.square_under_attack(row, col+2):
                moves.append(Move((row, col), (row, col+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, row, col, moves):
        # Проверяем пустые клетки между королем и ладьей
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--':
            # Проверяем, что король не проходит через битые поля
            if not self.square_under_attack(row, col-1) and not self.square_under_attack(row, col-2):
                moves.append(Move((row, col), (row, col-2), self.board, is_castle_move=True))