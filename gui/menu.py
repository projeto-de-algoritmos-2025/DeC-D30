from src.closest_pair import ClosestPair
from tkinter import messagebox, simpledialog
import tkinter as tk
import threading
import random
import json
import os



class Main():
    def __init__(self, root, db_path, w=1000, h=600, g=50, max=1000):
        self.root = root
        self.db_path, self.max = tk.StringVar(value=db_path), tk.StringVar(value=max)
        self.w, self.h, self.g = tk.StringVar(value=w), tk.StringVar(value=h), tk.StringVar(value=g)
        
        self.root.resizable(False, False)
        self.root.title("PairView")
        self.frame = tk.Frame(self.root, padx=8, pady=8)
        self.frame.pack()

        def validate_num(string): return (string.isdigit() or not string)
        val_num = self.root.register(validate_num)

        tk.Label(self.frame, text="Bem Vindo(a) ao\nPairView!", font='sylfaen').grid(row=0, column=0, columnspan=2, pady=(0, 6))
        tk.Label(self.frame, text="Path do JSON:").grid(row=1, column=0, columnspan=2, sticky='w')
        tk.Label(self.frame, text="Largura do Plano:").grid(row=3, column=0, columnspan=2, sticky='w')
        tk.Label(self.frame, text="Altura do Plano:").grid(row=5, column=0, columnspan=2, sticky='w')
        tk.Label(self.frame, text="Tamanho da Grade:").grid(row=7, column=0, columnspan=2, sticky='w')
        tk.Label(self.frame, text="Máximo de Pontos:").grid(row=9, column=0, columnspan=2, sticky='w')

        tk.Entry(self.frame, textvariable=self.db_path).grid(row=2, column=0, columnspan=2)
        tk.Entry(self.frame, textvariable=self.w, validate="key", validatecommand=(val_num, "%P")) \
            .grid(row=4, column=0, columnspan=2)
        tk.Entry(self.frame, textvariable=self.h, validate="key", validatecommand=(val_num, "%P")) \
            .grid(row=6, column=0, columnspan=2)
        tk.Entry(self.frame, textvariable=self.g, validate="key", validatecommand=(val_num, "%P")) \
            .grid(row=8, column=0, columnspan=2)
        tk.Entry(self.frame, textvariable=self.max, validate="key", validatecommand=(val_num, "%P")) \
            .grid(row=10, column=0, columnspan=2)

        tk.Button(self.frame, text='Iniciar', width=8, command=self.start) \
            .grid(row=11, column=0, pady=(10, 0), sticky='sw')
        tk.Button(self.frame, text="Sair", width=8, command=self.root.destroy) \
            .grid(row=11, column=1, pady=(10, 0), sticky='se')
        
    def start(self):
        try:
            db_path, max = self.db_path.get(), int(self.max.get())
            width, height, grid = int(self.w.get()), int(self.h.get()), int(self.g.get())
            App(self.root, db_path, width, height, grid, max)
            self.frame.destroy()
        except Exception:
            messagebox.showerror('Erro', f'Ocorreu um erro.')
            return



