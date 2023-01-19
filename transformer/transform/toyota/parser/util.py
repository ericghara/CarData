import re
from typing import Optional


def priceStrToInt(price: int | str | float) -> int:
    if type(price) is int:
        return price
    if type(price) is float:
        return int(round(price,0) )
    price = price.replace("$", "").replace(",", "")
    whole, *dec = price.split(".")
    price = int(whole)
    if len(dec) > 1:
        raise ValueError(f"Invalid input: {price}")
    if dec and float('.' + dec[0]) >= 0.5:
        price += 1
    return int(price)

def digitsToInt(input: str | int | float) -> Optional[int]:
    if type(input) is int:
        return input
    if type(input) is float:
        return int(round(input, 0))
    # creates an int from first group of consecutive digits in text
    if not (matchObj := re.search(r"\d+", input) ):
        return None
    return int(matchObj.group())



def removeBracketed(text: str) -> str:
    return re.sub(r'\[[^]]*]', '', text).strip()
