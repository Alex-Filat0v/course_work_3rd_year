import random


history = {}
for i in range(10):
    symbol = random.randint(1, 1000)
    history[f"{i}"] = symbol
print(history)

for items in history:
    print(history.get(items))