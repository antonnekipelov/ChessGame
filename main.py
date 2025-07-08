import sys
import pygame
from constants import *
from game import Game

def main():
    # Инициализация pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Шахматы")
    clock = pygame.time.Clock()
    
    # Создание экземпляра игры
    game = Game(screen)

    # Основной игровой цикл
    running = True
    while running:
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Обработка событий мыши
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                # Передаем события прокрутки
                game.handle_scroll(event)
                
                # Обработка кликов по доске (только левая кнопка мыши)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x, y = event.pos
                    # Клики обрабатываем только на шахматной доске
                    if x < BOARD_WIDTH:
                        row = y // SQUARE_SIZE
                        col = x // SQUARE_SIZE
                        game.handle_click(row, col)
            
            # Обработка клавиатуры
            elif event.type == pygame.KEYDOWN:
                # Отмена хода (Ctrl+Z)
                if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    game.board.undo_move()
                    game.game_over = False
                    # После отмены хода обновляем историю
                    if game.move_history:
                        if game.board.white_to_move:
                            # Если после отмены ход белых, удаляем последний ход черных
                            if '...' in game.move_history[-1]:
                                game.move_history.pop()
                        else:
                            # Если после отмены ход черных, удаляем последний ход белых
                            if '.' in game.move_history[-1] and '...' not in game.move_history[-1]:
                                game.move_history.pop()
                
                # Новая игра (Ctrl+N)
                elif event.key == pygame.K_n and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    game = Game(screen)  # Создаем новую игру
        
        # Отрисовка игры
        screen.fill(BLACK)
        game.draw_game_state()
        
        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)

    # Завершение работы
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()