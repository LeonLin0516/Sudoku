from tkinter import *
from Sudoku_Generator import *

MARGIN = 20 # Pixels around the board
SIDE = 50 # Width of every board cell
WIDTH = MARGIN * 2 + SIDE * 9
HEIGHT = MARGIN * 2 + SIDE * 9

class Error(Exception):
    """
    An application specific error
    """
    pass

class Game(object):
    """
    The actual game panel in charge of storing the state of the game and check
    whether the puzzle is completed.
    """
    def __init__(self, board_file):
        self.start_puzzle = board_file
        self.game_over = False
    
    def start(self):
        self.puzzle = []
        for i in range(9):
            self.puzzle.append([])
            for j in range(9):
                self.puzzle[i].append(self.start_puzzle[i][j])

    def new_game(self):
        pass
            
    def check_win(self):
        for row in range(9):
            if not self.check_row(row):
                return False
        for col in range(9):
            if not self.check_col(col):
                return False
        for row in range(3):
            for col in range(3):
                if not self.check_square(row,col):
                    return False
        self.game_over = True
        return True

    def check_block(self,block):
        return set(block) == set(range(1,10))

    def check_row(self,row):
        return self.check_block(self.puzzle[row])

    def check_col(self,col):
        return self.check_block([self.puzzle[row][col] for row in range(9)])

    def check_square(self,row,col):
        return self.check_block(
            [self.puzzle[r][c]
            for r in range(row*3, (row+1)*3)
            for c in range(col*3, (col+1)*3)])

    def check_redundancy(self, row, col, number):
        count = 0
        index = [[0, 1, 2], [3, 4, 5], [6, 7, 8]]

        # Find the answer's row, column, and square elements to check if the answer is redundant
        row_elements = [self.puzzle[row][c] for c in range(9)]
        col_elements = [self.puzzle[r][col] for r in range(9)]
        square_elements = []
        for i in index:
            if row in i:
                row_index = index.index(i)
            if col in i:
                col_index = index.index(i)
        for i in index[row_index]:
            for j in index[col_index]:
                square_elements.append(self.puzzle[i][j])
        
        for element in row_elements:
            if number == element:
                count += 1
            if count > 1:
                return True
        count = 0

        for element in col_elements:
            if number == element:
                count += 1
            if count > 1:
                return True
        count = 0

        for element in square_elements:
            if number == element:
                count += 1
            if count > 1:
                return True
        count = 0

        return False

class GameUI(Frame):
    """
    The Tkinter UI, responsible for drawing the board and accepting user input.
    """
    def __init__(self, parent, game):
       self.game = game
       self.parent = parent
       self.row, self.col = -1, -1

       Frame.__init__(self, parent)
       self.__initUI()

    def __initUI(self):
        self.parent.title("Sudoku")
        self.pack(fill=BOTH)
        self.canvas = Canvas(self,
                             width=WIDTH,
                             height=HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)

        clear_button = Button(self,
                              text="Clear Answers",
                              fg = "black",
                              command=self.__clear_answers)
        clear_button.pack(fill=BOTH, side=BOTTOM)

        new_game_button = Button(self,
                                 text="New Game",
                                 fg = "black",   
                                 command=self.__new_game)

        new_game_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_puzzle()

        self.canvas.bind("<Button-1>", self.__cell_clicked)
        self.canvas.bind("<Key>", self.__key_pressed)
        self.canvas.bind("<BackSpace>", self.__delete)

    def __draw_grid(self):
        """
        Draws grid divided with blue lines into 3x3 squares
        """
        for i in range(10):
            color = "blue" if i % 3 == 0 else "gray"

            x0 = MARGIN + i * SIDE
            y0 = MARGIN
            x1 = MARGIN + i * SIDE
            y1 = HEIGHT - MARGIN
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

            x0 = MARGIN
            y0 = MARGIN + i * SIDE
            x1 = WIDTH - MARGIN
            y1 = MARGIN + i * SIDE
            self.canvas.create_line(x0, y0, x1, y1, fill=color)

    def __draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = MARGIN + j * SIDE + SIDE // 2
                    y = MARGIN + i * SIDE + SIDE // 2
                    original = self.game.start_puzzle[i][j]
                    if answer == original:
                        color = "black"
                    elif answer != original and self.game.check_redundancy(i, j, answer):
                        color = "red"
                    else:
                        color = "sea green"
                    self.canvas.create_text(x, y, text=answer, tags="numbers", fill=color)
    
    def __draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0 = MARGIN + self.col * SIDE + 1
            y0 = MARGIN + self.row * SIDE + 1
            x1 = MARGIN + (self.col + 1) * SIDE - 1
            y1 = MARGIN + (self.row + 1) * SIDE - 1
            self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", tags="cursor")

    def __cell_clicked(self, event):
        x, y = event.x, event.y
        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            row, col = (y - MARGIN) // SIDE, (x - MARGIN) // SIDE

            # if cell was selected already - deselect it
            if (row, col) == (self.row, self.col):
                self.row, self.col = -1, -1
            elif self.game.puzzle[row][col] != self.game.start_puzzle[row][col] or self.game.puzzle[row][col] == 0:
                self.row, self.col = row, col
        else:
            self.row, self.col = -1, -1
        self.__draw_cursor()
    
    def __key_pressed(self, event):
        if self.row >= 0 and self.col >= 0 and event.char in "123456789":
            self.game.puzzle[self.row][self.col] = int(event.char)
            self.col, self.row = -1, -1
            self.__draw_puzzle()
            self.__draw_cursor()
        if self.game.check_win():
                self.__draw_victory()
    
    def __delete(self, event):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            if self.game.puzzle[self.row][self.col] != self.game.start_puzzle[self.row][self.col]:
                self.game.puzzle[self.row][self.col] = 0
                self.__draw_puzzle()

    def __draw_victory(self):
        # create a oval (which will be a circle)
        x0 = y0 = MARGIN + SIDE * 2
        x1 = y1 = MARGIN + SIDE * 7
        self.canvas.create_oval(
            x0, y0, x1, y1,
            tags="victory", fill="dark orange", outline="orange"
        )
        # create text
        x = y = MARGIN + 4 * SIDE + SIDE // 2
        self.canvas.create_text(
            x, y,
            text="You win!", tags="victory",
            fill="white", font=("Arial", 32)
        )
    
    def __clear_answers(self):
        self.canvas.delete("victory")
        self.game.start()
        self.__draw_puzzle()

    def __new_game(self):
        pass

if __name__ == '__main__':
    board_file = copyGrid
    game = Game(board_file)
    game.start()
    app = Tk()
    GameUI(app, game)
    app.mainloop()
