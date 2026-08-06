password = input("Enter your password: ")

upper = False
lower = False
digit = False
special = False
repeated = False

special_char = "!@#$%^&*()-_=+[]{}|\\/:;'<>,.?"

for i in range(len(password)):
    ch = password[i]

    if ch.isupper():
        upper = True
    elif ch.islower():
        lower = True
    elif ch.isdigit():
        digit = True
    elif ch in special_char:
        special = True

    # Check repeated consecutive characters
    if i > 0 and password[i] == password[i - 1]:
        repeated = True

print("\nPassword Analysis")
print("Uppercase letter :", upper)
print("Lowercase letter :", lower)
print("Digit            :", digit)
print("Special character:", special)
print("Repeated consecutive character :", repeated)

print("\nFailed Rules:")

failed = False

if not upper:
    print("- Missing Uppercase Letter")
    failed = True

if not lower:
    print("- Missing Lowercase Letter")
    failed = True

if not digit:
    print("- Missing Digit")
    failed = True

if not special:
    print("- Missing Special Character")
    failed = True

if repeated:
    print("- Contains Repeated Consecutive Character")
    failed = True

if not failed:
    print("None")
    print("Password is Strong")
else:
    print("Password is Weak")