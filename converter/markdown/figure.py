import re

from converter.guides.tools import get_text_in_brackets
from converter.markdown.text_as_paragraph import TextAsParagraph


class Figure(TextAsParagraph):
    def __init__(self, latex_str, figure_num, chapter_num, detect_asset_ext, caret_token, refs):
        super().__init__(latex_str, caret_token)

        self._figure_counter = 0
        self._figure_counter_offset = figure_num
        self._chapter_num = chapter_num
        self._pdfs = []
        self._detect_asset_ext = detect_asset_ext
        self._refs = refs

        self._figure_re = re.compile(r"""\\begin{figure}(.*?)\n
                                    (?P<block_contents>.*?)
                                    \\end{figure}""", flags=re.DOTALL + re.VERBOSE)

    def _figure_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        match_label = re.search(r'\\label{(.*?)}', block_contents)
        if match_label:
            label = match_label.group(1)
            block_contents = re.sub(r'\\label{.*?}', '', block_contents)

        self._figure_counter += 1

        images = []
        caption = 'Figure {}.{} '.format(
            self._chapter_num, self._figure_counter + self._figure_counter_offset
        )

        if self._refs.get(label, {}):
            caption = '**<p style="font-size: 10px">Figure {}'.format(
                self._refs.get(label).get('ref')
            )

        caption_line = None

        for line in block_contents.strip().split("\n"):
            if "\\includegraphics" in line:
                if not line.startswith("\\includegraphics"):
                    line = get_text_in_brackets(line)
                images.append(get_text_in_brackets(line))
            elif "\\caption" in line:
                if '}' in line:
                    caption += get_text_in_brackets(line)
                else:
                    caption_line = line
            elif caption_line:
                if '}' in line:
                    caption += get_text_in_brackets(caption_line + ' ' + line)
                    caption_line = None
                else:
                    caption_line += ' ' + line

        markdown_images = []

        for image in images:
            if '.' not in image:
                ext = self._detect_asset_ext(image)
                if ext:
                    image = '{}.{}'.format(image, ext)
            if image.lower().endswith('.pdf'):
                self._pdfs.append(image)
                image = image.replace('.pdf', '.jpg')
            markdown_images.append(
                "![{}]({})".format(caption, image)
            )
        caret_token = self._caret_token
        caption = caption.replace("**", "").strip()

        if markdown_images:
            return f'{self._caret_token.join(markdown_images)}{caret_token}{caret_token}**{caption}**'

        block_contents = re.sub(r"\\caption{(.*?)}", r"", block_contents, flags=re.DOTALL + re.VERBOSE)

        return f'{block_contents}{caret_token}**<p style="font-size: 10px">{caption}</p>**{caret_token}'

    def convert(self):
        output = self.str

        output = self._figure_re.sub(self._figure_block, output)

        return output, self._pdfs, self._figure_counter
