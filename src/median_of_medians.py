import math # Cálculo do teto para índices de listas com tamanho ímpar

# Retorna a mediana com base no algorito de Mediana das Medianas (MoM)
def median_of_medians(values):
    k = math.ceil(len(values)/2) # K inicial: metade para mediana

    # Algoritmo do K'ésimo menor número
    while(k):
        # Encontrar MoM
        medians = values[:]
        while(len(medians) > 1):
            groups = [sorted(medians[i:i + 5]) for i in range(0, len(medians), 5)]
            medians = [group[math.ceil(len(group)/2)-1] for group in groups]
        
        # Partição em torno da MoM
        m = medians[0]
        l = [v for v in values if v < m]
        r = [v for v in values if v > m]

        # Condição para dividir
        if(len(l) > k-1):
            values = l
        elif(len(l) < k-1):
            values = r
            k -= (len(l) + 1)
        else:
            return m
