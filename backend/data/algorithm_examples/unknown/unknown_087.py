def validate_email_87(email):
    return '@' in email and '.' in email.split('@')[-1]
