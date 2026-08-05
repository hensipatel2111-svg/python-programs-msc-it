max_roll=int(input("Enter maximum rno:"))
rno=list(map(int,input("Enter roll numbers:").split()))

print("Missing Roll Numbers:")

for i in range(1,max_roll+1):
    if i not in rno:
        print(i)