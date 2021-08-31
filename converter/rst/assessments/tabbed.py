import re


class Tabbed(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._tabbed_re = re.compile(
            r"""^\.\.\s+tabbed.*?::\s+(?P<name>.*?)\n(?P<content>.*?)\n(?=\S|(?!^$)$)""",
            flags=re.MULTILINE + re.DOTALL)

    def _tabbed(self, matchobj):
        content = matchobj.group('content').rstrip()
        tab_question_match = re.search(r"""\.\.\s+tab::\s+(?P<type>.*?)\n(?P<ex_content>.*?)\n(?=\s*.. tab:: Answer)""",
                                       content, flags=re.MULTILINE + re.DOTALL)
        if tab_question_match:
            str_len = 0
            cut_content = []
            ex_content = tab_question_match.group('ex_content').rstrip()
            content_list = ex_content.split('\n')
            content_list = [item for item in content_list if item.strip() != '']
            for ind, item in enumerate(content_list):
                indent_match = re.search(r'^( *)\.\. ', item, flags=re.MULTILINE)
                if indent_match:
                    str_len = len(indent_match.group(1))
                cut_content.append(content_list[ind][str_len:])
            final_content = '\n'.join(cut_content)
            return f'{final_content}\n\n'

    def convert(self):
        output = self._tabbed_re.sub(self._tabbed, self.str)
        return output
