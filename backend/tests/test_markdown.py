from app.services.markdown import render_markdown


def test_basic_markdown():
    html = render_markdown("# Hello")
    assert "<h1>Hello</h1>" in html


def test_code_block():
    md_text = "```python\nprint('hi')\n```"
    html = render_markdown(md_text)
    assert "<code" in html or "<pre" in html


def test_xss_removed():
    malicious = '<script>alert("xss")</script>'
    html = render_markdown(malicious)
    assert "<script>" not in html


def test_allowed_tags_preserved():
    html = render_markdown("[link](http://example.com)")
    assert '<a href="http://example.com"' in html
