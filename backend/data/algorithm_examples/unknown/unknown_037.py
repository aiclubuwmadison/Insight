def validate_email_37(email):
    return '@' in email and '.' in email.split('@')[-1]
