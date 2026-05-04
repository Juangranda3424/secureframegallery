from html import escape

def sanitize_text_input(text: str, max_length: int = 500) -> str:
    """Sanitiza entrada de usuario contra XSS"""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    text = text[:max_length]

    text = escape(text)

    return text