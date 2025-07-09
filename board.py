# Импорт класса Move из модуля move для работы с ходами
from move import Move
# Импорт класса CastleRights из модуля castleRights для отслеживания прав на рокировку
from castleRights import CastleRights

class ChessBoard:
    # Конструктор класса, инициализирующий шахматную доску
    def __init__(self):
        # Создаем начальную позицию на доске
        self.board = self.create_starting_board()
        # Флаг, указывающий, чей сейчас ход (True - белые, False - черные)
        self.white_to_move = True
        # Журнал всех сделанных ходов
        self.move_log = []
        # Начальная позиция белого короля (ряд 7, колонка 4 - e1)
        self.white_king_pos = (7, 4)
        # Начальная позиция черного короля (ряд 0, колонка 4 - e8)
        self.black_king_pos = (0, 4)
        # Флаг, указывающий на мат (True - мат)
        self.checkmate = False
        # Флаг, указывающий на пат (True - пат)
        self.stalemate = False
        # Координаты поля, где возможно взятие на проходе (пустой кортеж - нет возможности)
        self.enpassant_possible = ()
        # Текущие права на рокировку для обеих сторон
        self.current_castling_rights = CastleRights(True, True, True, True)
        # Журнал прав на рокировку (для возможности отмены хода)
        self.castle_rights_log = [CastleRights(self.current_castling_rights.wks,
                                             self.current_castling_rights.bks,
                                             self.current_castling_rights.wqs,
                                             self.current_castling_rights.bqs)]

    # Метод создания начальной позиции на шахматной доске
    def create_starting_board(self):
        # Создаем пустую доску 8x8, заполненную строками '--' (пустые клетки)
        board = [['--' for _ in range(8)] for _ in range(8)]

        # Расставляем черные фигуры на первой горизонтали (ряд 0)
        board[0] = ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR']
        # Расставляем черные пешки на второй горизонтали (ряд 1)
        board[1] = ['bp'] * 8

        # Расставляем белые пешки на седьмой горизонтали (ряд 6)
        board[6] = ['wp'] * 8
        # Расставляем белые фигуры на восьмой горизонтали (ряд 7)
        board[7] = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']

        # Возвращаем заполненную доску
        return board

    # Метод выполнения хода на доске
    def make_move(self, move):
        # Убираем фигуру с начальной позиции
        self.board[move.start_row][move.start_col] = '--'
        # Ставим фигуру на конечную позицию
        self.board[move.end_row][move.end_col] = move.piece_moved
        # Добавляем ход в журнал
        self.move_log.append(move)
        # Меняем очередь хода
        self.white_to_move = not self.white_to_move

        # Обновляем позицию короля, если он двигался
        if move.piece_moved == 'wK':
            self.white_king_pos = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.end_row, move.end_col)

        # Обработка превращения пешки
        if move.is_pawn_promotion:
            # Заменяем пешку на ферзя
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # Обработка взятия на проходе
        if move.is_enpassant_move:
            # Убираем взятую пешку
            self.board[move.start_row][move.end_col] = '--'

        # Обновление возможности взятия на проходе
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            # Устанавливаем координаты поля, где возможно взятие на проходе
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            # Сбрасываем возможность взятия на проходе
            self.enpassant_possible = ()

        # Обработка рокировки
        if move.is_castle_move:
            # Определяем ряд (для белых или черных)
            row = move.start_row
            # Короткая рокировка (в сторону королевского фланга)
            if move.end_col > move.start_col:
                # Перемещаем ладью на f1/f8
                self.board[row][move.end_col-1] = self.board[row][move.end_col+1]
                # Очищаем исходную позицию ладьи h1/h8
                self.board[row][move.end_col+1] = '--'
            # Длинная рокировка (в сторону ферзевого фланга)
            else:
                # Перемещаем ладью на d1/d8
                self.board[row][move.end_col+1] = self.board[row][move.end_col-2]
                # Очищаем исходную позицию ладьи a1/a8
                self.board[row][move.end_col-2] = '--'

        # Обновление прав на рокировку после хода
        self.update_castle_rights(move)
        # Сохраняем текущие права на рокировку в журнал
        self.castle_rights_log.append(CastleRights(self.current_castling_rights.wks,
                                                 self.current_castling_rights.bks,
                                                 self.current_castling_rights.wqs,
                                                 self.current_castling_rights.bqs))

    # Метод отмены последнего хода
    def undo_move(self):
        # Если нет ходов для отмены, выходим
        if len(self.move_log) == 0:
            return

        # Берем последний ход из журнала
        move = self.move_log.pop()
        # Восстанавливаем фигуру на начальной позиции
        self.board[move.start_row][move.start_col] = move.piece_moved
        # Восстанавливаем фигуру (или пустую клетку) на конечной позиции
        self.board[move.end_row][move.end_col] = move.piece_captured
        # Меняем очередь хода обратно
        self.white_to_move = not self.white_to_move

        # Обновляем позицию короля, если он двигался
        if move.piece_moved == 'wK':
            self.white_king_pos = (move.start_row, move.start_col)
        elif move.piece_moved == 'bK':
            self.black_king_pos = (move.start_row, move.start_col)

        # Отмена взятия на проходе
        if move.is_enpassant_move:
            # Очищаем конечную позицию (где оказалась пешка)
            self.board[move.end_row][move.end_col] = '--'
            # Восстанавливаем взятую пешку
            self.board[move.start_row][move.end_col] = move.piece_captured
            # Восстанавливаем возможность взятия на проходе
            self.enpassant_possible = (move.end_row, move.end_col)

        # Отмена двойного хода пешки
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            # Сбрасываем возможность взятия на проходе
            self.enpassant_possible = ()

        # Отмена рокировки
        if move.is_castle_move:
            row = move.start_row
            # Короткая рокировка
            if move.end_col > move.start_col:
                # Возвращаем ладью на h1/h8
                self.board[row][move.end_col+1] = self.board[row][move.end_col-1]
                # Очищаем промежуточную позицию f1/f8
                self.board[row][move.end_col-1] = '--'
            # Длинная рокировка
            else:
                # Возвращаем ладью на a1/a8
                self.board[row][move.end_col-2] = self.board[row][move.end_col+1]
                # Очищаем промежуточную позицию d1/d8
                self.board[row][move.end_col+1] = '--'

        # Восстановление прав на рокировку
        # Удаляем последнюю запись из журнала прав на рокировку
        self.castle_rights_log.pop()
        # Восстанавливаем предыдущие права на рокировку
        self.current_castling_rights = self.castle_rights_log[-1]

        # Сбрасываем флаги мата и пата
        self.checkmate = False
        self.stalemate = False

    # Метод обновления прав на рокировку после хода
    def update_castle_rights(self, move):
        # Если двигался белый король - теряем все права на рокировку белых
        if move.piece_moved == 'wK':
            self.current_castling_rights.wks = False
            self.current_castling_rights.wqs = False
        # Если двигался черный король - теряем все права на рокировку черных
        elif move.piece_moved == 'bK':
            self.current_castling_rights.bks = False
            self.current_castling_rights.bqs = False
        # Если двигалась белая ладья
        elif move.piece_moved == 'wR':
            if move.start_row == 7:  # Проверяем, что это ладья на первой горизонтали
                if move.start_col == 0:  # Ладья на a1 (длинная рокировка)
                    self.current_castling_rights.wqs = False
                elif move.start_col == 7:  # Ладья на h1 (короткая рокировка)
                    self.current_castling_rights.wks = False
        # Если двигалась черная ладья
        elif move.piece_moved == 'bR':
            if move.start_row == 0:  # Проверяем, что это ладья на восьмой горизонтали
                if move.start_col == 0:  # Ладья на a8 (длинная рокировка)
                    self.current_castling_rights.bqs = False
                elif move.start_col == 7:  # Ладья на h8 (короткая рокировка)
                    self.current_castling_rights.bks = False

        # Если была взята белая ладья
        if move.piece_captured == 'wR':
            if move.end_row == 7:  # Проверяем, что это ладья на первой горизонтали
                if move.end_col == 0:  # Ладья на a1 (длинная рокировка)
                    self.current_castling_rights.wqs = False
                elif move.end_col == 7:  # Ладья на h1 (короткая рокировка)
                    self.current_castling_rights.wks = False
        # Если была взята черная ладья
        elif move.piece_captured == 'bR':
            if move.end_row == 0:  # Проверяем, что это ладья на восьмой горизонтали
                if move.end_col == 0:  # Ладья на a8 (длинная рокировка)
                    self.current_castling_rights.bqs = False
                elif move.end_col == 7:  # Ладья на h8 (короткая рокировка)
                    self.current_castling_rights.bks = False

    # Метод получения всех допустимых ходов с учетом правил шахмат
    def get_valid_moves(self):
        # Сохраняем текущее состояние специальных ходов
        temp_enpassant_possible = self.enpassant_possible
        temp_castle_rights = CastleRights(
            self.current_castling_rights.wks,
            self.current_castling_rights.bks,
            self.current_castling_rights.wqs,
            self.current_castling_rights.bqs
        )

        # 1. Генерируем все возможные ходы без учета шаха
        moves = self.get_all_possible_moves()

        # 2. Фильтруем ходы, оставляющие короля под шахом
        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.white_to_move = not self.white_to_move
            if self.in_check():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undo_move()

        # 3. Проверяем конечное состояние игры
        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        # 4. Добавляем рокировки, если они возможны
        if self.white_to_move:
            self.get_castle_moves(self.white_king_pos[0], self.white_king_pos[1], moves)
        else:
            self.get_castle_moves(self.black_king_pos[0], self.black_king_pos[1], moves)

        # Восстанавливаем временные параметры
        self.enpassant_possible = temp_enpassant_possible
        self.current_castling_rights = temp_castle_rights

        return moves

    # Метод проверки, находится ли текущий король под шахом
    def in_check(self):
        if self.white_to_move:
            return self.square_under_attack(self.white_king_pos[0], self.white_king_pos[1])
        else:
            return self.square_under_attack(self.black_king_pos[0], self.black_king_pos[1])

    # Метод проверки, атакована ли указанная клетка
    def square_under_attack(self, row, col):
        # Переключаемся на ход противника для проверки его атак
        self.white_to_move = not self.white_to_move
        # Получаем все возможные ходы противника
        opponent_moves = self.get_all_possible_moves()
        # Возвращаем очередь хода обратно
        self.white_to_move = not self.white_to_move

        # Проверяем, есть ли среди ходов противника атака на указанную клетку
        for move in opponent_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False

    # Метод получения всех возможных ходов без учета шаха
    def get_all_possible_moves(self):
        moves = []
        # Перебираем все клетки доски
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                # Определяем цвет фигуры на текущей клетке
                turn = self.board[row][col][0]
                # Проверяем, соответствует ли цвет фигуры текущему игроку
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    # Получаем тип фигуры
                    piece = self.board[row][col][1]
                    # Вызываем соответствующий метод генерации ходов для фигуры
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

    # Метод получения ходов для пешки
    def get_pawn_moves(self, row, col, moves):
        if self.white_to_move:  # Ход белых пешек
            if self.board[row-1][col] == '--':  # Ход на 1 клетку вперед
                moves.append(Move((row, col), (row-1, col), self.board))
                # Ход на 2 клетки из начальной позиции
                if row == 6 and self.board[row-2][col] == '--':
                    moves.append(Move((row, col), (row-2, col), self.board))

            # Взятия влево
            if col-1 >= 0:
                if self.board[row-1][col-1][0] == 'b':  # Взятие черной фигуры
                    moves.append(Move((row, col), (row-1, col-1), self.board))
                elif (row-1, col-1) == self.enpassant_possible:  # Взятие на проходе
                    moves.append(Move((row, col), (row-1, col-1), self.board, is_enpassant_move=True))

            # Взятия вправо
            if col+1 <= 7:
                if self.board[row-1][col+1][0] == 'b':  # Взятие черной фигуры
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row-1, col+1) == self.enpassant_possible:  # Взятие на проходе
                    moves.append(Move((row, col), (row-1, col+1), self.board, is_enpassant_move=True))

        else:  # Ход черных пешек
            if self.board[row+1][col] == '--':  # Ход на 1 клетку вперед
                moves.append(Move((row, col), (row+1, col), self.board))
                # Ход на 2 клетки из начальной позиции
                if row == 1 and self.board[row+2][col] == '--':
                    moves.append(Move((row, col), (row+2, col), self.board))

            # Взятия влево
            if col-1 >= 0:
                if self.board[row+1][col-1][0] == 'w':  # Взятие белой фигуры
                    moves.append(Move((row, col), (row+1, col-1), self.board))
                elif (row+1, col-1) == self.enpassant_possible:  # Взятие на проходе
                    moves.append(Move((row, col), (row+1, col-1), self.board, is_enpassant_move=True))

            # Взятия вправо
            if col+1 <= 7:
                if self.board[row+1][col+1][0] == 'w':  # Взятие белой фигуры
                    moves.append(Move((row, col), (row+1, col+1), self.board))
                elif (row+1, col+1) == self.enpassant_possible:  # Взятие на проходе
                    moves.append(Move((row, col), (row+1, col+1), self.board, is_enpassant_move=True))

    # Метод получения ходов для ладьи
    def get_rook_moves(self, row, col, moves):
        # Направления движения ладьи (вверх, вниз, влево, вправо)
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        # Определяем цвет вражеских фигур
        enemy_color = 'b' if self.white_to_move else 'w'

        # Перебираем все направления
        for d in directions:
            # Перебираем все возможные расстояния в данном направлении
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                # Проверяем, что не вышли за пределы доски
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    # Если клетка пустая - добавляем ход
                    if end_piece == '--':
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # Если на клетке вражеская фигура - добавляем взятие и выходим из цикла
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    # Если на клетке своя фигура - выходим из цикла
                    else:
                        break
                # Если вышли за пределы доски - выходим из цикла
                else:
                    break

    # Метод получения ходов для коня
    def get_knight_moves(self, row, col, moves):
        # Все возможные ходы коня (L-образные)
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        # Определяем цвет своих фигур
        ally_color = 'w' if self.white_to_move else 'b'

        # Перебираем все возможные ходы коня
        for m in knight_moves:
            end_row = row + m[0]
            end_col = col + m[1]

            # Проверяем, что не вышли за пределы доски
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # Если клетка пустая или с вражеской фигурой - добавляем ход
                if end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    # Метод получения ходов для слона
    def get_bishop_moves(self, row, col, moves):
        # Направления движения слона (по диагоналям)
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        # Определяем цвет вражеских фигур
        enemy_color = 'b' if self.white_to_move else 'w'

        # Перебираем все направления
        for d in directions:
            # Перебираем все возможные расстояния в данном направлении
            for i in range(1, 8):
                end_row = row + d[0] * i
                end_col = col + d[1] * i

                # Проверяем, что не вышли за пределы доски
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    # Если клетка пустая - добавляем ход
                    if end_piece == '--':
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    # Если на клетке вражеская фигура - добавляем взятие и выходим из цикла
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                        break
                    # Если на клетке своя фигура - выходим из цикла
                    else:
                        break
                # Если вышли за пределы доски - выходим из цикла
                else:
                    break

    # Метод получения ходов для ферзя
    def get_queen_moves(self, row, col, moves):
        # Ферзь сочетает возможности ладьи и слона
        self.get_rook_moves(row, col, moves)
        self.get_bishop_moves(row, col, moves)

    # Метод получения ходов для короля
    def get_king_moves(self, row, col, moves):
        # Все возможные ходы короля (на 1 клетку в любом направлении)
        king_moves = ((-1, -1), (-1, 0), (-1, 1),
                     (0, -1),          (0, 1),
                     (1, -1),  (1, 0), (1, 1))
        # Определяем цвет своих фигур
        ally_color = 'w' if self.white_to_move else 'b'

        # Перебираем все возможные ходы короля
        for i in range(8):
            end_row = row + king_moves[i][0]
            end_col = col + king_moves[i][1]

            # Проверяем, что не вышли за пределы доски
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # Если клетка пустая или с вражеской фигурой - добавляем ход
                if end_piece[0] != ally_color:
                    moves.append(Move((row, col), (end_row, end_col), self.board))

    # Метод проверки возможности рокировки
    def get_castle_moves(self, row, col, moves):
        # Нельзя рокироваться под шахом
        if self.square_under_attack(row, col):
            return
        
        # Короткая рокировка (kingside)
        if (self.white_to_move and self.current_castling_rights.wks) or \
           (not self.white_to_move and self.current_castling_rights.bks):
            self.get_kingside_castle_moves(row, col, moves)
        
        # Длинная рокировка (queenside)
        if (self.white_to_move and self.current_castling_rights.wqs) or \
           (not self.white_to_move and self.current_castling_rights.bqs):
            self.get_queenside_castle_moves(row, col, moves)

    # Метод проверки возможности короткой рокировки
    def get_kingside_castle_moves(self, row, col, moves):
        # Проверяем, что клетки между королем и ладьей пусты
        if self.board[row][col+1] == '--' and self.board[row][col+2] == '--':
            # Проверяем, что король не проходит через атакованные клетки
            if not self.square_under_attack(row, col+1) and not self.square_under_attack(row, col+2):
                # Добавляем ход рокировки
                moves.append(Move((row, col), (row, col+2), self.board, is_castle_move=True))

    # Метод проверки возможности длинной рокировки
    def get_queenside_castle_moves(self, row, col, moves):
        # Проверяем, что клетки между королем и ладьей пусты
        if self.board[row][col-1] == '--' and self.board[row][col-2] == '--' and self.board[row][col-3] == '--':
            # Проверяем, что король не проходит через атакованные клетки
            if not self.square_under_attack(row, col-1) and not self.square_under_attack(row, col-2):
                # Добавляем ход рокировки
                moves.append(Move((row, col), (row, col-2), self.board, is_castle_move=True))