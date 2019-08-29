import re
import logging

from converter.markdown.block_matcher import match_block
from converter.guides.tools import get_text_in_brackets

cite_re = re.compile(r"""~?\\cite{(?P<ref>.*?)}""", flags=re.DOTALL + re.VERBOSE)

bib_re = re.compile(r"""@(?P<type>.*?){(?P<ref>.*?),""", flags=re.DOTALL + re.VERBOSE)


class Cite(object):
    _bib_file = None
    _bib_entries = []

    def __init__(self, latex_str, load_workspace_file):
        self.str = latex_str
        if Cite._bib_file is None:
            Cite._bib_file = {}
            content = load_workspace_file('saasbook.bib')
            if content:
                content_lines = content.split('\n')
                content_lines = list(
                    filter(lambda line: not line.startswith('%') and not line.startswith('#'), content_lines)
                )
                content = '\n'.join(content_lines)

                try:
                    bib_re.sub(self.make_bib_block, content)
                    for entry in Cite._bib_entries:
                        entry_type = entry.get('type')
                        ref = entry.get('ref')
                        token = f'@{entry_type}{{{ref},'

                        def make_bib_content(line):
                            bib_entry = {}
                            for item in line.split(',\n'):
                                item = item.strip()
                                sub_items = item.split('=', 1)
                                if len(sub_items) > 1:
                                    value = sub_items[1].strip()
                                    key = sub_items[0].strip().lower()
                                    if value.startswith('{'):
                                        value = get_text_in_brackets(value)
                                    value = ' '.join(value.split('\n'))
                                    bib_entry[key] = value
                            Cite._bib_file[ref.lower()] = bib_entry
                            return ''
                        match_block(token, content, make_bib_content)
                except BaseException as e:
                    logging.error('can not process bibfile', e)

    def make_bib_block(self, matchobj):
        type = matchobj.group('type')
        ref = matchobj.group('ref')

        Cite._bib_entries.append({
            'type': type,
            'ref': ref
        })

        return ''

    def get_bib_text(self, ref):
        bib_item = Cite._bib_file.get(ref.lower(), {})
        if bib_item:
            if bib_item.get('title') and bib_item.get('author'):
                author = bib_item.get('author')
                title = bib_item.get('title')
                return f'<abbr title="{title}">{author}</abbr>'
            elif bib_item.get('title'):
                return bib_item.get('title')
            elif bib_item.get('author'):
                return bib_item.get('author')
        return ref

    def make_block(self, matchobj):
        ref = matchobj.group('ref')
        return ','.join(list(map(self.get_bib_text, ref.split(','))))

    def convert(self):
        return cite_re.sub(self.make_block, self.str)
