import re


class Refs(object):
    def __init__(self, latex_str, refs):
        self.str = latex_str

        self._refs = refs

        self._refs_re = re.compile(r"""\\ref{(?P<ref_name>.*?)}""", flags=re.DOTALL + re.VERBOSE)
        self._page_refs_re = re.compile(r"""\\pageref{(?P<ref_name>.*?)}""", flags=re.DOTALL + re.VERBOSE)

    def _refs_block(self, matchobj):
        ref_name = matchobj.group('ref_name')
        refs = self._refs.get(ref_name, {'ref': ref_name})
        return '{}'.format(refs.get('ref', ''))

    def _page_refs_block(self, matchobj):
        ref_name = matchobj.group('ref_name')
        refs = self._refs.get(ref_name, {'pageref': ref_name})
        pageref = refs.get('pageref', '')
        if isinstance(pageref, str):
            return 'in section {}'.format(pageref)
        else:
            return str(pageref)

    def convert(self):
        output = self.str
        output = self._refs_re.sub(self._refs_block, output)
        output = self._page_refs_re.sub(self._page_refs_block, output)

        return output
