from converter.markdown.match_elements import match_elements
from converter.markdown.text_as_paragraph import TextAsParagraph


class TuringWinner(TextAsParagraph):
    def __init__(self, latex_str, caret_token, detect_asset_ext):
        super().__init__(latex_str, caret_token)
        self._pdfs = []
        self._detect_asset_ext = detect_asset_ext

    def make_content(self, image, block_name, block_contents, q_content, q_name):
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

        block_name = block_name.strip()
        sidebar = f'{caret_token}{caret_token}|||xdiscipline{caret_token}**{block_name}** ' \
                  f'{block_contents}{caret_token}{image_src}{caret_token}|||{caret_token}{caret_token}'

        quote = ''
        q_name = q_name.strip()
        if q_name and q_content:
            quote = f'{caret_token}> {q_content}{caret_token}>' \
                    f'{caret_token}> __{q_name}__{caret_token}{caret_token}'

        return sidebar + quote

    def convert(self):
        out = self.str
        search_str = "\\turingwinner"
        pos = out.find(search_str)
        while pos != -1:
            matches, index = match_elements(out[pos + len(search_str):], 5)
            start = out[0:pos]
            end_pos = pos + len(search_str) + 1 + index
            end = out[end_pos:]
            out = start + self.make_content(
                f'turing/figs/{matches[0]}', matches[1], matches[2], matches[3], matches[4]
            ) + end
            pos = out.find(search_str, end_pos + 1)
        return out, self._pdfs
