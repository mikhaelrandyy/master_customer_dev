import random

# async def generate_number(size: int):

#     min_value = 10**(size - 1)  
#     max_value = 10**size - 1    

#     return random.randint(min_value, max_value)

async def generate_number(size: int) -> str:

    return ''.join(random.choices('0123456789', k=size))




    



