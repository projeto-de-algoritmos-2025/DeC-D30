from gui.menu import Main
import tkinter as tk


DB_FILE = 'db/database.json'
board_width = 1000
board_height = 600
board_grid = 50
max_points = 1000


if __name__ == '__main__':
    root = tk.Tk()
    app = Main(root, DB_FILE, w=board_width, h=board_height, g=board_grid, max=max_points)
    root.mainloop()