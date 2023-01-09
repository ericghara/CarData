

def priceStrToInt(price: int | str) -> int:
    if type(price) is int:
        return price
    price = price.replace("$", "").replace(",", "")
    return int(price)

