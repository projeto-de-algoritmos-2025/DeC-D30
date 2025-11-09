try: from median_of_medians import median_of_medians
except ModuleNotFoundError: from src.median_of_medians import median_of_medians
import math # Cálculo de distância euclidiana
import time


class ClosestPair():
    def __init__(self, points, closest=[float('inf'), {(None, None)}], canvas=None, w=None, h=None, ids=None, response=None):
        self.points = points
        self.closest = closest
        self.canvas = canvas
        self.w, self.h = w, h
        self.ids = ids
        self.response = response


    # Retorna o nome da mediana
    def median(self, names):
        points = [tuple(self.points[point]) for point in names] # Obtém os pontos
        median = median_of_medians(points) # Obtém o ponto cuja abscissa é mediana

        median_name = [point for point in names if self.points[point] == list(median)] # Separa nomes de pontos "mediana"
        return median_name[0] # Retorna o nome do primeiro ponto "mediana" (para o caso de pontos coincidentes)


    # Divide um conjunto de pontos com base na mediana (l <= m < r)
    def divide(self, points, m):
        left = [point for point in points if self.points[point] <= self.points[m]]
        right = [point for point in points if self.points[point] > self.points[m]]
        
        return left, right


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

            self.ids['points'].append(self.canvas.create_oval(self.w+self.points[full[-1]][0]-5, self.h-self.points[full[-1]][1]-5,
                                                              self.w+self.points[full[-1]][0]+5, self.h-self.points[full[-1]][1]+5, fill="orange"))

            if self.checkpoint(3/self.response[2].get()): return

            self.canvas.delete(self.ids['points'].pop(-1))

        for point in left[i:] + right[j:]:
            full.append(point)

            self.ids['points'].append(self.canvas.create_oval(self.w+self.points[point][0]-5, self.h-self.points[point][1]-5,
                                                              self.w+self.points[point][0]+5, self.h-self.points[point][1]+5, fill="orange"))

            if self.checkpoint(3/self.response[2].get()): return

            self.canvas.delete(self.ids['points'].pop(-1))

        return full


    # Separa os pontos próximos (abscissa <= d) da divisa
    def border(self, points, m):
        l, r = self.points[m][0] - self.closest[0], self.points[m][0] + self.closest[0]
        
        border_points = [point for point in points if (l <= self.points[point][0] <= r)]

        return border_points


    # Calcula a distância de um ponto com os 6 próximos, seguindo a ordenação de y
    def distances(self, points):
        for i in range(len(points)):
            for j in range(i+1, i + 7):
                try: points[j]
                except IndexError: break
                d = math.sqrt((self.points[points[i]][0] - self.points[points[j]][0])**2 + \
                              (self.points[points[i]][1] - self.points[points[j]][1])**2) # Distância euclidiana

                self.ids['lines'].append(self.canvas.create_line(self.w+self.points[points[i]][0], self.h-self.points[points[i]][1],
                                                                 self.w+self.points[points[j]][0], self.h-self.points[points[j]][1],
                                                                 width=3, fill="yellow"))
                
                if self.checkpoint(5/self.response[2].get()): return

                if(d < self.closest[0]):
                    self.closest[:] = [d, {(points[i], points[j])}]

                    for line in self.ids['closest']: self.canvas.delete(line)
                    self.canvas.itemconfig(self.ids['lines'][-1], fill="green")
                    self.ids['closest'].append(self.ids['lines'].pop(-1))
                elif(d == self.closest[0]):
                    self.closest[1].add((points[i], points[j]))

                    self.canvas.itemconfig(self.ids['lines'][-1], fill="green")
                    self.ids['closest'].append(self.ids['lines'].pop(-1))
                else:
                    self.canvas.delete(self.ids['lines'].pop(-1))


    # Sequência de passos do algoritmo recursivo
    def execution(self, points):

        if self.checkpoint(5/self.response[2].get()): return

        # Condição de parada do algoritmo: left/right com tamanho nulo ou unitário
        if(len(points)==0 or len(points)==1): return points
        
        # Encontrar a mediana
        median = self.median(points)
        self.ids['points'].append(self.canvas.create_oval(self.w+self.points[median][0]-5, self.h-self.points[median][1]-5,
                                                          self.w+self.points[median][0]+5, self.h-self.points[median][1]+5, fill="red"))

        if self.checkpoint(5/self.response[2].get()): return

        # Dividir os pontos em torno da mediana
        self.canvas.delete(self.ids['points'].pop(-1))
        left, right = self.divide(points, median)
        self.ids['lines'].append(self.canvas.create_line(self.w+self.points[median][0], 0,
                                                         self.w+self.points[median][0], 2*self.h,
                                                         width=2, fill="red"))

        # Recursão para a esquerda e direita (encontra a menor distância)
        left = self.execution(left)
        right = self.execution(right)

        if self.checkpoint(5/self.response[2].get()): return

        # Faz o merge dos conjuntos
        points = self.merge(left, right)

        if self.checkpoint(5/self.response[2].get()): return

        # Separa os pontos próximos à borda
        border_points = self.border(points, median)
        self.ids['lines'].append(self.canvas.create_line(self.w+(self.points[median][0]-self.closest[0]), 0,
                                                         self.w+(self.points[median][0]-self.closest[0]), 2*self.h, fill="orange"))
        self.ids['lines'].append(self.canvas.create_line(self.w+(self.points[median][0]+self.closest[0]), 0,
                                                         self.w+(self.points[median][0]+self.closest[0]), 2*self.h, fill="orange"))
        for point in points:
            self.ids['points'].append(self.canvas.create_oval(self.w+self.points[point][0]-5, self.h-self.points[point][1]-5,
                                                              self.w+self.points[point][0]+5, self.h-self.points[point][1]+5, fill="orange"))


        if self.checkpoint(5/self.response[2].get()): return

        # Procura possíveis menores distâncias na borda, e retorna os pontos ordenados por y
        self.distances(border_points)

        for i in range(3):
            self.canvas.delete(self.ids['lines'].pop(-1))
        for i in range(len(self.ids['points'])):
            self.canvas.delete(self.ids['points'].pop(-1))

        return points
    

    def checkpoint(self, sleep):
        time.sleep(sleep)
        self.response[0].wait()
        if self.response[1].is_set(): return True


    # Inicia o algoritmo
    def start(self):
        self.execution(self.points.keys())


# Teste rápido do algoritmo
'''
import json

with open('./db/database.json', 'r') as file:
    points = json.load(file)

closest_pair = ClosestPair(points)
closest_pair.start()

print(closest_pair.closest)
'''