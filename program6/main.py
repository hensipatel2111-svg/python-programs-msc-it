from student import get_student
from ranking import rank_students
from  report import display

n = int(input("Enter number of students:"))
students = []

for i in range(n):
    print("\n student", i+1)
    students.append(get_student())
students = rank_students(students)
display(students)