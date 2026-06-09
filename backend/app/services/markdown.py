import bleach
import markdown as md

ALLOWED_TAGS = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr", "a", "img",
    "ul", "ol", "li", "pre", "code",
    "blockquote", "table", "thead", "tbody", "tr", "th", "td",
    "strong", "em", "del", "ins", "sup", "sub",
    "div", "span", "dl", "dt", "dd", "abbr", "cite",
]

ALLOWED_ATTRS = {
    "a": ["href", "title", "rel"],
    "img": ["src", "alt", "title"],
    "code": ["class"],
    "pre": ["class"],
    "th": ["align"],
    "td": ["align"],
    "*": ["id"],
}

EXTENSIONS = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.codehilite",
    "markdown.extensions.tables",
    "markdown.extensions.toc",
    "markdown.extensions.nl2br",
]


def render_markdown(text: str) -> str:
    html = md.markdown(text, extensions=EXTENSIONS)
    cleaned = bleach.clean(html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=True)
    return cleaned
