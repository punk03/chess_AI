import tkinter as tk
from tkinter import messagebox
from piece import Piece
import random

class ChessGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Шахматы")
        self.current_player = "white"
        self.selected_piece = None
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.last_move = None  # Для подсветки последнего хода
        self.move_history = []  # Добавляем историю ходов
        self.status_message_timer = None  # Добавляем таймер для сообщений
        self.last_pawn_double_move = None  # Для взятия на проходе
        self.setup_game_mode()
        
    def setup_game_mode(self):
        # Создаем окно выбора режима игры
        self.mode_window = tk.Toplevel(self.window)
        self.mode_window.title("Выбор режима игры")
        self.mode_window.geometry("300x150")
        self.mode_window.transient(self.window)
        self.mode_window.grab_set()
        
        label = tk.Label(self.mode_window, text="Выберите режим игры:", font=('Arial', 14))
        label.pack(pady=10)
        
        bot_button = tk.Button(self.mode_window, text="Игра с компьютером", 
                              command=lambda: self.start_game(True),
                              font=('Arial', 12))
        bot_button.pack(pady=5)
        
        human_button = tk.Button(self.mode_window, text="Игра с человеком", 
                                command=lambda: self.start_game(False),
                                font=('Arial', 12))
        human_button.pack(pady=5)

    def start_game(self, with_ai):
        self.ai_enabled = with_ai
        self.mode_window.destroy()
        self.setup_board()
        self.create_board_gui()
        
        # Создаем фрейм для нижней панели
        bottom_frame = tk.Frame(self.window)
        bottom_frame.grid(row=8, column=0, columnspan=8, sticky="ew")
        
        # Добавляем кнопку отмены хода
        self.undo_button = tk.Button(
            bottom_frame, 
            text="↩ Отменить ход", 
            command=self.undo_move,
            font=('Arial', 12),
            state='disabled'
        )
        self.undo_button.pack(side='left', padx=5)
        
        # Добавляем статус-лейбл
        self.status_label = tk.Label(
            bottom_frame, 
            text="Ход белых", 
            font=('Arial', 14)
        )
        self.status_label.pack(side='left', padx=20)

    def setup_board(self):
        # Расстановка белых фигур
        self.board[7] = [
            Piece("white", "rook"), Piece("white", "knight"), 
            Piece("white", "bishop"), Piece("white", "queen"),
            Piece("white", "king"), Piece("white", "bishop"), 
            Piece("white", "knight"), Piece("white", "rook")
        ]
        self.board[6] = [Piece("white", "pawn") for _ in range(8)]
        
        # Расстановка черных фигур
        self.board[0] = [
            Piece("black", "rook"), Piece("black", "knight"), 
            Piece("black", "bishop"), Piece("black", "queen"),
            Piece("black", "king"), Piece("black", "bishop"), 
            Piece("black", "knight"), Piece("black", "rook")
        ]
        self.board[1] = [Piece("black", "pawn") for _ in range(8)]

    def create_board_gui(self):
        self.buttons = [[None for _ in range(8)] for _ in range(8)]
        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                button = tk.Button(self.window, width=4, height=2, bg=color, font=('Arial', 24))
                button.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                button.config(command=lambda r=row, c=col: self.handle_click(r, c))
                self.buttons[row][col] = button
        
        # Настраиваем размеры столбцов и строк
        for i in range(8):
            self.window.grid_columnconfigure(i, weight=1)
            self.window.grid_rowconfigure(i, weight=1)
        
        self.update_board_display()

    def update_board_display(self):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                text = ""
                if piece:
                    text = self.get_piece_symbol(piece)
                self.buttons[row][col].config(text=text)

    def get_piece_symbol(self, piece):
        symbols = {
            "king": "♔" if piece.color == "white" else "♚",
            "queen": "♕" if piece.color == "white" else "♛",
            "rook": "♖" if piece.color == "white" else "♜",
            "bishop": "♗" if piece.color == "white" else "♝",
            "knight": "♘" if piece.color == "white" else "♞",
            "pawn": "♙" if piece.color == "white" else "♟"
        }
        return symbols.get(piece.type, "")

    def handle_click(self, row, col):
        if self.current_player == "black" and self.ai_enabled:
            return  # Игнорируем клики во время хода ИИ

        if not self.selected_piece:
            if self.board[row][col] and self.board[row][col].color == self.current_player:
                self.selected_piece = (row, col)
                self.buttons[row][col].config(bg="yellow")
                # Показываем возможные ходы
                possible_moves = self.board[row][col].get_possible_moves(row, col, self.board)
                for move_row, move_col in possible_moves:
                    if self.is_valid_move(row, col, move_row, move_col):
                        self.buttons[move_row][move_col].config(bg="lightgreen")
            else:
                self.show_status_message("Выберите свою фигуру!", 2000)
        else:
            old_row, old_col = self.selected_piece
            if self.is_valid_move(old_row, old_col, row, col):
                self.make_move(old_row, old_col, row, col)
                if self.ai_enabled and self.current_player == "black":
                    self.window.after(500, self.make_ai_move)
            else:
                self.show_status_message("Недопустимый ход!", 2000)
            
            self.selected_piece = None
            self.reset_colors()

    def make_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        # Сброс флага взятия на проходе для всех пешек
        for row in self.board:
            for piece in row:
                if piece and piece.type == "pawn":
                    piece.just_moved_two = False
        
        # Проверка на рокировку
        if piece.type == "king" and abs(to_col - from_col) == 2:
            # Короткая рокировка
            if to_col > from_col:
                rook = self.board[from_row][7]
                move_info['rook_had_moved'] = rook.has_moved if rook else None
                self.board[from_row][5] = rook
                self.board[from_row][7] = None
                if rook:
                    rook.has_moved = True
            # Длинная рокировка
            else:
                rook = self.board[from_row][0]
                move_info['rook_had_moved'] = rook.has_moved if rook else None
                self.board[from_row][3] = rook
                self.board[from_row][0] = None
                if rook:
                    rook.has_moved = True
        
        # Проверка на взятие на проходе
        elif piece.type == "pawn" and abs(to_col - from_col) == 1 and not captured_piece:
            self.board[from_row][to_col] = None  # Удаляем взятую пешку
        
        # Проверка на ход пешки на две клетки
        if piece.type == "pawn" and abs(from_row - to_row) == 2:
            piece.just_moved_two = True
        
        # Сохраняем состояние перед ходом
        move_info = {
            'from_pos': (from_row, from_col),
            'to_pos': (to_row, to_col),
            'captured_piece': self.board[to_row][to_col],
            'moved_piece': self.board[from_row][from_col],
            'last_move': self.last_move,
            'piece_had_moved': piece.has_moved,
            'was_castling': piece.type == "king" and abs(to_col - from_col) == 2,
            'was_en_passant': piece.type == "pawn" and abs(to_col - from_col) == 1 and not self.board[to_row][to_col],
            'en_passant_captured_pos': (from_row, to_col) if piece.type == "pawn" and abs(to_col - from_col) == 1 and not self.board[to_row][to_col] else None,
            'rook_had_moved': None  # Будет установлено ниже для рокировки
        }
        self.move_history.append(move_info)
        self.undo_button.config(state='normal')
        
        # Сбрасываем подсветку предыдущего хода
        if self.last_move:
            old_from_row, old_from_col, old_to_row, old_to_col = self.last_move
            color1 = "white" if (old_from_row + old_from_col) % 2 == 0 else "gray"
            color2 = "white" if (old_to_row + old_to_col) % 2 == 0 else "gray"
            self.buttons[old_from_row][old_from_col].config(bg=color1)
            self.buttons[old_to_row][old_to_col].config(bg=color2)
        
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.has_moved = True

        # Подсвечиваем текущий ход
        self.last_move = (from_row, from_col, to_row, to_col)
        self.buttons[from_row][from_col].config(bg="light blue")
        self.buttons[to_row][to_col].config(bg="light blue")

        # Обновляем сообщения
        messages = []
        
        # Сообщение о взятии фигуры
        if captured_piece:
            messages.append(
                f"{'Белые' if self.current_player == 'white' else 'Черные'} "
                f"взяли {self.get_piece_name(captured_piece)}"
            )

        self.current_player = "black" if self.current_player == "white" else "white"
        self.update_board_display()
        
        # Проверяем шах
        if self.is_check(self.current_player):
            messages.append(
                f"{'Черному' if self.current_player == 'black' else 'Белому'} королю шах!"
            )
        
        # Проверка на превращение пешки
        if piece.type == "pawn" and (to_row == 0 or to_row == 7):
            self.promote_pawn(to_row, to_col)
        
        # Проверка на мат или пат после хода
        if self.is_checkmate():
            if self.is_check(self.current_player):
                messages.append(f"Мат! {'Белые' if piece.color == 'white' else 'Черные'} победили!")
            else:
                messages.append("Пат! Ничья!")
        
        # Показываем сообщения
        if messages:
            self.show_status_message(" | ".join(messages))
        else:
            self.status_label.config(text=f"Ход {'черных' if self.current_player == 'black' else 'белых'}")

    def get_piece_name(self, piece):
        names = {
            "king": "короля",
            "queen": "ферзя",
            "rook": "ладью",
            "bishop": "слона",
            "knight": "коня",
            "pawn": "пешку"
        }
        return names.get(piece.type, "фигуру")

    def make_ai_move(self):
        # Собираем все возможные ходы
        possible_moves = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == "black":
                    moves = piece.get_possible_moves(row, col, self.board)
                    for move_row, move_col in moves:
                        if self.is_valid_move(row, col, move_row, move_col):
                            possible_moves.append((row, col, move_row, move_col))

        if possible_moves:
            # Оцениваем ходы и выбираем лучший
            best_moves = []
            best_score = float('-inf')
            
            for from_row, from_col, to_row, to_col in possible_moves:
                score = self.evaluate_move(from_row, from_col, to_row, to_col)
                if score > best_score:
                    best_moves = [(from_row, from_col, to_row, to_col)]
                    best_score = score
                elif score == best_score:
                    best_moves.append((from_row, from_col, to_row, to_col))

            # Выбираем случайный ход из лучших
            from_row, from_col, to_row, to_col = random.choice(best_moves)
            self.make_move(from_row, from_col, to_row, to_col)

    def evaluate_move(self, from_row, from_col, to_row, to_col):
        piece_values = {
            "pawn": 1,
            "knight": 3,
            "bishop": 3,
            "rook": 5,
            "queen": 9,
            "king": 0
        }
        
        score = 0
        # Если можем взять фигуру противника
        if self.board[to_row][to_col]:
            score += piece_values[self.board[to_row][to_col].type]
        
        # Если ход защищает свою фигуру от взятия
        if self.is_piece_under_attack(from_row, from_col):
            score += piece_values[self.board[from_row][from_col].type] / 2
            
        # Бонус за продвижение пешки
        if self.board[from_row][from_col].type == "pawn":
            score += (7 - to_row) * 0.1
            
        return score

    def is_piece_under_attack(self, row, col):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.color != self.current_player:
                    moves = piece.get_possible_moves(r, c, self.board)
                    if (row, col) in moves:
                        return True
        return False

    def is_check(self, color):
        # Находим короля
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.type == "king" and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        # Проверяем, находится ли король под атакой
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    moves = piece.get_possible_moves(row, col, self.board)
                    if king_pos in moves:
                        return True
        return False

    def is_valid_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        if not piece or piece.color != self.current_player:
            return False

        # Получаем все возможные ходы для фигуры
        possible_moves = piece.get_possible_moves(from_row, from_col, self.board)
        if (to_row, to_col) not in possible_moves:
            return False

        # Специальная проверка для рокировки
        if piece.type == "king" and abs(to_col - from_col) == 2:
            # Проверяем, что король не находится под шахом
            if self.is_check(self.current_player):
                return False
            
            # Проверяем, что король не проходит через атакованные поля
            step = 1 if to_col > from_col else -1
            for c in range(from_col + step, to_col + step, step):
                # Создаем временную доску с королем на промежуточной позиции
                temp_board = [row[:] for row in self.board]
                temp_board[from_row][c] = temp_board[from_row][from_col]
                temp_board[from_row][from_col] = None
                
                # Проверяем, атакована ли эта позиция
                for r in range(8):
                    for col_check in range(8):
                        enemy_piece = temp_board[r][col_check]
                        if enemy_piece and enemy_piece.color != self.current_player:
                            enemy_moves = enemy_piece.get_possible_moves(r, col_check, temp_board)
                            if (from_row, c) in enemy_moves:
                                return False

        # Проверяем, не подставляем ли мы короля под шах
        temp_board = [row[:] for row in self.board]
        temp_board[to_row][to_col] = temp_board[from_row][from_col]
        temp_board[from_row][from_col] = None

        # Находим позицию короля
        king_pos = None
        for r in range(8):
            for c in range(8):
                if (temp_board[r][c] and 
                    temp_board[r][c].color == self.current_player and 
                    temp_board[r][c].type == "king"):
                    king_pos = (r, c)
                    break
            if king_pos:
                break

        # Проверяем, не находится ли король под шахом после хода
        for r in range(8):
            for c in range(8):
                if (temp_board[r][c] and 
                    temp_board[r][c].color != self.current_player):
                    enemy_moves = temp_board[r][c].get_possible_moves(r, c, temp_board)
                    if king_pos in enemy_moves:
                        return False

        return True

    def reset_colors(self):
        for row in range(8):
            for col in range(8):
                color = "white" if (row + col) % 2 == 0 else "gray"
                self.buttons[row][col].config(bg=color)

    def show_status_message(self, message, duration=5000):
        # Отменяем предыдущий таймер, если он существует
        if self.status_message_timer:
            self.window.after_cancel(self.status_message_timer)
        
        # Показываем новое сообщение
        self.status_label.config(text=message)
        
        # Устанавливаем таймер для возврата к отображению текущего хода
        self.status_message_timer = self.window.after(
            duration, 
            lambda: self.status_label.config(text=f"Ход {'черных' if self.current_player == 'black' else 'белых'}")
        )

    def undo_move(self):
        if not self.move_history:
            return
        
        # Получаем последний ход
        last_move = self.move_history.pop()
        from_row, from_col = last_move['from_pos']
        to_row, to_col = last_move['to_pos']
        
        # Возвращаем фигуры на места
        self.board[from_row][from_col] = last_move['moved_piece']
        self.board[to_row][to_col] = last_move['captured_piece']
        
        # Восстанавливаем состояние has_moved
        self.board[from_row][from_col].has_moved = last_move['piece_had_moved']
        
        # Обрабатываем специальные случаи
        if last_move['was_castling']:
            # Возвращаем ладью на место
            if to_col > from_col:  # Короткая рокировка
                rook = self.board[from_row][5]
                self.board[from_row][7] = rook
                self.board[from_row][5] = None
                if rook:
                    rook.has_moved = last_move['rook_had_moved'] if last_move['rook_had_moved'] is not None else False
            else:  # Длинная рокировка
                rook = self.board[from_row][3]
                self.board[from_row][0] = rook
                self.board[from_row][3] = None
                if rook:
                    rook.has_moved = last_move['rook_had_moved'] if last_move['rook_had_moved'] is not None else False
        
        if last_move['was_en_passant'] and last_move['en_passant_captured_pos']:
            # Восстанавливаем взятую на проходе пешку
            cap_row, cap_col = last_move['en_passant_captured_pos']
            captured_pawn = Piece(
                "black" if self.current_player == "white" else "white", 
                "pawn"
            )
            captured_pawn.just_moved_two = True
            self.board[cap_row][cap_col] = captured_pawn
        
        # Восстанавливаем подсветку предыдущего хода
        self.last_move = last_move['last_move']
        if self.last_move:
            old_from_row, old_from_col, old_to_row, old_to_col = self.last_move
            self.buttons[old_from_row][old_from_col].config(bg="light blue")
            self.buttons[old_to_row][old_to_col].config(bg="light blue")
        
        # Меняем игрока обратно
        self.current_player = "white" if self.current_player == "black" else "black"
        
        # Обновляем доску
        self.reset_colors()
        self.update_board_display()
        
        # Обновляем статус
        self.status_label.config(text=f"Ход {'черных' if self.current_player == 'black' else 'белых'}")
        
        # Отключаем кнопку, если история пуста
        if not self.move_history:
            self.undo_button.config(state='disabled')

    def promote_pawn(self, row, col):
        # Создаем окно выбора фигуры
        promotion_window = tk.Toplevel(self.window)
        promotion_window.title("Превращение пешки")
        promotion_window.transient(self.window)
        promotion_window.grab_set()
        
        pieces = ["queen", "rook", "bishop", "knight"]
        for piece_type in pieces:
            button = tk.Button(
                promotion_window,
                text=self.get_piece_symbol(Piece(self.board[row][col].color, piece_type)),
                font=('Arial', 24),
                command=lambda p=piece_type: self.complete_promotion(row, col, p, promotion_window)
            )
            button.pack(side='left', padx=5, pady=5)

    def complete_promotion(self, row, col, piece_type, window):
        self.board[row][col] = Piece(self.board[row][col].color, piece_type)
        window.destroy()
        self.update_board_display()

    def is_checkmate(self):
        # Проверяем все возможные ходы текущего игрока
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == self.current_player:
                    moves = piece.get_possible_moves(row, col, self.board)
                    for move_row, move_col in moves:
                        if self.is_valid_move(row, col, move_row, move_col):
                            return False
        return True

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    game = ChessGame()
    game.run() 