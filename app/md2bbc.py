import mistune
from fastapi import APIRouter, Form
from starlette.responses import HTMLResponse, PlainTextResponse


class Render(mistune.Renderer):
    @staticmethod
    def not_support(func):
        return f'[s] unsupported {func} [/s]'

    def newline(self):
        return '\n'

    def table(self, header, body):
        return self.not_support('table')

    def linebreak(self):
        return '\n'

    def list_item(self, text):
        return self.not_support('list item')

    def list(self, body, ordered=True):
        return self.not_support('list')

    def inline_html(self, html):
        return self.not_support('inline html')

    def header(self, text, level, raw=None):
        return (
            self.linebreak() + f'[size={26 - level * 2}]{text}[/size]' +
            self.linebreak()
        )

    def block_code(self, code, lang=None):
        return self.linebreak() + f'[code]{code}[/code]' + self.linebreak()

    def link(self, link, title, text):
        return f'[url={link}]{text or link}[/url]'

    def image(self, src, title, text):
        return f'[img]{src}[/img]'

    def codespan(self, text):
        return f'[b]{text}[/b]'

    def hrule(self):
        return self.not_support('hrule')

    def double_emphasis(self, text):
        """Rendering **strong** text.

        :param text: text content for emphasis.
        """
        return f'[b]{text}[/b]'

    def emphasis(self, text):
        """Rendering *emphasis* text.

        :param text: text content for emphasis.
        """
        return f'[i]{text}[/i]'

    def paragraph(self, text):
        return text + self.linebreak()

    def block_html(self, html):
        return self.not_support('block html')

    def block_quote(self, text):
        return self.linebreak() + f'[quote]{text}[/quote]' + self.linebreak()

    def footnotes(self, text):
        """Wrapper for all footnotes.

        :param text: contents of all footnotes.
        """
        return ''


markdown2bbcode = mistune.Markdown(renderer=Render(escape=True, hard_wrap=True))
router = APIRouter()


@router.get('/md2bbc', response_class=HTMLResponse)
def md2bbc():
    return """<!doctype html><html lang="zh"><head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>convert Markdown to BBcode</title></head>
    <body><form action="/md2bbc" method="post"><h1>paste your markdown here</h1>
    <textarea name="markdown" style='width: 100%' rows="10"></textarea>
    <input type="submit"></form></body></html>"""


@router.post('/md2bbc', response_class=PlainTextResponse, tags=[])
def render_md2bbc(markdown: str = Form('')):
    return markdown2bbcode(markdown)
