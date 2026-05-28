def validate_email_7(email):
    return '@' in email and '.' in email.split('@')[-1]
