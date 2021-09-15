import re

from converter.markdown.text_as_paragraph import TextAsParagraph


class SaasSpecific(TextAsParagraph):
    def __init__(self, latex_str, caret_token):
        super().__init__(latex_str, caret_token)
        self.str = latex_str

        self._saas_icons_re = re.compile(r"""\\(dry|reuse|codegen|concise|coc|legacy|beauty|tool|
                                         learnbydoing|automation|curric|idio|lookout)(\s+)?(\[.*?\])?({.*\})?""",
                                         flags=re.DOTALL + re.VERBOSE)

        self._saas_2icons_re = re.compile(
            r"""\\twoicons(\[.*?\])?
            {(dry|reuse|codegen|concise|coc|legacy|beauty|tool|learnbydoing|automation|curric|idio|lookout)\}
            {(dry|reuse|codegen|concise|coc|legacy|beauty|tool|learnbydoing|automation|curric|idio|lookout)\}""",
            flags=re.DOTALL + re.VERBOSE
        )

        self._new_re = re.compile(r"""\\begin{NEW}(?P<block_contents>.*?)\\end{NEW}""",
                                  flags=re.DOTALL + re.VERBOSE)

    def _saas_icons_block(self, matchobj):
        return ""

    def make_block(self, matchobj):
        block_contents = matchobj.group('block_contents')
        block_contents = self.to_paragraph(block_contents)
        return f'{block_contents}'

    def convert(self):
        output = self.str
        output = re.sub(r"\\protect", "", output)
        output = re.sub(r"\\putbib", "", output)
        output = re.sub(r"\\ig({\})?", "Instructors' Manual", output)
        output = re.sub(r"\\js({\})?", "JavaScript", output)
        output = re.sub(r"\\slash({\})?", "/", output)
        output = re.sub(r"\\ldots({\})?", r"...", output)
        output = re.sub(r"\\LaTeX({\})?", r"LaTeX", output)
        output = re.sub(r"\\TeX({\})?", r"TeX", output)
        output = re.sub(r"\\\"{(.*?)\}", r"\1", output)
        output = re.sub(r"\\spaceship({\})?", r"<=>", output)
        output = re.sub(r"\\thinspace({\})?", r" ", output)
        output = re.sub(r"\\tl({\})?", r"<", output)
        output = re.sub(r"\\tg({\})?", r">", output)
        output = re.sub(r"\\ttil({\})?", r"~", output)
        output = re.sub(r"\\textbar({\})?", r"|", output)
        output = re.sub(r"\\hrule", "<hr>", output)
        output = re.sub(r"\\hspace", "", output)
        output = re.sub(r"\\small", "", output)
        output = self._saas_icons_re.sub(self._saas_icons_block, output)
        output = self._saas_2icons_re.sub(self._saas_icons_block, output)
        output = self._new_re.sub(self.make_block, output)
        return output
