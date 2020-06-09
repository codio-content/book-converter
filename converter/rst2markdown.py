import re
import uuid


class Rst2Markdown(object):
    def __init__(self, lines_array, chapter_num=1):
        self._caret_token = str(uuid.uuid4())
        self._chapter_num = chapter_num
        self.lines_array = lines_array
        self._heading1_re = re.compile(r"""^(?P<content>.*?\n)?(?:=)+\s*$""", flags=re.MULTILINE)
        self._heading2_re = re.compile(r"""^(?P<content>.*?\n)?(?:-)+\s*$""", flags=re.MULTILINE)
        self._heading3_re = re.compile(r"""^(?P<content>.*?\n)?(?:~)+\s*$""", flags=re.MULTILINE)
        self._heading4_re = re.compile(r"""^(?P<content>.*?\n)?(?:")+\s*$""", flags=re.MULTILINE)
        self._num_list_re = re.compile(r"""^#\. (?P<content>.*?)\s*?^$""", flags=re.MULTILINE + re.DOTALL)
        self._code_re = re.compile(r"""^(?P<content>(?: {3}(?!:)| {2}if).*?)\n^$""", flags=re.MULTILINE + re.DOTALL)
        self._ext_links_re = re.compile(r"""`(?P<name>.*?)\n?<(?P<ref>https?:.*?)>`_""")
        self._ref_re = re.compile(r""":ref:`(?P<name>.*?)(?P<label_name><.*?>)?`""")
        self._term_re = re.compile(r""":term:`(?P<name>.*?)(<(?P<label_name>.*?)>)?`""")
        self._math_re = re.compile(r""":math:`(?P<content>.*?)`""")
        self._math_block_re = re.compile(r""" {,3}.. math::\n^[\s\S]*?(?P<content>.*?)(?=\n{2,})""",
                                         flags=re.MULTILINE + re.DOTALL)
        self._paragraph_re = re.compile(r"""^(?!\s|\d|#\.|\*|\..).*?(?=\n^\s*$)""", flags=re.MULTILINE + re.DOTALL)
        self._topic_example_re = re.compile(
            r"""^(?!\s)\.\. topic:: (?P<type>Example)\n*^$\n {3}(?P<content>.*?\n^$\n(?=\S))""",
            flags=re.MULTILINE + re.DOTALL)
        self._epigraph_re = re.compile(r"""^(?!\s)\.\. epigraph::\n*^$\n {3}(?P<content>.*?\n^$\n(?=\S))""",
                                       flags=re.MULTILINE + re.DOTALL)
        self._image_re = re.compile(r"""\.\. odsafig:: (?P<image>.*?)\n*^\s*$\n {6}(?P<caption>.*?\n^$\n(?=\S*))""",
                                    flags=re.MULTILINE + re.DOTALL)
        self._sidebar_re = re.compile(r"""\.\. sidebar:: (?P<name>.*?)\n^$\n(?P<content>.*?)\n^$(?=\S*)""",
                                      flags=re.MULTILINE + re.DOTALL)

    def _heading1(self, matchobj):
        return ''

    def _heading2(self, matchobj):
        content = matchobj.group('content')
        return f'## {content}'

    def _heading3(self, matchobj):
        content = matchobj.group('content')
        return f'### {content}'

    def _heading4(self, matchobj):
        content = matchobj.group('content')
        return f'#### {content}'

    def _num_list(self, matchobj):
        content = matchobj.group('content')
        content = content.strip()
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(line)
        list_item = ' '.join(out)
        return f'1. {list_item}'

    def _ext_links(self, matchobj):
        name = matchobj.group('name')
        ref = matchobj.group('ref')
        name = name.strip()
        return f'[{name}]({ref})'

    def _ref(self, matchobj):
        name = matchobj.group('name')
        name = name.strip()
        label_name = matchobj.group('label_name')
        return f'Chapter: **{name}**'

    def _term(self, matchobj):
        name = matchobj.group('name')
        name = name.strip()
        label_name = matchobj.group('label_name')
        return f'**{name}**'

    def _math(self, matchobj):
        content = matchobj.group('content')
        return f'$${content}$$'

    def _math_block(self, matchobj):
        content = matchobj.group('content')
        return f'  <center>$${content}$$</center>'

    def _paragraph(self, matchobj):
        content = matchobj.group(0)
        content = content.replace('\n', ' ')
        return content

    def _topic_example(self, matchobj):
        caret_token = self._caret_token
        topic_type = matchobj.group('type')
        content = matchobj.group('content')
        content = content.strip()
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**{topic_type}**<br/><br/>' \
               f'{caret_token}{caret_token}{content}</div><br/>{caret_token}{caret_token}'

    def _epigraph(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        return f'<div style="padding: 30px;">{content}{caret_token}</div>{caret_token}{caret_token}'

    def _code(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        return f'{caret_token}```{caret_token}{content}{caret_token}```{caret_token}'

    def _image(self, matchobj):
        caret_token = self._caret_token
        image = matchobj.group('image')
        caption = matchobj.group('caption')
        caption = caption.strip()
        return f'![{caption}]({image}){caret_token}{caption}{caret_token}{caret_token}'

    def _sidebar(self, matchobj):
        caret_token = self._caret_token
        name = matchobj.group('name')
        content = matchobj.group('content')
        content = content.strip()
        return f'{caret_token}|||xdiscipline{caret_token}{caret_token}**{name}**{caret_token}{caret_token}' \
               f'{content}{caret_token}{caret_token}|||{caret_token}{caret_token}'

    def to_markdown(self):
        output = '\n'.join(self.lines_array)
        output = re.sub(r"\|---\|", "--", output)
        output = self._heading1_re.sub(self._heading1, output)
        output = self._heading2_re.sub(self._heading2, output)
        output = self._heading3_re.sub(self._heading3, output)
        output = self._heading4_re.sub(self._heading4, output)
        output = self._num_list_re.sub(self._num_list, output)
        output = self._ext_links_re.sub(self._ext_links, output)
        output = self._ref_re.sub(self._ref, output)
        output = self._term_re.sub(self._term, output)
        output = self._math_re.sub(self._math, output)
        output = self._math_block_re.sub(self._math_block, output)
        output = self._topic_example_re.sub(self._topic_example, output)
        output = self._epigraph_re.sub(self._epigraph, output)
        output = self._sidebar_re.sub(self._sidebar, output)
        output = re.sub(self._caret_token, "\n", output)
        output = self._image_re.sub(self._image, output)
        output = self._code_re.sub(self._code, output)
        output = re.sub(self._caret_token, "\n", output)
        return output
