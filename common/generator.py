import ulid

async def generate_number_16_digit():
    ulid_str = str(ulid.new())[:16]  
    return int(ulid_str)  

async def generate_number_22_digit():
    ulid_str = str(ulid.new())[:22]  
    return int(ulid_str)  



    



