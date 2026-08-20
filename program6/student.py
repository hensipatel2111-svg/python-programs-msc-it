def get_student():
    
    rollno=int(input("Enter your roll No. : "))
    name=input("Enter Your Name: ")
    m1=int(input("Enter Your DS Marks: "))
    m2=int(input("Enter Your CN Marks: "))
    m3=int(input("Enter Your Linux Marks: "))
    m4=int(input("Enter Your Python Marks: "))
    m5=int(input("Enter Your Digital Grafics: "))    
    
    total=m1+m2+m3+m4+m5
    percentage=total/5
    
    if percentage>=90:
        grade="A"
    elif percentage>=80:
        grade="B"
    elif percentage>=70:
        grade="C"
    elif percentage>=60:
        grade="D"
    elif percentage>=50:
        grade="E"
    else:
        grade="F"
    return [rollno, name, total, percentage, grade]