import re
from html import unescape
from html.parser import HTMLParser


class PlainTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data):
        if not self.skip_depth:
            self.parts.append(data)

    def text(self):
        return " ".join(self.parts)

def sanitize_text_input(text: str, max_length: int = 500) -> str:
    """Sanitiza entrada de usuario y conserva solo texto plano."""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    text = unescape(text[:max_length])

    parser = PlainTextExtractor()
    parser.feed(text)
    parser.close()

    clean_text = parser.text()
    clean_text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    return clean_text[:max_length]
