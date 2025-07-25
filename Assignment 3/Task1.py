# the factorial using the recursion
def factorial(n):
    if (n<2):
        return 1
    else:
        return factorial(n-1) *n
n = int(input("Enter the number: "))
a = factorial(n)
print(f"The factorial of {n} is {a}")