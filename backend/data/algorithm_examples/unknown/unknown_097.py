def validate_email_97(email):
    return '@' in email and '.' in email.split('@')[-1]
