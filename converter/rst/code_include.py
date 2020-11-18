import re
import pathlib
import logging


class CodeInclude(object):
    def __init__(self, source_string, caret_token, workspace_dir, load_file_method):
        self.str = source_string
        self._caret_token = caret_token
        self._workspace_dir = workspace_dir
        self._load_file = load_file_method
        self._code_include_re = re.compile(r"""\.\. codeinclude:: (?P<path>.*?)\n(?P<options>(?: +:.*?: \S*\n)+)?""")

    def _code_include(self, matchobj):
        options = {}
        lines = []
        content = ''
        tag = None
        caret_token = self._caret_token
        curr_dir = self._workspace_dir
        code_dir = curr_dir.joinpath('SourceCode')
        option_re = re.compile('[\t ]+:([^:]+): (.+)')
        path = matchobj.group('path').strip()
        path = pathlib.Path(path)
        opt = matchobj.group('options')
        if opt:
            opt = opt.split('\n')
            for item in opt:
                match = option_re.match(item)
                if match:
                    options[match[1]] = match[2]
                    tag = options.get('tag', '')
        file_path = pathlib.Path(path)
        if not str(file_path).endswith(".java"):
            file_path = "{}.java".format(file_path)
        if not str(file_path).startswith('Java'):
            java_dir = pathlib.Path('Java')
            file_path = java_dir.joinpath(file_path)
        file = code_dir.joinpath(file_path).resolve()
        try:
            lines = self._load_file(file)
        except BaseException as e:
            logging.error(e)
        if lines:
            for line in lines:
                if not line:
                    continue
                if tag:
                    start_tag_string = f'/* *** ODSATag: {tag} *** */'
                    end_tag_string = f'/* *** ODSAendTag: {tag} *** */'
                    if line.strip().startswith(start_tag_string):
                        content = ''
                        continue
                    if line.strip().startswith(end_tag_string):
                        return f'{caret_token}```{caret_token}{content}{caret_token}```{caret_token}{caret_token}'
                line = re.sub(r"/\* \*\*\* .*? \*\*\* \*/", "", line)
                content += line
        return f'{caret_token}```{caret_token}{content}{caret_token}```{caret_token}{caret_token}'

    def convert(self):
        output = self.str
        output = self._code_include_re.sub(self._code_include, output)
        return output
