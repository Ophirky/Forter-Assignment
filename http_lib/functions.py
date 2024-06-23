"""
    AUTHOR: Ophir Nevo Michrowski
    DESCRIPTION: Useful functions on dictionaries
"""


def dict_to_bytes(dictionary: dict) -> dict[bytes]:
    """
    Takes a dictionary and casts all the elements within to bytes.
    EXAMPLE: {"name": "John", "age": 45} -> {b"name": b"John", b"age": b"45"}
    :param dictionary: the dict to convert
    :return dict[bytes]: the converted dictionary .
    """
    if dictionary:
        return {(key.encode('utf-8') if isinstance(key, str) else str(key).encode('utf-8')):
                    (value.encode('utf-8') if isinstance(value, str) else str(value).encode('utf-8'))
                for key, value in dictionary.items()}
    else:
        return dict()
