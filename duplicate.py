n = [1, 2, 2, 3, 4, 4, 4, 5]
dup = []
for i in n:
 if n.count(i) > 1 and i not in dup:
     dup.append(i)
print(dup)