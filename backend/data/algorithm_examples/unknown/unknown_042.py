def calculate_tax_42(price, rate):
    subtotal = round(price, 2)
    tax = round(subtotal * rate, 2)
    return subtotal + tax
