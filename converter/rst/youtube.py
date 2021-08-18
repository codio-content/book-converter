import re


class Youtube(object):
    def __init__(self, source_string, caret_token):
        self.str = source_string
        self._caret_token = caret_token
        self._youtube_re = re.compile(r"""^ *\.\.\s+youtube:: ?(?P<id>.*?)?\n(?P<options>.*?)\n(?=\S)""",
                                      flags=re.MULTILINE + re.DOTALL)

    def _youtube(self, matchobj):
        options = {}
        caret_token = self._caret_token
        id = matchobj.group('id')
        options_group = matchobj.group('options').split('\n')
        option_re = re.compile(':([^:]+): (.+)')
        for line in options_group:
            line = line.strip()
            opt_match = option_re.match(line)
            if opt_match:
                options[opt_match[1]] = opt_match[2]
        width = options.get('width', '')
        height = options.get('height', '')

        return f'<div>{caret_token} <iframe width="{width}" height="{height}" ' \
               f'src="https://www.youtube.com/embed/{id}?autoplay=1" frameborder="0" allowfullscreen></iframe>' \
               f'{caret_token}</div>{caret_token}<br>{caret_token}{caret_token}\n'

    def convert(self):
        output = self._youtube_re.sub(self._youtube, self.str)
        return output
