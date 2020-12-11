import re
import pathlib
import logging


class CodeInclude(object):
    def __init__(self, source_string, caret_token, workspace_dir, load_file_method):
        self.str = source_string
        self._caret_token = caret_token
        self._workspace_dir = workspace_dir
        self._load_file = load_file_method
        self._code_include_re = re.compile(r"""\.\. codeinclude:: (?P<path>.*?) *\n(?P<options>(?: +:.*?: .*?\n)+)?""")

    def _code_include(self, matchobj):
        lines = []
        caret_token = self._caret_token
        curr_dir = self._workspace_dir
        code_dir = curr_dir.joinpath('SourceCode')
        path = matchobj.group('path').strip()
        path = pathlib.Path(path)
        opt = matchobj.group('options')
        tag = self._get_tag_by_opt(opt) if opt else None
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

        content = self._get_content(lines, tag) if lines else ''
        return f'{caret_token}```{caret_token}{content.strip()}{caret_token}```{caret_token}{caret_token}'

    @staticmethod
    def _get_tag_by_opt(opt):
        option_re = re.compile('[\t ]+:([^:]+): (.+)')
        options = {}
        tag = None
        opt = opt.split('\n')
        for item in opt:
            match = option_re.match(item)
            if match:
                options[match[1]] = match[2]
                tag = options.get('tag', '')
        return tag

    @staticmethod
    def _get_content(lines, tag):
        start_tag_string = f'/* *** ODSATag: {tag} *** */' if tag else False
        end_tag_string = f'/* *** ODSAendTag: {tag} *** */' if tag else False
        content = ''
        for line in lines:
            if not line:
                continue
            if start_tag_string and line.strip().startswith(start_tag_string):
                content = ''
                continue
            if end_tag_string and line.strip().startswith(end_tag_string):
                break
            line = re.sub(r"/\* \*\*\* .*? \*\*\* \*/", "", line)
            content += line
        return content

    def convert(self):
        output = self.str
        output = self._code_include_re.sub(self._code_include, output)
        return output
