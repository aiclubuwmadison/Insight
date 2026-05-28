def validate_email_77(email):
    return '@' in email and '.' in email.split('@')[-1]
