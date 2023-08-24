import uuid

def is_valid_uuid(s):
    try:
        uuid_obj = uuid.UUID(s)
        return str(uuid_obj) == s  # This ensures that the input string is in a valid UUID format
    except ValueError:
        return False