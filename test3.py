import random

# Define some example functions
def function1():
    print("Function 1 executed")

def function2():
    print("Function 2 executed")

def function3():
    print("Function 3 executed")

# Create a list of the functions
functions = [function1, function2, function3]

# Select a random function and execute it
random_function = random.choice(functions)
random_function()
