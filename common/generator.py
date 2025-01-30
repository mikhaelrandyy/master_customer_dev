import random

def generate_number(digit: int) -> int:
    start = 10**(digit - 1)
    end = (10**digit) - 1
    return random.randint(start, end)



    



