import re
from collections import namedtuple

TagTopic = namedtuple('TagTopic', ['position', 'tag', 'type'])


class Topic(object):
    def __init__(self, source_string, caret_token, chapter_num, subsection_num, figure_counter):
        self.str = source_string
        self._caret_token = caret_token
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._figure_counter = figure_counter
        self._topics = list()
        self._topic_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n\s*)?^\.{2} topic::? +(?P<type>.*?)\n\n*(?P<content>(?:\s+[^\n]+\n*)*)""",
            flags=re.MULTILINE)

    def _topic(self, matchobj):
        caret_token = self._caret_token
        topic_type = matchobj.group('type')
        content = matchobj.group('content')
        content = re.sub(r"\n +", "\n ", content)
        self._figure_counter += 1

        tag = matchobj.group('tag') if matchobj.group('tag') is not None else False
        if tag:
            self._topics.append(TagTopic(self._figure_counter, matchobj.group('tag'), topic_type))

        return f'\n<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**{topic_type} {self._chapter_num}.{self._subsection_num}.' \
               f'{self._figure_counter}**<br/>' \
               f'{caret_token}{caret_token}\n\n{content}\n\n</div><br/>{caret_token}{caret_token}\n'

    def _set_topic_links_by_tag(self, output):
        for topic in self._topics:
            output = output.replace(f'{topic.type} :num:`#{topic.tag}`',
                                    f'{topic.type} {self._chapter_num}.{self._subsection_num}.{topic.position}')
        return output

    def convert(self):
        output = self.str
        output = self._topic_re.sub(self._topic, output)
        output = self._set_topic_links_by_tag(output)
        return output, self._figure_counter
