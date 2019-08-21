import re


class SaasSpecific(object):
    def __init__(self, latex_str):
        self.str = latex_str

        self._saas_icons_re = re.compile(r"""\\(dry|reuse|codegen|concise|coc|legacy|beauty|tool|
                                         learnbydoing|automation|curric|idio|lookout)(\s+)?(\[.*?\])?({.*\})?""",
                                         flags=re.DOTALL + re.VERBOSE)

    def _saas_icons_block(self, matchobj):
        return ""

    def convert(self):
        output = self.str
        output = re.sub(r"\\protect", "", output)
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
        output = re.sub(r"\\{", r"{", output)
        output = re.sub(r"\\}", r"}", output)
        output = re.sub(r"\\#", "#", output)
        output = re.sub(r"\\_", "_", output)
        output = re.sub(r"\\-", "-", output)
        output = self._saas_icons_re.sub(self._saas_icons_block, output)
        return output
