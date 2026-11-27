
class Course:
    def __init__(self, code, day, start, end):
        self.code = code
        self.day = day
        self.start = start
        self.end = end

    def __str__(self):
        return self.code + " - " + self.day + " - " + str(self.start) + " to " + str(self.end)


class Student:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
        self.courses = []

    def __str__(self):
        return "Student ID: " + self.sid + "\nStudent Name: " + self.name


try:
    n = int(input("Enter number of students: "))

    if n <= 0:
        raise ValueError("Number of students must be positive")

    for i in range(n):
        print("\nEnter Student Details")

        sid = input("Enter Student ID: ")
        name = input("Enter Student Name: ")

        s = Student(sid, name)

        total = int(input("Enter number of courses: "))

        if total < 0:
            raise ValueError("Number of courses cannot be negative")

        for j in range(total):
            print("\nEnter Course Details")

            code = input("Enter Course Code: ")
            day = input("Enter Day: ").strip().title()

            if day not in ["Monday", "Tuesday", "Wednesday",
                           "Thursday", "Friday", "Saturday", "Sunday"]:
                raise ValueError("Invalid day")

            start = int(input("Enter Start Hour (0-23): "))
            end = int(input("Enter End Hour (0-23): "))

            if start < 0 or start > 23 or end < 0 or end > 23 or start >= end:
                raise ValueError("Invalid time")

            c = Course(code, day, start, end)
            s.courses.append(c)

        print("\nStudent Details")
        print(s)

        conflict = False

        for a in range(len(s.courses)):
            for b in range(a + 1, len(s.courses)):
                c1 = s.courses[a]
                c2 = s.courses[b]

                if c1.day == c2.day and c1.start < c2.end and c2.start < c1.end:
                    print("Conflict:", c1.code, "and", c2.code)
                    conflict = True

        if conflict == False:
            print("\nNo Conflict Found")
            print("Student Timetable:")

            for c in s.courses:
                print(c)

        print("Total Registered Courses:", len(s.courses))

except ValueError as e:
    print("Invalid Input:", e)