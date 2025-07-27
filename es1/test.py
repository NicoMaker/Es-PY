def somma_numeri_inferiori(lista, number):
    somma = 0
    s = [x for x in lista if x < number]
    return sum(s)

with open("lista.json", "r") as file:
    import json
    data = json.load(file)
    lista = data["numbers"]
    limits = data["limits"]
    print(somma_numeri_inferiori(lista, limits))