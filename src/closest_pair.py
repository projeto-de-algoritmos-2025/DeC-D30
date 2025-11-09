try: from median_of_medians import median_of_medians
except ModuleNotFoundError: from src.median_of_medians import median_of_medians
import math # Cálculo de distância euclidiana
import time


class ClosestPair():
    def __init__(self, points, closest=[float('inf'), {(None, None)}], canvas=None, ids=None, response=None):
        self.points = points
        self.closest = closest
        self.canvas = canvas
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

        for point in left[i:]:
            full.append(point)
        for point in right[j:]:
            full.append(point)

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

                if(d < self.closest[0]): self.closest[:] = [d, {(points[i], points[j])}]
                elif(d == self.closest[0]): self.closest[1].add((points[i], points[j]))


    # Sequência de passos do algoritmo recursivo
    def execution(self, points):
        # Condição de parada do algoritmo: left/right com tamanho nulo ou unitário
        if(len(points)==0 or len(points)==1): return points
        
        # Encontrar a mediana e dividir
        median = self.median(points)
        left, right = self.divide(points, median)

        # Recursão para a esquerda e direita (encontra a menor distância)
        left = self.execution(left)
        right = self.execution(right)

        # Faz o merge dos conjuntos e separa os pontos próximos da borda
        points = self.merge(left, right)
        points = self.border(points, median)

        # Procura possíveis menores distâncias na borda, e retorna os pontos ordenados por y
        self.distances(points)
        return points
    

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