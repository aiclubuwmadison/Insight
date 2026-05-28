def normalize_rows_24(rows):
    output = []
    for row in rows:
        output.append({str(k).lower(): v for k, v in row.items()})
    return output
