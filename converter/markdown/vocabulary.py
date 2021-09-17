import re

from converter.markdown.text_as_paragraph import TextAsParagraph

vocabulary_re = re.compile(r"""\\begin{description}(?P<block_content>.*?)\\end{description}""", flags=re.DOTALL)
term_re = re.compile(r"""\\term{(?P<term>.*?)}\n*(?P<content>.*?)\n(?=^$|(?!^$)$)""", flags=re.MULTILINE + re.DOTALL)
term_item_re = re.compile(r"""\\item\[(?P<term>.*?):]\n*(?P<content>.*?)\n(?=^$|(?!^$)$)""",
                          flags=re.MULTILINE + re.DOTALL)


class Vocabulary(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_block(self, matchobj):
        block_content = matchobj.group('block_content')
        block_content = self.to_paragraph(block_content) + '\n'
        block_content = term_re.sub(r'<b>\1:</b>\n\t\2\n', block_content)
        block_content = term_item_re.sub(r'<b>\1:</b>\n\t\2\n', block_content)
        return block_content

    def convert(self):
        return vocabulary_re.sub(self.make_block, self.str)
