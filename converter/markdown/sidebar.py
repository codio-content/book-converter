import re

from converter.guides.tools import get_text_in_brackets
from converter.markdown.text_as_paragraph import TextAsParagraph


class Sidebar(TextAsParagraph):
    def __init__(self, latex_str, detect_asset_ext, caret_token):
        super().__init__(latex_str, caret_token)
        self._detect_asset_ext = detect_asset_ext

        self._pdfs = []

        self._sidebargraphic_re = re.compile(r"""\\begin{sidebargraphic}(\[(?P<props>.*?)])?
                                    {(?P<block_graphics>.*?)}(.*?)
                                    {(?P<block_name>.*?)}
                                    (?P<block_contents>.*?)
                                    \\end{sidebargraphic}""", flags=re.DOTALL + re.VERBOSE)

        self._sidebar_re = re.compile(r"""\\begin{sidebar}
                                    (?P<block_contents>.*?)
                                    \\end{sidebar}""", flags=re.DOTALL + re.VERBOSE)

    def _sidebar_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        lines = block_contents.split('\n')
        head = lines[0]
        title = ''
        additional = ''

        lines = lines[1:]

        matches = re.match(r"(\[.*\])?({.*?\})(.*)?", head)
        if matches:
            title = matches.group(2).strip()
            title = get_text_in_brackets(title)
            additional = matches.group(3).strip()

        if additional:
            lines.insert(0, additional)

        lines = map(lambda line: line.strip(), lines)
        block_contents = '\n'.join(lines)
        block_contents = self.to_paragraph(block_contents)

        caret_token = self._caret_token
        if title:
            return f'{caret_token}{caret_token}|||info{caret_token}**{title}** ' \
                f'{block_contents}{caret_token}|||{caret_token}{caret_token}'

        return f'{caret_token}{caret_token}|||info{caret_token}{block_contents}' \
            f'{caret_token}{caret_token}|||{caret_token}{caret_token}'

    def _sidebargraphic_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        image = matchobj.group('block_graphics')
        block_name = matchobj.group('block_name')

        if '.' not in image:
            ext = self._detect_asset_ext(image)
            if ext:
                image = '{}.{}'.format(image, ext)

        if image.lower().endswith('.pdf'):
            self._pdfs.append(image)
            image = image.replace('.pdf', '.jpg')

        image_src = "<img alt='{}' src='{}' style='width:200px' />".format(block_name, image)

        block_contents = self.to_paragraph(block_contents)
        caret_token = self._caret_token

        if block_name:
            block_name = block_name.strip()
            return f'{caret_token}{caret_token}|||xdiscipline{caret_token}**{block_name}** ' \
                f'{block_contents}{caret_token}{image_src}{caret_token}|||{caret_token}{caret_token}'

        if not block_contents:
            return f'{caret_token}{image_src}{caret_token}'

        return f'{caret_token}{caret_token}|||xdiscipline{caret_token}{block_contents}' \
            f'{caret_token}{image_src}{caret_token}|||{caret_token}{caret_token}'

    def convert(self):
        output = self.str

        output = self._sidebargraphic_re.sub(self._sidebargraphic_block, output)
        output = self._sidebar_re.sub(self._sidebar_block, output)

        return output, self._pdfs
