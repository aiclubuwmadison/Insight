def validate_email_67(email):
    return '@' in email and '.' in email.split('@')[-1]