class App():
    def __init__(self, root, db_path, w=1000, h=600, g=50, max=1000):
        self.root = root
        self.db_path, self.max = db_path, max
        self.w, self.h, self.g = int(w/2), int(h/2), g
        self.points, self.ids = {}, {}
        self.closest = [float('inf'), {(None, None)}]

        self.frame = tk.Frame(self.root, padx=15, pady=10)
        self.frame.pack()
        
        # Plota o canvas e linhas/textos de referência
        self.canvas = tk.Canvas(self.frame, background='white', width=2*self.w, height=2*self.h)
        self.canvas.grid(row=1, column=0, rowspan=3, columnspan=3, pady=10)
        self.canvas.create_line(0, self.h, 2*self.w, self.h, arrow=tk.LAST, width=2) # Eixo X
        self.canvas.create_line(self.w, 0, self.w, 2*self.h, arrow=tk.FIRST, width=2) # Eixo Y
        self.canvas.create_text(self.w-11, self.h+7, text='0,0', font=("Arial", 10)) # Marcação da origem
        self.canvas.create_text(self.w+10, 10, text=f'X', font=("Arial", 10, "bold")) # Marcação do eixo X
        self.canvas.create_text(2*self.w-8, self.h-10, text=f'Y', font=("Arial", 10, "bold")) # Marcação do eixo Y
        self.canvas.create_text(self.w-11, self.h+1-self.g, text=f'+{self.g}', font=("Arial", 8)) # Referência do grid (X)
        self.canvas.create_text(self.w-3+self.g, self.h+7, text=f'+{self.g}', font=("Arial", 8)) # Referência do grid (Y)
        self.canvas.create_text(2*self.w-12, self.h+10, text=f'+{self.w}', font=("Arial", 8)) # X máximo
        self.canvas.create_text(14, self.h+10, text=f'-{self.w}', font=("Arial", 8)) # X mínimo
        self.canvas.create_text(self.w-16, 8, text=f'+{self.h}', font=("Arial", 8)) # Y máximo
        self.canvas.create_text(self.w-16, 2*self.h-5, text=f'-{self.h}', font=("Arial", 8)) # Y mínimo

        for x in range(0, 2*self.w, self.g):
            self.canvas.create_line(x, 0, x, 2*self.h, fill="gray", dash=(2, 2)) # Plota grids verticais
        for y in range(0, 2*self.h, self.g):
            self.canvas.create_line(0, y, 2*self.w, y, fill="gray", dash=(2, 2)) # Plota grids horizontais

        # Ações de click no canvas
        self.canvas.bind("<Button-1>", self.on_add)
        self.canvas.bind("<Button-2>", self.on_edit)
        self.canvas.bind("<Button-3>", self.on_rem)

        # Demais elementos da interface
        title = tk.Label(self.frame, text='Visualização Interativa: Par de Pontos Mais Próximo',
                         font=('sylfaen', 15, "italic"))
        self.screen = [
            tk.Canvas(self.frame, height=96, background='lightgray'),
            tk.Label(self.frame, text=f'N° de Pontos: {len(self.points)}',
                     bg="lightgray", font=('Cambria', 10)),
            tk.Label(self.frame, text=f'Menor Distância:  {self.closest[0]:.4f}\nPontos: {str(self.closest[1])[1:-1]}',
                     bg="lightgray", font=('Cambria', 10)),
            tk.Label(self.frame, text='Clique em "Iniciar Algoritmo" para executar o algoritmo.',
                     bg="lightgray", font=('Bahnschrift SemiBold SemiConden', 12))
        ]
        self.buttons = [
            tk.Button(self.frame, text="Adicionar Ponto", width=15, command=self.on_add),
            tk.Button(self.frame, text="Remover Ponto(s)", width=15, command=self.on_rem),
            tk.Button(self.frame, text="Gerar Pontos", width=31, command=self.on_gen),
            tk.Button(self.frame, text="Salvar em JSON", width=15, command=self.on_save),
            tk.Button(self.frame, text="Carregar JSON", width=15, command=self.on_load),
            tk.Button(self.frame, text="Iniciar Algoritmo", width=31, command=self.on_start),
            tk.Button(self.frame, text="Sair", width=31, command=self.root.destroy),
        ]

        # Ajuste dos elementos no grid
        title.grid(row=0, column=1, sticky='n')
        self.screen[0].grid(row=4, column=1, rowspan=3, sticky="we")
        self.screen[1].grid(row=6, column=1, padx=4, sticky="w")
        self.screen[2].grid(row=5, column=1, padx=4, pady=(0, 7), rowspan=2, sticky="se")
        self.screen[3].grid(row=4, column=1, rowspan=2)
        self.buttons[0].grid(row=4, column=0, pady=5, sticky='w')
        self.buttons[1].grid(row=4, column=0, padx=(114, 0), pady=5, sticky='w')
        self.buttons[2].grid(row=5, column=0, padx=(1, 0), pady=5, sticky='w')
        self.buttons[3].grid(row=6, column=0, pady=5, sticky='w')
        self.buttons[4].grid(row=6, column=0, padx=(114, 0), pady=5, sticky='w')
        self.buttons[5].grid(row=4, column=2, pady=5, sticky='e')
        self.buttons[6].grid(row=6, column=2, padx=(0, 1), pady=5, sticky='e')

    
    def on_add(self, event=None):
        if len(self.points) == self.max:
            messagebox.showwarning('Erro', f'Você atingiu o número máximo de pontos ({self.max})!')
            return
        
        canvas_x, canvas_y = (event.x, event.y) if event else (self.w, self.h)
        x, y, name = (canvas_x-self.w), (self.h-canvas_y), self.default_name()
        self.edit_window(x, y, name, 'add', event)
        

    def on_edit(self, event):
        click = self.click(event)
        if not click: return

        x, y = self.points[click][0], self.points[click][1]
        self.edit_window(x, y, click, 'edit', event)
    

    def edit_window(self, x, y, old_name, action, event=None):
        x, y = tk.StringVar(value=x), tk.StringVar(value=y)
        new_name = tk.StringVar(value=old_name)
        if action == 'add':
            string, old_name = 'Adicionar', None
        elif action == 'edit':
            string = 'Editar'

        win_pos = f'+{event.x_root-50}+{event.y_root-150}' if event else None
        win = tk.Toplevel(self.root)
        win.geometry(win_pos)
        win.title(f"{string} Ponto")
        win.resizable(False, False)
        win.grab_set()
        
        frame = tk.Frame(win, padx=8, pady=8)
        frame.pack()

        def validate_str(char, string):
            return len(string) <= 20 or char == ''

        def validate_num(char, string):
            try: return (len(string) <= 10) and ((not string) or float(string+'1'))
            except ValueError: return False

        val_str, val_num = win.register(validate_str), win.register(validate_num)

        tk.Label(frame, text="Nome do Ponto:").grid(row=0, column=0, columnspan=2)
        tk.Label(frame, text="X   ").grid(row=2, column=0)
        tk.Label(frame, text="   Y").grid(row=2, column=1)

        tk.Entry(frame, width=21, textvariable=new_name, validate="key", validatecommand=(val_str, "%S", "%P")) \
            .grid(row=1, column=0, columnspan=2, pady=(0, 6))
        tk.Entry(frame, width=9, textvariable=x, validate="key", validatecommand=(val_num, "%S", "%P")) \
            .grid(row=3, column=0, pady=(0, 10), sticky='w')
        tk.Entry(frame, width=9, textvariable=y, validate="key", validatecommand=(val_num, "%S", "%P")) \
            .grid(row=3, column=1, pady=(0, 10), sticky='e')

        tk.Button(frame, text=string, width=8, command=lambda: self.add_point(x.get(), y.get(), new_name.get(), old_name, win)) \
            .grid(row=4, column=0, sticky='sw')
        tk.Button(frame, text="Voltar", width=8, command=win.destroy) \
            .grid(row=4, column=1, sticky='se')


    def add_point(self, x, y, new_name, old_name, win):
        if not self.verify_point(x, y, new_name, old_name, win): return

        x, y = float(x), float(y)
        if x.is_integer(): x = int(x) # Elimina casas decimais se for um int
        if y.is_integer(): y = int(y) # Elimina casas decimais se for um int

        # Deleta a versão antiga do ponto, se estiver editando
        if old_name:
            string = 'editado'
            self.canvas.delete(self.ids[old_name][0]), self.canvas.delete(self.ids[old_name][1])
            del self.points[old_name], self.ids[old_name]
        else: string = 'adicionado'

        point_id, text_id = self.plot(x, y, new_name)
        self.points[new_name], self.ids[new_name] = [x, y], [point_id, text_id]

        self.screen[1].config(text=f'N° de Pontos: {len(self.points)}')
        win.destroy()
        #messagebox.showinfo(f'Ponto {string}', f'O ponto "{new_name}" foi {string} no plano.')


    def on_rem(self, event=None):
        click = self.click(event)

        if click:
            self.canvas.delete(self.ids[click][0]), self.canvas.delete(self.ids[click][1])
            del self.points[click], self.ids[click]
            self.screen[1].config(text=f'N° de Pontos: {len(self.points)}')
        elif not event:
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

            def alph_order():
                self.points = dict(sorted(self.points.items(), key=lambda item: item[0]))
                refresh_points()

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
                if not messagebox.askyesno("Apagar?", f"Deseja apagar ({len(listbox.curselection())}) " \
                                           "ponto(s) selecionado(s)?", parent=win):
                    return
                
                removing = [listbox.get(i) for i in listbox.curselection()]
                for point in removing:
                    self.canvas.delete(self.ids[point][0]), self.canvas.delete(self.ids[point][1])
                    del self.points[point], self.ids[point]

                refresh_points()
                self.screen[1].config(text=f'N° de Pontos: {len(self.points)}')
                messagebox.showinfo('Pontos Apagados', f'Os pontos selecionados foram apagados.', parent=win)

            tk.Label(frame, text='Selecione o(s) ponto(s)\npara remoção:').grid(row=0, column=0, columnspan=2)
            tk.Button(frame, text="A", font=("Arial", 8), width=1, height=1, command=alph_order).place(x=1, y=28, width=14, height=14)
            tk.Button(frame, text="S", font=("Arial", 8), width=1, height=1, command=select_all).place(x=16, y=28, width=14, height=14)
            tk.Button(frame, text="Remover", width=10, command=delete_points).grid(row=2, column=0, sticky='sw')
            tk.Button(frame, text="Voltar", width=10, command=win.destroy).grid(row=2, column=1, sticky='se')

            refresh_points()


    def on_gen(self):
        n = simpledialog.askinteger('Gerar Pontos', 'Número de pontos:')
        if n<0:
            messagebox.showerror('Erro', f'O número de pontos não pode ser negativo!')
            return
        if (len(self.points)+n) > self.max:
            messagebox.showerror('Erro', f'Número máximo de pontos ({self.max}) estourado!')
            return

        while n:
            x = random.randint(-self.w, self.w)
            y = random.randint(-self.h, self.h)
            if not self.check_conflict(x, y):
                name = self.default_name()
                point_id, text_id = self.plot(x, y, name)
                
                self.points[name] = [x, y]
                self.ids[name] = [point_id, text_id]
                n -= 1

        self.screen[1].config(text=f'N° de Pontos: {len(self.points)}')
        messagebox.showinfo('Pontos Gerados', f'Novos pontos gerados com sucesso!')


    def on_save(self):
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
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

            self.screen[1].config(text=f'N° de Pontos: {len(self.points)}')
            messagebox.showinfo('Carregamento concluído', f'Os pontos foram carregados no plano!')

        except Exception:
            messagebox.showerror('Aviso', f'Não foi possível carregar "{self.db_path}".')
            return
        

    # Prepara a interface gráfica para a execução do algoritmo
    def on_start(self):
        if len(self.points)==0 or len(self.points)==1:
            messagebox.showwarning('Erro', f'O plano deve ter no mínimo 2 pontos para a execução do algoritmo!')
            return

        for button in self.buttons:
            button.config(state="disabled")

        self.canvas.unbind("<Button-1>")
        self.canvas.unbind("<Button-2>")
        self.canvas.unbind("<Button-3>")

        self.speed = tk.IntVar(value=10)
        self.buttons[5].destroy()
        self.buttons[5] = [
            tk.Label(self.frame, text='Velocidade', font=("Arial", 7)),
            tk.Spinbox(self.frame, from_=1, to=20, textvariable=self.speed, state="normal", width=9),
            tk.Button(self.frame, text="Pausar", width=9, command=self.on_pause),
            tk.Button(self.frame, text="Interromper", width=9, command=self.on_stop)
        ]

        self.buttons[5][0].grid(row=4, column=2, padx=(0, 169), sticky='ne')
        self.buttons[5][1].grid(row=4, column=2, padx=(0, 159), sticky='se')
        self.buttons[5][2].grid(row=4, column=2, padx=(0, 80), sticky='e')
        self.buttons[5][3].grid(row=4, column=2, padx=(0, 1), sticky='e')

        self.stop_flag = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()
        
        self.execution = threading.Thread(target=self.start)
        self.execution.start()


    # Pausa a thread de execução do algoritmo
    def on_pause(self):
            if self.pause_event.is_set():
                self.pause_event.clear()
                self.buttons[5][2].config(text="Despausar")
            else:
                self.pause_event.set()
                self.buttons[5][2].config(text="Pausar")


    # Interrompe o algoritmo (utilizando a flag de parada)
    def on_stop(self):
        self.stop_flag.set()
        self.pause_event.set()
        self.speed.set(20)


    # Gera um nome "default" para um ponto
    def default_name(self, i = 1):
        while f'Ponto {i:02}' in self.points.keys(): i += 1
        return f'Ponto {i:02}'


    # Checa se já existe um ponto nessas coordenadas
    def check_conflict(self, x, y, old_name=None):
        same_point = True if not old_name else (x!=self.points[old_name][0] or y!=self.points[old_name][1])
        return ([x, y] in self.points.values()) and (same_point)


    # Plota um ponto e seu texto no plano
    def plot(self, x, y, name):
        canvas_x, canvas_y = (self.w + x), (self.h - y)
        name_pos = self.name_fix(canvas_x, canvas_y)

        point_id = self.canvas.create_oval(canvas_x-5, canvas_y-5, canvas_x+5, canvas_y+5, fill="blue")
        text_id = self.canvas.create_text(canvas_x+name_pos[0], canvas_y+name_pos[1], angle=name_pos[2], text=name, font=("Arial", 8))

        return point_id, text_id


    # Verifica se 'x', 'y' e 'name' são válidas no contexto do sistema
    def verify_point(self, x, y, name, old_name, win):
        try: x, y = float(x), float(y)
        except ValueError:
            return not messagebox.showwarning('Erro', f'Digite coordenadas válidas para o ponto.', parent=win)

        if self.check_conflict(x, y, old_name):
            messagebox.showwarning('Erro', f'O ponto ({x}, {y}) já existe no plano.', parent=win)
        elif (-self.w > x) or (x > self.w) or (-self.h > y) or (y > self.h):
            messagebox.showwarning('Erro', f'As coordenadas ({x}, {y}) estão fora do limite do plano.', parent=win)
        elif (name in self.points.keys()) and (name!=old_name):
            messagebox.showwarning('Erro', f'Já existe um ponto com o nome "{name}".', parent=win)
        elif not name:
            messagebox.showwarning('Erro', f'Digite um nome válido para o ponto.', parent=win)
        else:
            return True


    # Conserta a posição do nome no canvas
    def name_fix(self, x, y):
        name_pos = [0, -10, 0] # Valores padrão: [x, y, angle]

        # Se estiver nas bordas horizontais (vira o nome)
        if x > 2*self.w-10:  name_pos[:] = [-10, 0, 90]
        if x < 10:           name_pos[:] = [+10, 0, -90]
        # Se estiver na borda superior (projeta o nome em baixo)
        if y < 13:           name_pos[1] = +10

        return name_pos


    # Detecta se há algum ponto onde o usuário clicou
    def click(self, event):
        if not event: return

        x, y = (event.x-self.w), (self.h-event.y)
        for point in self.points.items():
            if (x-5 <= point[1][0] <= x+5) and (y-5 <= point[1][1] <= y+5):
                return point[0]


    # Thread de execução do algoritmo
    def start(self):
        self.closest[:] = [float('inf'), {(None, None)}]
        self.screen[2].config(text=f'Menor Distância:  {self.closest[0]:.4f}\nPontos: {str(self.closest[1])[1:-1]}')
        temp_ids = {"points": [], "lines": [], "closest": []}

        closest_pair = ClosestPair(points=self.points,
                                   closest=self.closest,
                                   canvas=self.canvas,
                                   w=self.w, h=self.h,
                                   screen=self.screen, ids=temp_ids,
                                   response=[self.pause_event, self.stop_flag, self.speed])
        
        try: closest_pair.start()
        except Exception: messagebox.showerror('Erro', f'Ocorreu um erro.')
        self.stop(temp_ids)


    # Encerra e execução do algoritmo, resetando os elementos gráficos
    def stop(self, temp_ids):
        self.screen[3].config(text=f'Algoritmo finalizado! Menor Distância: {self.closest[0]:.2f}\n' \
                                    'Pressione "Finalizar" para encerrar a execução.')
        self.buttons[5][2].config(state="disabled")
        self.buttons[5][3].config(text="Finalizar")
        self.stop_flag.wait()

        for key in temp_ids.keys():
            for id in temp_ids[key]:
                self.canvas.delete(id)

        for element in self.buttons[5]:
            element.destroy()

        self.screen[3].config(text='Clique em "Iniciar Algoritmo" para executar o algoritmo.')
        self.buttons[5] = tk.Button(self.frame, text="Iniciar Algoritmo", width=31, command=self.on_start)
        self.buttons[5].grid(row=4, column=2, pady=5, sticky='e')

        self.canvas.bind("<Button-1>", self.on_add)
        self.canvas.bind("<Button-2>", self.on_edit)
        self.canvas.bind("<Button-3>", self.on_rem)

        for button in self.buttons:
            button.config(state="normal")
