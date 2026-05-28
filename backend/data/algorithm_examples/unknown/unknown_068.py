def summarize_grades_68(grades):
    if not grades:
        return {'average': 0, 'count': 0}
    return {'average': sum(grades) / len(grades), 'count': len(grades)}
