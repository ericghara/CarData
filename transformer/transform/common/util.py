import re
from typing import Optional


def numStrToInt(numStr: str) -> int:
    numStr = numStr.strip().replace(",", "")
    if not re.fullmatch("-?\d*\.?\d*", numStr) or numStr in {'.', '-', '-.'}:
        # '.' falls through regex pattern
        # number at the end of a sentence accurately parsed, although a bit of an edge case
        raise ValueError(f"Invalid input: {numStr}")
    numFloat = float(numStr)
    return int(round(numFloat, 0))


def priceToInt(price: int | str | float) -> int:
    if type(price) is int:
        return price
    if type(price) is float:
        return int(round(price, 0))
    price = price.replace("$", "")
    return numStrToInt(price)


def digitsToInt(input: str | int | float) -> Optional[int]:
    if type(input) is int:
        return input
    if type(input) is float:
        return int(round(input, 0))
    # creates an int from first group of consecutive digits in text
    if not (matchObj := re.search(r"-?\d+", input)):
        return None
    return int(matchObj.group())


def removeBracketed(text: str) -> str:
    return re.sub(r'\[[^]]*]', '', text).strip()
