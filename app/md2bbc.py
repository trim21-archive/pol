import mistune
from flask import Flask, request, Response
from app import app


@app.route('/md2bbc')
def md2bbc_index():
    return """<!doctype html>
<html lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport"
        content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
  <meta http-equiv="X-UA-Compatible" content="ie=edge">
  <title>Document</title>
</head>
<body>
<form action="/md2bbc" method="post">
  <h1>paste your markdown here</h1>
  <textarea name="markdown" id="" cols="30" rows="10" placeholder="paste your markdown here">

  </textarea>
  <input type="submit">
</form>

</body>
</html>"""


@app.route('/md2bbc', methods=['POST'])
def rmd2bbc_render():

    return Response(
        markdown(request.form.get('markdown', '')), mimetype='text/plain'
    )


class Render(mistune.Renderer):
    def not_support(self, func):
        return f"[s] unsupported {func} [/s]"

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
            self.linebreak() + f'[size={26-level*2}]{text}[/size]' +
            self.linebreak()
        )

    def block_code(self, code, lang=None):
        return self.linebreak() + f'[code]{code}[/code]' + self.linebreak()

    def link(self, link, title, text):
        return f'[url={link}]{title or link}[/url]'

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


markdown = mistune.Markdown(renderer=Render(escape=True, hard_wrap=True))
