import os
import random
import json

# Percorso cartella e file
folder_path = "../JSON"
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../JSON/numbers.json")

# Crea la cartella se non esiste
os.makedirs(folder_path, exist_ok=True)

# Numero massimo casuale tra 1 e 1000
max_number = random.randint(1, 1000)
numbers_list = list(range(1, max_number + 1))
limits = random.choice(numbers_list)

data = {
    "numbers": numbers_list,
    "limits": limits
}

print(f"Numeri da 1 a {max_number}, limits: {limits}")

with open(file_path, "w") as file:
    json.dump(data, file, indent=2)
