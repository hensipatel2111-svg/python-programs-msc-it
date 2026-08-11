p = input("Enter paragraph: ")

words = p.split()

print("Total words:", len(words))

unique = []

for w in words:
    if w not in unique:
        unique.append(w)

print("Unique words:", len(unique))

longest = max(words, key=len)
shortest = min(words, key=len)

print("Longest word:", longest)
print("Shortest word:", shortest)

print("Words appearing more than once:")

for w in unique:
    if words.count(w) > 1:
        print(w)
