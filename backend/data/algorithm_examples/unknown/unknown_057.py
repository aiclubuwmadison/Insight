def validate_email_57(email):
    return '@' in email and '.' in email.split('@')[-1]
