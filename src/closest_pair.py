from median_of_medians import median_of_medians
import math # Cálculo de distância euclidiana


# Retorna o nome da mediana em um dicionário {nome: coordenada}
def median(points):
    x_values = [point[0] for point in points.values()] # Obtém as abscissas do plano
    x_median = median_of_medians(x_values) # Obtém a mediana das abscissas

    median_name = [name for name in points.keys() if points[name][0] == x_median] # Separa nomes de pontos com x = mediana
    return median_name[0], x_median # Retorna o nome do primeiro elemento com x = mediana


# Divide um conjunto de pontos com base na mediana (l <= m < r)
def divide(points, m):
    left = dict([pair for pair in points.items() if pair[1][0] <= m])
    right = dict([pair for pair in points.items() if pair[1][0] > m])
    
    return left, right


# Une dois conjuntos ordenados (merge)
def merge(left, right):
    full, i, j = [], 0, 0
    
    while i < len(left) and j < len(right):
        if left[i][1][1] < right[j][1][1]:
            full.append(left[i])
            i += 1
        else:
            full.append(right[j])
            j += 1

    full.extend(left[i:])
    full.extend(right[j:])
    return full


# Separa os pontos próximos (abscissa <= d) da divisa
def border(points, m, d):
    l, r = m-d, m+d
    
    border_points = [point for point in points if (l<=point[1][0] and point[1][0]<=r)]

    return border_points


# Calcula a distância de um ponto com os 6 próximos, seguindo a ordenação de y
def distances(points, closest):
    for i in range(len(points)):
        for j in range(i+1, i + 7):
            try: points[j]
            except IndexError: break
            d = math.sqrt((points[i][1][0] - points[j][1][0])**2 + (points[i][1][1] - points[j][1][1])**2)

            if(d < closest[0]): closest[:] = [d, {(points[i][0], points[j][0])}]
            elif(d == closest[0]): closest[1].add((points[i][0], points[j][0]))


# Sequência de passos do algoritmo recursivo
def execution(points, closest=[float('inf'), (None, None)]):
    # Condição de parada do algoritmo: left/right com tamanho nulo ou unitário
    if(len(points)==0 or len(points)==1): return list(points.items())
    
    # Encontrar a mediana e dividir
    m, m_value = median(points)
    left, right = divide(points, m_value)

    # Recursão para a esquerda e direita (encontra a menor distância)
    left = execution(left, closest)
    right = execution(right, closest)

    # Faz o merge dos conjuntos e separa os pontos próximos da borda
    points = merge(left, right)
    points = border(points, m_value, closest[0])

    # Procura possíveis menores distâncias na borda, e retorna os pontos ordenados por y
    distances(points, closest)
    return points


# Teste rápido do algoritmo
'''
import json

with open('./db/database.json', 'r') as file:
    points = json.load(file)

closest = [float('inf'), {(None, None)}]

execution(points, closest)

print(closest)
'''