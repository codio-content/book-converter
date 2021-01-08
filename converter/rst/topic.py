import re


class Topic(object):
    def __init__(self, source_string, caret_token, tags):
        self.str = source_string
        self._caret_token = caret_token
        self._tags = tags
        self._topic_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n\s*)?^\.{2} topic::? +(?P<type>.*?)\n\n*(?P<content>(?:\s+[^\n]+\n*)*)""",
            flags=re.MULTILINE)

    def _topic(self, matchobj):
        caret_token = self._caret_token
        topic_type = matchobj.group('type')
        content = matchobj.group('content')
        content = re.sub(r"\n +", "\n ", content)

        reference = ''
        tag = matchobj.group('tag') if matchobj.group('tag') is not None else False
        if tag and tag in self._tags:
            reference = self._tags[tag]

        return f'\n<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**{topic_type} {reference} **<br/>' \
               f'{caret_token}{caret_token}\n\n{content}\n\n</div><br/>{caret_token}{caret_token}\n'

    def convert(self):
        output = self.str
        output = self._topic_re.sub(self._topic, output)
        return output
