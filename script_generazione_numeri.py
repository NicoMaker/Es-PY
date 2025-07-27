import random
import json

# Numero massimo casuale tra 1 e 1000
max_number = random.randint(1, 1000)

# Lista dei numeri da 1 a max_number
numbers_list = list(range(1, max_number + 1))

# Scegli un valore di "limits" a caso tra i numeri estratti
limits = random.choice(numbers_list)

# Costruisci il dizionario finale
data = {
    "numbers": numbers_list,
    "limits": limits
}

# Stampa preview con limite visibile
print(f"Numeri da 1 a {max_number}, limits: {limits}")

# Scrivi su file come JSON formattato
with open("lista.json", "w") as file:
    json.dump(data, file, indent=2)
