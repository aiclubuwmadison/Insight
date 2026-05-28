def validate_email_17(email):
    return '@' in email and '.' in email.split('@')[-1]
