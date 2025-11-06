from gui.menu import App
import tkinter as tk


DB_FILE = 'db/database.json'
board_width = 1000
board_height = 600
board_grid = 50


if __name__ == '__main__':
    root = tk.Tk()
    app = App(root, DB_FILE, w=board_width, h=board_height, g=board_grid)
    root.mainloop()