def validate_email_47(email):
    return '@' in email and '.' in email.split('@')[-1]
