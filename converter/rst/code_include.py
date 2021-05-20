import re
import logging
from pathlib import Path

SOURCE_CODE_DICT = {
    'java': {
        'name': 'Java',
        'ext': ['java']
    },
    'c++': {
        'name': 'C++',
        'ext': ['cpp', 'h']
    },
    'python': {
        'name': 'Python',
        'ext': ['py']
    },
}


class CodeInclude(object):
    def __init__(self, source_string, caret_token, workspace_dir, load_file_method, source_code_dir, source_code):
        self.str = source_string
        self._caret_token = caret_token
        self._workspace_dir = workspace_dir
        self._load_file = load_file_method
        self.source_code = source_code
        self.source_code_dir = source_code_dir
        self._code_include_re = re.compile(r"""\.\. codeinclude:: (?P<path>.*?) *\n(?P<options>(?: +:.*?: .*?\n)+)?""")

    def _code_include(self, matchobj):
        lines = []
        caret_token = self._caret_token
        opt = matchobj.group('options')
        tag = self._get_tag_by_opt(opt) if opt else None
        file_path = self._get_file_path(matchobj)
        try:
            lines = self._load_file(file_path)
        except BaseException as e:
            logging.error(e)
        content = self._get_content(lines, tag) if lines else ''
        return f'{caret_token}```{caret_token}{content}```{caret_token}{caret_token}'

    def _get_file_path(self, matchobj):
        source_code_path = self._workspace_dir.joinpath(self.source_code_dir)
        rel_file_path = Path(matchobj.group('path').strip())
        file_path = source_code_path.joinpath(rel_file_path).resolve()
        if Path(file_path).is_file():
            return file_path

        file_path = None
        lang_key = self.source_code.lower() if (self.source_code.lower() in SOURCE_CODE_DICT) else 'java'
        lang = SOURCE_CODE_DICT.get(lang_key)
        lang_dir = Path(lang['name'])

        for ext in lang['ext']:
            path = source_code_path.joinpath(lang_dir.joinpath(f'{rel_file_path}.{ext}')).resolve()
            if Path(path).exists():
                file_path = path
        java_lang = SOURCE_CODE_DICT.get('java')
        path_for_java = source_code_path.joinpath(Path(java_lang['name']).joinpath(f'{rel_file_path}.java')).resolve()
        if not file_path and Path(path_for_java).exists():
            file_path = path_for_java
        path_for_pseudo = source_code_path.joinpath(Path('Pseudo').joinpath(f'{rel_file_path}.txt')).resolve()
        if not file_path and Path(path_for_pseudo).exists():
            file_path = path_for_pseudo
        return file_path

    @staticmethod
    def _get_tag_by_opt(opt):
        option_re = re.compile('[\t ]+:([^:]+): (.+)')
        opt = opt.split('\n')
        for item in opt:
            match = option_re.match(item)
            if match and match[1] == "tag":
                return match[2]
        return ''

    def _get_content(self, lines, tag):
        tag = tag.strip() if tag else tag
        start_tag_string = f'/* *** ODSATag: {tag} *** */' if tag else False
        end_tag_string = f'/* *** ODSAendTag: {tag} *** */' if tag else False
        content = ''
        for line in lines:
            if not line:
                continue
            if start_tag_string and start_tag_string in line:
                content = ''
                continue
            if end_tag_string and end_tag_string in line:
                break
            line = re.sub(r"/\* \*\*\* .*? \*\*\* \*/", "", line)
            content += line.rstrip("\n") + self._caret_token
        return content

    def convert(self):
        output = self.str
        output = self._code_include_re.sub(self._code_include, output)
        return output
