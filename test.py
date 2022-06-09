# string = '75 / 759 / 549'
# string = list(string.split(' / '))
# string = [int(i) for i in string]
# print(string)

data = [('UF1', 7277.0, '133 / 61 / 39', '51 / 11 / 39', '147 / 58 / 91', '0.82'), ('UF2', 8000.0, '146 / 67 / 42', '57 / 12 / 42', '162 / 63 / 100', '0.88'), ('UF3', 8497.0, '155 / 71 / 45', '60 / 13 / 45', '172 / 67 / 106', '0.03'), ('UF4', 7277.0, '133 / 61 / 39', '51 / 11 / 39', '147 / 43 / 91', '2.03'), ('UF5', 8000.0, '146 / 67 / 42', '57 / 12 / 42', '162 / 47 / 100', '2.39'), ('UF6', 8497.0, '155 / 71 / 45', '60 / 13 / 45', '172 / 50 / 106', '0.18'), ('UF7', 7277.0, '133 / 61 / 39', '51 / 11 / 39', '184 / 86 / 122', '2.18'), ('UF8', 8000.0, '146 / 67 / 42', '57 / 12 / 42', '203 / 95 / 133', '1.88'), ('UF9', 8497.0, '155 / 71 / 45', '60 / 13 / 45', '215 / 101 / 142', '0.63')]

ce = [int(e[1]) for e in data]
area = [float(e[5]) for e in data]
npk = [str(e[4]) for e in data]
lista = [e.split(' / ') for e in npk ]
n = [int(e[0]) for e in lista]
p = [int(e[1]) for e in lista]
k = [int(e[2]) for e in lista]
print(lista)
print(k)





def calculo(x,y):
    """
    x = Value y = Area

    """
    zipedd = zip(x, y)
    p1 = [x * y for (x, y) in zipedd]
    p2 = round(sum(p1)/sum(y))

    # print(p2)
    return p2

cosecha_ponderada = calculo(ce, area)
n_ponderado = calculo(n, area)
p_ponderado = calculo(p, area)
k_ponderado = calculo(k, area)
print(n_ponderado,p_ponderado,k_ponderado)




