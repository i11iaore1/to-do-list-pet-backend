def generate_nickname_from_email(email: str) -> str:
    """
    Takes an email string
    Generates a nickname by splitting the email by @ separator
    Return a generated nickname
    """

    return email.split("@")[0]