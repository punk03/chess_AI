class Piece:
    def __init__(self, color, piece_type):
        self.color = color
        self.type = piece_type
        self.has_moved = False  # Для пешек и рокировки
        self.just_moved_two = False  # Для взятия на проходе
        
    def get_possible_moves(self, row, col, board):
        if self.type == "pawn":
            return self._pawn_moves(row, col, board)
        elif self.type == "rook":
            return self._rook_moves(row, col, board)
        elif self.type == "knight":
            return self._knight_moves(row, col, board)
        elif self.type == "bishop":
            return self._bishop_moves(row, col, board)
        elif self.type == "queen":
            return self._queen_moves(row, col, board)
        elif self.type == "king":
            return self._king_moves(row, col, board)
        return []

    def _pawn_moves(self, row, col, board):
        moves = []
        direction = -1 if self.color == "white" else 1
        
        # Обычный ход вперед
        if 0 <= row + direction < 8 and not board[row + direction][col]:
            moves.append((row + direction, col))
            
            # Ход на две клетки с начальной позиции
            if ((self.color == "white" and row == 6) or 
                (self.color == "black" and row == 1)):
                if not board[row + 2*direction][col]:
                    moves.append((row + 2*direction, col))
        
        # Взятие по диагонали (включая взятие на проходе)
        for c in [col-1, col+1]:
            if 0 <= c < 8 and 0 <= row + direction < 8:
                if board[row + direction][c]:  # Обычное взятие
                    if board[row + direction][c].color != self.color:
                        moves.append((row + direction, c))
                elif (board[row][c] and  # Взятие на проходе
                      board[row][c].color != self.color and
                      board[row][c].type == "pawn" and
                      board[row][c].just_moved_two):
                    moves.append((row + direction, c))
        
        return moves

    def _rook_moves(self, row, col, board):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if not board[r][c]:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc
        return moves

    def _knight_moves(self, row, col, board):
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                  (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if (0 <= r < 8 and 0 <= c < 8 and 
                (not board[r][c] or board[r][c].color != self.color)):
                moves.append((r, c))
        return moves

    def _bishop_moves(self, row, col, board):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dr, dc in directions:
            r, c = row + dr, col + dc
            while 0 <= r < 8 and 0 <= c < 8:
                if not board[r][c]:
                    moves.append((r, c))
                elif board[r][c].color != self.color:
                    moves.append((r, c))
                    break
                else:
                    break
                r, c = r + dr, c + dc
        return moves

    def _queen_moves(self, row, col, board):
        return self._rook_moves(row, col, board) + self._bishop_moves(row, col, board)

    def _king_moves(self, row, col, board):
        moves = []
        # Обычные ходы короля
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if (0 <= r < 8 and 0 <= c < 8 and 
                    (not board[r][c] or board[r][c].color != self.color)):
                    moves.append((r, c))
        
        # Рокировка
        if not self.has_moved:
            # Короткая рокировка
            if (col + 3 < 8 and board[row][col+3] and 
                board[row][col+3].type == "rook" and 
                not board[row][col+3].has_moved and
                not board[row][col+1] and 
                not board[row][col+2]):
                moves.append((row, col+2))
            
            # Длинная рокировка
            if (col - 4 >= 0 and board[row][col-4] and 
                board[row][col-4].type == "rook" and 
                not board[row][col-4].has_moved and
                not board[row][col-1] and 
                not board[row][col-2] and 
                not board[row][col-3]):
                moves.append((row, col-2))
        
        return moves 