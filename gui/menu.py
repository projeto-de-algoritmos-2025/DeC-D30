from tkinter import messagebox, simpledialog
import tkinter as tk
import random
import json


class App():
    def __init__(self, root, db_path, w=1000, h=600, g=50, max=1000):
        self.root = root
        self.db_path = db_path
        self.w, self.h, self.g = w, h, g
        self.max = max
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
        self.canvas.bind("<Button-1>", lambda event: self.on_add_edit(self.add_point, event))
        self.canvas.bind("<Button-2>", lambda event: self.on_add_edit(self.edit_point, event))
        self.canvas.bind("<Button-3>", self.on_rem)
        
        # Demais elementos da interface
        title = tk.Label(frame, text='idk')
        btn_add = tk.Button(frame, text="Adicionar Ponto", width=20, command=lambda: self.on_add_edit(self.add_point))
        btn_edit = tk.Button(frame, text="Editar Ponto(s)", width=20, command=lambda: self.on_add_edit(self.edit_point))
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

    
    

    def on_add_edit(self, action, event=None):
        if len(self.points) == self.max:
            messagebox.showwarning('Erro', f'Você atingiu o número máximo de pontos ({self.max})!')
            return

        canvas_x, canvas_y = (event.x, event.y) if event else (self.w/2, self.h/2)
        win_pos = f'+{event.x_root-50}+{event.y_root-150}' if event else None
        x, y, name = int(canvas_x - self.w/2), int(self.h/2 - canvas_y), self.default_name()

        win = tk.Toplevel(self.root)
        win.geometry(win_pos)
        win.title(f"Adicionar Ponto")
        win.resizable(False, False)
        win.grab_set()
        
        frame = tk.Frame(win, padx=8, pady=8)
        frame.pack()
                
        def validate_str(char, string):
            return len(string) <= 20 or char == ''
        
        def validate_num(char, string):
            if (len(string) <= 9) or (char == ''):
                if (char.isdigit()) or (char=='.' and string.count('.')==0) or (char==''):
                    return True
            return False

        val_str, val_num = win.register(validate_str), win.register(validate_num)

        tk.Label(frame, text="Nome do Ponto:").grid(row=0, column=0, columnspan=2)
        tk.Label(frame, text="X   ").grid(row=2, column=0)
        tk.Label(frame, text="   Y").grid(row=2, column=1)

        x, y, name = tk.StringVar(value=x), tk.StringVar(value=y), tk.StringVar(value=name)
        tk.Entry(frame, width=21, textvariable=name, validate="key", validatecommand=(val_str, "%S", "%P")) \
            .grid(row=1, column=0, columnspan=2, pady=(0, 6))
        tk.Entry(frame, width=9, textvariable=x, validate="key", validatecommand=(val_num, "%S", "%P")) \
            .grid(row=3, column=0, pady=(0, 10), sticky='w')
        tk.Entry(frame, width=9, textvariable=y, validate="key", validatecommand=(val_num, "%S", "%P")) \
            .grid(row=3, column=1, pady=(0, 10), sticky='e')

        tk.Button(frame, text="Adicionar", width=8, command=lambda: action(float(x.get()), float(y.get()), name.get(), win)) \
            .grid(row=4, column=0, sticky='sw')
        tk.Button(frame, text="Voltar", width=8, command=win.destroy) \
            .grid(row=4, column=1, sticky='se')


    def add_point(self, x, y, name, win):
        if not self.verify_point(x, y, name, win): return
        point_id, text_id = self.plot(x, y, name)

        self.points[name] = [x, y]
        self.ids[name] = [point_id, text_id]

        win.destroy()
        messagebox.showinfo('Ponto adicionado', f'O ponto "{name}" foi adicionado no plano.')


    def edit_point(self, x, y, name, win):
        pass

    def on_rem(self, event=None):
        if event:
            x, y = int(event.x-self.w/2), int(self.h/2-event.y)
            for point in self.points.items():
                if (x-5 <= point[1][0] <= x+5) and (y-5 <= point[1][1] <= y+5):
                    self.canvas.delete(self.ids[point[0]][0]), self.canvas.delete(self.ids[point[0]][1])
                    del self.points[point[0]], self.ids[point[0]]
                    return
        else:
            win = tk.Toplevel(self.root)
            win.title(f"Remover Ponto(s)")
            win.resizable(False, False)
            win.grab_set()

            frame = tk.Frame(win, padx=8, pady=8)
            frame.pack()

            listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=10, width=26)
            listbox.grid(row=1, column=0, pady=5, columnspan=2)

            scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listbox.yview)
            scrollbar.grid(row=1, column=1, pady=5, sticky='nse')
            listbox.configure(yscrollcommand=scrollbar.set)

            def select_all():
                if len(listbox.curselection()) == len(self.points): listbox.select_clear(0, tk.END)
                else: listbox.select_set(0, tk.END)

            def refresh_points():
                listbox.delete(0, tk.END)
                for point in self.points.keys():
                    listbox.insert(tk.END, point)

            def delete_points():
                if not listbox.curselection():
                    messagebox.showwarning('Seleção Vazia', f'Nenhum ponto foi selecionado!', parent=win)
                    return
                if not messagebox.askyesno("Apagar?", f"Deseja apagar o(s) ponto(s) selecionado(s)?", parent=win):
                    return
                
                removing = [listbox.get(i) for i in listbox.curselection()]
                for point in removing:
                    self.canvas.delete(self.ids[point][0]), self.canvas.delete(self.ids[point][1])
                    del self.points[point], self.ids[point]

                messagebox.showinfo('Pontos Apagados', f'Os pontos selecionados foram apagados.', parent=win)
                refresh_points()

            tk.Label(frame, text='Selecione o(s) ponto(s)\npara remoção:').grid(row=0, column=0, columnspan=2)
            tk.Button(frame, text="A", font=("Arial", 8), width=1, height=1, command=select_all).place(x=2, y=28, width=14, height=14)
            tk.Button(frame, text="Remover", width=10, command=delete_points).grid(row=2, column=0, sticky='sw')
            tk.Button(frame, text="Voltar", width=10, command=win.destroy).grid(row=2, column=1, sticky='se')

            refresh_points()

            

    def on_start(self):
        pass

    def on_gen(self):
        n = simpledialog.askinteger('Gerar Pontos', 'Número de pontos:')
        if (len(self.points)+n) >= self.max:
            messagebox.showerror('Erro', f'Número máximo de pontos ({self.max}) estourado!')
            return

        points = self.points.values()
        for i in range(n):            
            while True:
                x = random.randint(int(-self.w/2), int(self.w/2))
                y = random.randint(int(-self.h/2), int(self.h/2))
                if not self.check_conflict(x, y): break

            name = self.default_name()
            point_id, text_id = self.plot(x, y, name)
            
            self.points[name] = [x, y]
            self.ids[name] = [point_id, text_id]
        
        messagebox.showinfo('Pontos Gerados', f'{n} novos pontos foram gerados no plano.')




    def on_save(self):
        try:
            with open(self.db_path, 'w') as file:
                json.dump(self.points, file, ensure_ascii=False, indent=4)
            messagebox.showinfo('Pontos salvos', f'Os pontos foram salvos no arquivo "{self.db_path}".')
        except Exception:
            messagebox.showerror('Aviso', f'Não foi possível salvar em "{self.db_path}".')
            return

    
    def on_load(self):
        try:
            with open(self.db_path, 'r') as file:
                self.points = json.load(file)

            for point in self.points.items():
                point_id, text_id = self.plot(point[1][0], point[1][1], point[0])
                self.ids[point[0]] = [point_id, text_id]

            messagebox.showinfo('Carregamento concluído', f'Os pontos foram carregados no plano!')

        except Exception:
            messagebox.showerror('Aviso', f'Não foi possível carregar "{self.db_path}".')
            return
        



    def default_name(self, i = 1):
        while f'Ponto {i}' in self.points.keys(): i += 1
        return f'Ponto {i}'
    
    def plot(self, x, y, name):
        canvas_x, canvas_y = (x + self.w/2), (self.h/2 - y)
        name_pos = self.name_fix(canvas_x, canvas_y)

        point_id = self.canvas.create_oval(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5, fill="blue")
        text_id = self.canvas.create_text(canvas_x+name_pos[0], canvas_y+name_pos[1], angle=name_pos[2], text=name, font=("Arial", 8))

        return point_id, text_id
    
    def check_boundary(self, x, y):
        return (x < -self.w/2) or (self.w/2 < x) or (y < -self.h/2) or (self.h/2 < y)

    def check_conflict(self, x, y):
        return [x, y] in self.points.values()
    
    def check_name(self, name):
        return name in self.points.keys()
    
    def verify_point(self, x, y, name, win):
        if self.check_boundary(x, y):
            messagebox.showwarning('Erro', f'As coordenadas ({x}, {y}) estão fora do limite do plano.', parent=win)
        elif self.check_conflict(x, y):
            messagebox.showwarning('Erro', f'O ponto ({x}, {y}) já existe no plano.', parent=win)
        elif self.check_name(name):
            messagebox.showwarning('Erro', f'Já existe um ponto com o nome "{name}".', parent=win)
        else:
            return True
        return False
        


    def name_fix(self, x, y):
        name_pos = [0, -10, 0] # [x, y, angle]
        if x > self.w-10:  name_pos[:] = [-10, 0, 90]
        if x < 10:         name_pos[:] = [+10, 0, -90]
        if y < 13:         name_pos[1] = +10

        return name_pos