from tkinter import messagebox
import tkinter as tk
import random
import json


class App():
    def __init__(self, root, db_path, w=1000, h=600, g=50):
        self.root = root
        self.db_path = db_path
        self.w, self.h, self.g = w, h, g
        self.points, self.ids = {}, {}

        self.root.resizable(False, False)
        self.root.title("PairView")
        frame = tk.Frame(root, padx=15, pady=10)
        frame.pack()
        
        # Plota o canvas e linhas/textos de referência
        self.canvas = tk.Canvas(frame, background='white', width=w, height=h)
        self.canvas.grid(row=1, column=0, columnspan=3, rowspan=3)
        self.canvas.create_line(0, h/2, w, h/2, arrow=tk.LAST, width=2) # Eixo X
        self.canvas.create_line(w/2, 0, w/2, h, arrow=tk.FIRST, width=2) # Eixo Y
        self.canvas.create_text(w/2-11, h/2+7, text='0,0', font=("Arial", 10)) # Marcação da origem
        self.canvas.create_text(w/2+10, 10, text=f'X', font=("Arial", 10, "bold")) # Marcação do eixo X
        self.canvas.create_text(w-8, h/2-10, text=f'Y', font=("Arial", 10, "bold")) # Marcação do eixo Y
        self.canvas.create_text(w/2-11, h/2+1-g, text=f'+{g}', font=("Arial", 8)) # Referência do grid (X)
        self.canvas.create_text(w/2-3+g, h/2+7, text=f'+{g}', font=("Arial", 8)) # Referência do grid (Y)
        self.canvas.create_text(w-12, h/2+10, text=f'+{int(w/2)}', font=("Arial", 8)) # X máximo
        self.canvas.create_text(14, h/2+10, text=f'-{int(w/2)}', font=("Arial", 8)) # X mínimo
        self.canvas.create_text(w/2-16, 8, text=f'+{int(h/2)}', font=("Arial", 8)) # Y máximo
        self.canvas.create_text(w/2-16, h-5, text=f'-{int(h/2)}', font=("Arial", 8)) # Y mínimo

        for x in range(0, w, g):
            self.canvas.create_line(x, 0, x, h, fill="gray", dash=(2, 2)) # Plota grids verticais
        for y in range(0, h, g):
            self.canvas.create_line(0, y, w, y, fill="gray", dash=(2, 2)) # Plota grids horizontais

        # Ações de click no canvas
        self.canvas.bind("<Button-1>", self.on_add)
        self.canvas.bind("<Button-2>", self.on_edit)
        self.canvas.bind("<Button-3>", self.on_rem)
        
        # Demais elementos da interface
        title = tk.Label(frame, text='idk')
        btn_add = tk.Button(frame, text="Adicionar Ponto", width=20, command=self.on_add)
        btn_edit = tk.Button(frame, text="Editar Ponto(s)", width=20, command=self.on_edit)
        btn_rem = tk.Button(frame, text="Remover Ponto(s)", width=20, command=self.on_rem)
        btn_gen = tk.Button(frame, text="Gerar Pontos", width=20, command=self.on_gen)
        btn_save = tk.Button(frame, text="Salvar em JSON", width=20, command=self.on_save)
        btn_load = tk.Button(frame, text="Carregar JSON", width=20, command=self.on_load)
        btn_start = tk.Button(frame, text="Iniciar Algoritmo", width=30, command=self.on_start)
        btn_exit = tk.Button(frame, text="Sair", width=30, command=self.root.destroy)

        # Ajuste dos elementos no grid
        title.grid(row=0, column=1)
        btn_add.grid(row=4, column=0, padx=5, pady=5, sticky='w')
        btn_edit.grid(row=5, column=0, padx=5, pady=5, sticky='w')
        btn_rem.grid(row=6, column=0, padx=5, pady=5, sticky='w')
        btn_gen.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        btn_save.grid(row=5, column=0, padx=5, pady=5, sticky='e')
        btn_load.grid(row=6, column=0, padx=5, pady=5, sticky='e')
        btn_start.grid(row=4, column=2, padx=5, pady=5)
        btn_exit.grid(row=6, column=2, padx=5, pady=5)

        


    def on_add(self, event=None):
        canvas_x, canvas_y = (event.x, event.y) if event else (0, 0)
        x, y = (canvas_x - self.w/2), (self.h/2 - canvas_y)

        name = self.name()
        name_pos = self.name_fix(canvas_x, canvas_y)
        
        point_id = self.canvas.create_oval(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5, fill="blue")
        text_id = self.canvas.create_text(canvas_x+name_pos[0], canvas_y+name_pos[1], angle=name_pos[2], text=name, font=("Arial", 8))

        self.points[name] = [x, y]
        self.ids[name] = [point_id, text_id]
    

    def on_edit(self):
        pass


    def on_rem(self, event=None):
        # Coletar coordenadas do clique
        x, y = event.x, event.y
        
        # Verificar se o clique está dentro de algum ponto
        for ponto_id, ponto in self.pontos.items():
            if (x - 5 <= ponto["x_cartesiano"] + 300 <= x + 5) and (y - 5 <= 300 - ponto["y_cartesiano"] <= y + 5):
                # Remover ponto e nome
                self.canvas.delete(ponto["ponto_id"])
                self.canvas.delete(ponto["texto_id"])
                del self.pontos[ponto_id]
                break

    def on_start(self):
        pass

    def on_gen(self):
        points = {}
        x = random.sample(range(-500, 501), 100)  # coordenadas únicas para x
        y = random.sample(range(-300, 301), 100)  # coordenadas únicas para y

        for i in range(50):
            points[f"Ponto {i+1}"] = [x[i], y[i]]

        #for i in pontos.items():
        #    print(f'    "{i[0]}": {i[1]},')


    def on_save(self):
        try:
            with open(self.db_path, 'w') as file:
                json.dump(self.points, file, ensure_ascii=False, indent=4)
            messagebox.showinfo('Pontos salvos', f'Os pontos foram salvos no arquivo "{self.db_path}".')
        except Exception:
            messagebox.showwarning('Aviso', f'Não foi possível salvar em "{self.db_path}".')
            return

    
    def on_load(self):
        try:
            with open(self.db_path, 'r') as file:
                self.points = json.load(file)

            for point in self.points.items():
                canvas_x, canvas_y = (point[1][0] + self.w/2), (self.h/2 - point[1][1])
                name_pos = self.name_fix(canvas_x, canvas_y)

                point_id = self.canvas.create_oval(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5, fill="blue")
                text_id = self.canvas.create_text(canvas_x+name_pos[0], canvas_y+name_pos[1], angle=name_pos[2], text=point[0], font=("Arial", 8))
                self.ids[point[0]] = [point_id, text_id]

            messagebox.showinfo('Carregamento concluído', f'Os pontos foram carregados no plano!')

        except Exception:
            messagebox.showwarning('Aviso', f'Não foi possível carregar "{self.db_path}".')
            return
        



    def name(self):
        i = 1
        while f'Ponto {i}' in self.points.keys(): i += 1
        return f'Ponto {i}'
    

    def name_fix(self, x, y):
        name_pos = [0, -10, 0] # [x, y, angle]
        if x > self.w-10:  name_pos[:] = [-10, 0, 90]
        if x < 10:         name_pos[:] = [+10, 0, -90]
        if y < 13:         name_pos[1] = +10

        return name_pos