import os

folder_path = "../JSON"
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../JSON/numbers.json")

def somma_numeri_inferiori(lista, number):
    somma = 0
    s = [x for x in lista if x < number]
    return sum(s)

with open(file_path, "r") as file:
    import json
    data = json.load(file)
    lista = data["numbers"]
    limits = data["limits"]
    print(somma_numeri_inferiori(lista, limits))