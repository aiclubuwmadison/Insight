def normalize_rows_34(rows):
    output = []
    for row in rows:
        output.append({str(k).lower(): v for k, v in row.items()})
    return output
