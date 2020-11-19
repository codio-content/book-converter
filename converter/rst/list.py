import re


class List(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._list_re = re.compile(r"""^( *)(?P<type>[*+\-]|[0-9#]+[\.|)]) [^\n]*(?:\n(?!\1\2|\S)[^\n]*)*""",
                                   flags=re.MULTILINE)

    def _list(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group(0)
        content = content.strip()
        items = []
        match_all_items = list(re.finditer(r'^( *)([*+-]|[0-9#]+[.]) [\s\S]+?(?:\n{2,}(?! )(?!\1\2 |\S)\n*|\s*$)',
                                           content, flags=re.MULTILINE))
        if len(match_all_items) > 1:
            for item in match_all_items:
                item = f'{item.group(0)}{caret_token}'
                item = self._clearing_line_breaks(item)
                items.append(item)
            content = '\n'.join(items)
        else:
            content = self._clearing_text_spaces(content)
            content = self._clearing_line_breaks(content)
        return f'{content}\n'

    @staticmethod
    def _clearing_text_spaces(data):
        space = re.search('\n *', data)
        if space:
            space_count = len(space.group(0))
            space_regex = f"\n^ {{{space_count}}}"
            data = re.sub(space_regex, '', data, flags=re.MULTILINE)
        return data

    @staticmethod
    def _clearing_line_breaks(data):
        out = []
        for line in data.split('\n'):
            out.append(line)
        return ' '.join(out)

    def convert(self):
        output = self.str
        output = self._list_re.sub(self._list, output)
        return output
