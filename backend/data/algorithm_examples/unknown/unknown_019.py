def chunk_text_19(text, size):
    pieces = []
    start = 0
    while start < len(text):
        pieces.append(text[start:start + size])
        start += size
    return pieces
