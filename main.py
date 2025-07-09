# Импорт системных модулей
import sys
# Импорт библиотеки pygame для создания графического интерфейса
import pygame
# Импорт констант из файла constants.py
from constants import *
# Импорт класса Game из файла game.py
from game import Game

# Главная функция приложения


def main():
    # Инициализация всех модулей pygame
    pygame.init()

    # Создание окна приложения с заданными размерами
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    # Установка заголовка окна
    pygame.display.set_caption("Шахматы")
    # Создание объекта Clock для контроля FPS
    clock = pygame.time.Clock()

    # Создание экземпляра игры, передаем ему экран для отрисовки
    game = Game(screen)

    # Флаг работы основного цикла
    running = True
    # Основной игровой цикл
    while running:
        # Обработка всех событий, произошедших с последнего кадра
        for event in pygame.event.get():
            # Событие закрытия окна
            if event.type == pygame.QUIT:
                running = False

            # Обработка событий мыши (нажатие, отпускание, движение)
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                # Передаем события, связанные с прокруткой, в объект игры
                game.handle_scroll(event)

                # Обработка кликов левой кнопкой мыши
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Получаем координаты курсора
                    x, y = event.pos
                    # Обрабатываем клики только в области шахматной доски
                    if x < BOARD_WIDTH:
                        # Вычисляем номер строки и столбца по координатам
                        row = y // SQUARE_SIZE
                        col = x // SQUARE_SIZE
                        # Передаем клик в объект игры
                        game.handle_click(row, col)

            # Обработка событий клавиатуры
            elif event.type == pygame.KEYDOWN:
                # Комбинация Ctrl+Z - отмена последнего хода
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Отменяем ход на доске
                    game.board.undo_move()
                    # Сбрасываем флаг окончания игры
                    game.game_over = False
                    # Обновляем историю ходов после отмены
                    if game.move_history:
                        if game.board.white_to_move:
                            # Если после отмены ход белых, удаляем последний ход черных
                            if '...' in game.move_history[-1]:
                                game.move_history.pop()
                        else:
                            # Если после отмены ход черных, удаляем последний ход белых
                            if '.' in game.move_history[-1] and '...' not in game.move_history[-1]:
                                game.move_history.pop()

                # Комбинация Ctrl+N - новая игра
                elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Создаем новый экземпляр игры
                    game = Game(screen)

        # Заливаем экран черным цветом (фон)
        screen.fill(BLACK)
        # Отрисовываем текущее состояние игры
        game.draw_game_state()

        # Обновляем содержимое экрана
        pygame.display.flip()
        # Ограничиваем FPS для плавной работы
        clock.tick(FPS)

    # Завершаем работу pygame
    pygame.quit()
    # Выходим из приложения
    sys.exit()


# Точка входа в приложение
if __name__ == "__main__":
    main()
