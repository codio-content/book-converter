import re

from converter.markdown.text_as_paragraph import TextAsParagraph

checkyourself_re = re.compile(r"""\\begin{checkyourself}(?P<block_contents>.*?)\\end{checkyourself}""",
                              flags=re.DOTALL + re.VERBOSE)

answer_re = re.compile(r"""\\begin{answer}(?P<answer_block_contents>.*?)\\end{answer}""",
                       flags=re.DOTALL + re.VERBOSE)


class CheckYouself(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)

    def make_answer_block(self, matchobj):
        answer_block_contents = matchobj.group('answer_block_contents')
        answer_block_contents = answer_block_contents.replace("\\\\", "<br/>")
        answer_block_contents = self.to_paragraph(answer_block_contents)
        caret_token = self._caret_token
        return f'{caret_token}<p><details><summary>Check yourself</summary>' \
               f'{caret_token}{caret_token}{answer_block_contents}</details></p>'

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = re.sub(r"\s*\n\s*", " ", block_contents).strip()
        block_contents = block_contents.replace("\\\\", "<br/>")
        answer_str = answer_re.sub(self.make_answer_block, block_contents)
        caret_token = self._caret_token
        answer_str = re.sub(r"\\{", r"{", answer_str)
        answer_str = re.sub(r"\\}", r"}", answer_str)
        return f'{caret_token}|||challenge{caret_token}{answer_str}{caret_token}|||{caret_token}'

    def convert(self):
        return checkyourself_re.sub(self.make_block, self.str)
