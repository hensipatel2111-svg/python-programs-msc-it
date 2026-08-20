def rank_students(students):

    students.sort(key=lambda x: x[2],reverse=True)
    rank = 1
    for i in range(len(students)):
        if i > 0 and students[i][2] !=students[i - 1][2]:
            rank=i+1
        students[i].append(rank)
    return students