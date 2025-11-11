try: from median_of_medians import median_of_medians
except ModuleNotFoundError: from src.median_of_medians import median_of_medians
import math # Cálculo de distância euclidiana
import time


class ClosestPair():
    # Método de inicialização do algoritmo
    def __init__(self, points, closest=[float('inf'), {(None, None)}],
                 canvas=None, w=None, h=None, screen=None, ids=None, response=None):
        
        self.points, self.closest = points, closest
        self.canvas, self.w, self.h = canvas, w, h
        self.screen, self.ids, self.response, self.progress = screen, ids, response, 1



    # Retorna o nome da mediana
    def median(self, names):
        points = [tuple(self.points[point]) for point in names] # Obtém os pontos
        median = median_of_medians(points) # Obtém o ponto cuja abscissa é mediana

        median_name = [point for point in names if self.points[point] == list(median)] # Separa pontos "mediana"
        return median_name[0] # Retorna o nome do primeiro ponto "mediana" (para o caso de pontos coincidentes)



    # Divide um conjunto de pontos com base na mediana (l <= m < r)
    def divide(self, points, m):
        left = [point for point in points if self.points[point] <= self.points[m]]
        right = [point for point in points if self.points[point] > self.points[m]]
        
        return left, right



    # Separa os pontos próximos (abscissa <= d) da divisa
    def border(self, points, m):
        l, r = self.points[m][0] - self.closest[0], self.points[m][0] + self.closest[0]
        
        border_points = [point for point in points if (l <= self.points[point][0] <= r)]

        return border_points



    # Une dois conjuntos ordenados (merge)
    def merge(self, left, right):
        full, i, j = [], 0, 0
        

        while i < len(left) and j < len(right):
            if self.points[left[i]][1] < self.points[right[j]][1]:
                full.append(left[i])
                i += 1
            else:
                full.append(right[j])
                j += 1

            if self.canvas: # Se foi passado um canvas para acompanhamento visual
                self.plot((self.points[full[-1]][0], self.points[full[-1]][1]), color="orange")
                if self.checkpoint(7): return
                self.canvas.delete(self.ids['points'].pop(-1))


        for point in left[i:] + right[j:]:
            full.append(point)

            if self.canvas: # Se foi passado um canvas para acompanhamento visual
                self.plot((self.points[point][0], self.points[point][1]), color="orange")
                if self.checkpoint(7): return
                self.canvas.delete(self.ids['points'].pop(-1))


        return full



    # Calcula a distância de um ponto com os 6 próximos, seguindo a ordenação de y
    def distances(self, points):
        for i in range(len(points)): # Para cada ponto próximo à borda
            for j in range(i+1, i + 7): # Compara ele com os 6 próximos
                try: points[j]
                except IndexError: break

                d = math.sqrt((self.points[points[i]][0] - self.points[points[j]][0])**2 + \
                              (self.points[points[i]][1] - self.points[points[j]][1])**2) # Distância euclidiana

                if self.canvas: # Se foi passado um canvas para acompanhamento visual
                    self.plot((self.points[points[i]][0], self.points[points[i]][1]),
                              (self.points[points[j]][0], self.points[points[j]][1]),
                              width=3, color="yellow")
                    if self.checkpoint(13): return

                if(d < self.closest[0]): # Se foi encontrada uma distância menor
                    self.closest[:] = [d, {(points[i], points[j])}]

                    if self.canvas: # Se foi passado um canvas para acompanhamento visual
                        for line in self.ids['closest']: self.canvas.delete(line)
                        self.canvas.itemconfig(self.ids['lines'][-1], fill="green")
                        self.ids['closest'].append(self.ids['lines'].pop(-1))
                        self.screen[2].config(text=f'Menor Distância:  {self.closest[0]:.4f}' \
                                                   f'\nPontos: {str(self.closest[1])[1:-1]}') # Atualiza o texto

                elif(d == self.closest[0]): # Se foi encontrado um novo par de pontos com mesma menor distância
                    self.closest[1].add((points[i], points[j]))

                    if self.canvas: # Se foi passado um canvas para acompanhamento visual
                        self.canvas.itemconfig(self.ids['lines'][-1], fill="green")
                        self.ids['closest'].append(self.ids['lines'].pop(-1))
                        self.screen[2].config(text=f'Menor Distância:  {self.closest[0]:.4f}' \
                                                   f'\nPontos: {str(self.closest[1])[1:-1]}') # Atualiza o texto

                elif self.canvas: # Se foi passado um canvas para acompanhamento visual
                    self.canvas.delete(self.ids['lines'].pop(-1))



    # Sequência de passos do algoritmo recursivo
    def execution(self, points):
        # 1: Condição de parada do algoritmo: left/right com tamanho nulo ou unitário
        if(len(points)==0 or len(points)==1): return points


        # 2: Encontrar a mediana
        median = self.median(points)

        if self.canvas: # Se foi passado um canvas para acompanhamento visual
            self.screen[3].config(text=f'{self.step()}Encontrar a mediana de X')
            self.plot((self.points[median][0], self.points[median][1]), color="red")
            if self.checkpoint(13): return
            self.canvas.delete(self.ids['points'].pop(-1))


        # 3: Dividir os pontos em torno da mediana
        left, right = self.divide(points, median)

        if self.canvas: # Se foi passado um canvas para acompanhamento visual
            self.screen[3].config(text=f'{self.step()}Dividir os pontos na mediana')
            self.plot((self.points[median][0], -self.h), (self.points[median][0], +self.h), width=2, color="red")


        # 4: Recursão para a esquerda e direita (encontra a menor distância)
        if self.canvas:
            self.screen[3].config(text=f'{self.step()}Recursão (lado esquerdo)')
            if self.checkpoint(9): return
        left = self.execution(left)
        
        if self.canvas:
            self.screen[3].config(text=f'{self.step()}Recursão (lado direito)')
            if self.checkpoint(9): return
        right = self.execution(right)


        # 5: Faz o merge ordenado dos conjuntos
        if self.canvas:
            self.screen[3].config(text=f'{self.step()}Merge (ordenação) dos pontos')
            if self.checkpoint(13): return  # Se foi passado um canvas para acompanhamento visual
        points = self.merge(left, right)

        if self.canvas and self.checkpoint(13): return  # Se foi passado um canvas para acompanhamento visual


        # 6: Separa os pontos próximos à borda
        border_points = self.border(points, median)

        if self.canvas: # Se foi passado um canvas para acompanhamento visual
            self.plot((self.points[median][0]-self.closest[0], -self.h),
                      (self.points[median][0]-self.closest[0], +self.h), width=3, color="orange")
            self.plot((self.points[median][0]+self.closest[0], -self.h),
                      (self.points[median][0]+self.closest[0], +self.h), width=3, color="orange")

            for point in border_points:
                self.plot((self.points[point][0], self.points[point][1]), color="orange")

            self.screen[3].config(text=f'{self.step()}Análise dos pontos próximos a borda')
            if self.checkpoint(13): return


        # 7: Procura menores distâncias entre pontos próximos à borda
        self.distances(border_points)

        if self.canvas: # Se foi passado um canvas para acompanhamento visual
            for i in range(3):
                self.canvas.delete(self.ids['lines'].pop(-1))
            for i in range(len(self.ids['points'])):
                self.canvas.delete(self.ids['points'].pop(-1))


        # 8: Retorna os pontos left+right obtidos em (5)
        return points
    


    # Plota linhas ou pontos no canvas (se solicitado)
    def plot(self, p1, p2=None, width=1, color="blue"):
        if p2:
            line = self.canvas.create_line(self.w+p1[0], self.h-p1[1],
                                           self.w+p2[0], self.h-p2[1],
                                           width=width, fill=color)
            self.ids['lines'].append(line)

        else:
            point = self.canvas.create_oval(self.w+p1[0]-5, self.h-p1[1]-5,
                                            self.w+p1[0]+5, self.h-p1[1]+5,
                                            width=width, fill="red")
            self.ids['points'].append(point)



    # Checkpoint da thread: tempo de espera + se foi pausada ou encerrada
    def checkpoint(self, sleep):
        time.sleep(sleep/(self.response[2].get()**1.4)) # Tempo de espera (para acompanhamento visual)
        self.response[0].wait() # Pausa a thread quando a flag for ativa
        if self.response[1].is_set(): return True # Encerra a thread recursivamente


    # Acompanhamento do progresso do algoritmo
    def step(self):
        self.progress += 1
        return f'Etapa {self.progress}/{len(self.points)*6-5}: '


    # Inicia o algoritmo
    def start(self):
        self.execution(self.points.keys()) # Obs: o algoritmo trabalha recursivamente com os nomes dos pontos


# Teste do algoritmo
'''
import json

with open('./db/database.json', 'r') as file:
    points = json.load(file)

closest_pair = ClosestPair(points)
closest_pair.start()

print(closest_pair.closest)
'''