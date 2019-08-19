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
        output = self._saas_icons_re.sub(self._saas_icons_block, output)
        return output
