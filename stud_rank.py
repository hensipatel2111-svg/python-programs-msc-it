n = int(input("Enter number of students: "))

students = []

for i in range(n):
    roll = int(input("Enter Roll No: "))
    name = input("Enter Name: ")

    total = 0
    for j in range(5):
        marks = int(input("Enter marks: "))
        total = total + marks

    percentage = total / 5

    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    students.append([roll, name, total, percentage, grade])

# Sort by total marks
students.sort(key=lambda x: x[2], reverse=True)

# Display rank
rank = 1

for i in range(n):
    if i > 0 and students[i][2] != students[i-1][2]:
        rank = i + 1

    print(rank, students[i][0], students[i][1],
          students[i][2], students[i][3], students[i][4])