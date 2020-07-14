import pathlib
import re
import uuid


class Rst2Markdown(object):
    def __init__(self, lines_array, chapter_num=0, subsection_num=0):
        self._caret_token = str(uuid.uuid4())
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._figure_counter = 0
        self.lines_array = lines_array
        self._heading1_re = re.compile(r"""^(?P<content>.*?\n)?(?:=)+\s*$""", flags=re.MULTILINE)
        self._heading2_re = re.compile(r"""^(?P<content>.*?\n)?(?:-)+\s*$""", flags=re.MULTILINE)
        self._heading3_re = re.compile(r"""^(?P<content>.*?\n)?(?:~)+\s*$""", flags=re.MULTILINE)
        self._heading4_re = re.compile(r"""^(?P<content>.*?\n)?(?:")+\s*$""", flags=re.MULTILINE)
        self._list_re = re.compile(r"""^(?P<type>[#|\d]\.|[*]) (?P<content>.*?\n(?: .*?\n.*?)*)""",
                                   flags=re.MULTILINE + re.DOTALL)
        self._ext_links_re = re.compile(r"""`(?P<name>.*?)\n?<(?P<ref>https?:.*?)>`_""")
        self._ref_re = re.compile(r""":(ref|chap):`(?P<name>.*?)(?P<label_name><.*?>)?`""")
        self._term_re = re.compile(r""":term:`(?P<name>.*?)(<(?P<label_name>.*?)>)?`""")
        self._math_re = re.compile(r""":math:`(?P<content>.*?)`""")
        self._math_block_re = re.compile(r""" {,3}.. math::\n^[\s\S]*?(?P<content>.*?)(?=\n{2,})""",
                                         flags=re.MULTILINE + re.DOTALL)
        self._todo_block_re = re.compile(r"""\.\. TODO::\n(?P<options>^ +:.*?: \S*\n$)(?P<text>.*?\n^$\n(?=\S*)|.*)""",
                                         flags=re.MULTILINE + re.DOTALL)
        self._paragraph_re = re.compile(r"""^(?!\s|\d|#\.|\*|\..).*?(?=\n^\s*$)""", flags=re.MULTILINE + re.DOTALL)
        self._topic_example_re = re.compile(
            r"""^(?!\s)\.\. topic:: (?P<type>Example)\n*^$\n {3}(?P<content>.*?\n^$\n(?=\S)|.*)""",
            flags=re.MULTILINE + re.DOTALL)
        self._epigraph_re = re.compile(r"""^(?!\s)\.\. epigraph::\n*^$\n {3}(?P<content>.*?\n^$\n(?=\S))""",
                                       flags=re.MULTILINE + re.DOTALL)
        self._image_re = re.compile(r"""\.\. odsafig:: (?P<image>.*?)\n*^\s*$\n {6}(?P<caption>.*?\n^$\n(?=\S*))""",
                                    flags=re.MULTILINE + re.DOTALL)
        self._sidebar_re = re.compile(r"""\.\. sidebar:: (?P<name>.*?)\n^$\n(?P<content>.*?)\n^$(?=\S*)""",
                                      flags=re.MULTILINE + re.DOTALL)
        self._inlineav_re = re.compile(
            r"""\.\. inlineav:: (?P<name>.*?) (?P<type>.*?$)\n(?P<options> {3}.*?)(?=^\s*$)""",
            flags=re.MULTILINE + re.DOTALL)
        self._code_lines_re = re.compile(
            r"""^$\n(?P<content> {2}[\S ]*)\n^$""", flags=re.MULTILINE + re.DOTALL)
        self._code_include_re = re.compile(
            r"""\.\. codeinclude:: (?P<path>.*?$)\n(?P<options>^ +:.*?: \S*\n$)?""", flags=re.MULTILINE + re.DOTALL)

    def _heading1(self, matchobj):
        return ''

    def _heading2(self, matchobj):
        content = matchobj.group('content')
        return f'{self._caret_token}## {content}'

    def _heading3(self, matchobj):
        content = matchobj.group('content')
        return f'{self._caret_token}{self._caret_token}### {content}'

    def _heading4(self, matchobj):
        content = matchobj.group('content')
        return f'{self._caret_token}#### {content}'

    def _list(self, matchobj):
        caret_token = self._caret_token
        list_type = matchobj.group('type')
        content = matchobj.group('content')
        content = content.strip()
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(line)
        list_item = ' '.join(out)
        if list_type == '*':
            return f'* {list_item}{caret_token}'
        return f'{list_item}{caret_token}'

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
        content = content.replace("\\+", "+")
        return f'$${content}$$'

    def _math_block(self, matchobj):
        content = matchobj.group('content')
        content = content.strip()
        content = content.replace("\\+", "+")
        return f'<center>$${content}$$</center>'

    def _paragraph(self, matchobj):
        content = matchobj.group(0)
        content = content.replace('\n', ' ')
        return content

    def _topic_example(self, matchobj):
        caret_token = self._caret_token
        topic_type = matchobj.group('type')
        content = matchobj.group('content')
        content = re.sub(r"\n +", "\n ", content)
        self._figure_counter += 1
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**{topic_type} {self._chapter_num}.{self._subsection_num}.' \
               f'{self._figure_counter}**<br/><br/>' \
               f'{caret_token}{caret_token}{content}</div><br/>{caret_token}{caret_token}'

    def _epigraph(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        content = content.strip()
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(line)
        content = '\n'.join(out)
        return f'<div style="padding: 50px;">{caret_token}{content}{caret_token}</div>{caret_token}{caret_token}'

    def _todo_block(self, matchobj):
        return ''

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

    def _code_lines(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        return f'{caret_token}```{caret_token}{content}```{caret_token}'

    def _inlineav(self, matchobj):
        images = {}
        caret_token = self._caret_token
        option_re = re.compile('[\t ]+:([^:]+): (.+)')
        name = matchobj.group('name')
        av_type = matchobj.group('type')
        options = matchobj.group('options')
        options = options.split('\n')
        for opt in options:
            match = option_re.match(opt)
            if match:
                images[match[1]] = match[2]
        script_opt = images.get('scripts')
        script_opt = script_opt.split()
        if len(script_opt) > 0:
            scripts = ''.join(list(map(lambda x: f'<script type="text/javascript" src=".guides/{x}">'
                                                 f'</script>{caret_token}', script_opt)))
            if av_type == 'dgm':
                return f'{caret_token}<div id="{name}" class="ssAV"></div>{caret_token}{scripts}{caret_token}'
            if av_type == 'ss':
                return f'{caret_token}<div id="{name}" class="ssAV">{caret_token}' \
                       f'<span class="jsavcounter"></span>{caret_token}' \
                       f'<a class="jsavsettings" href="#">Settings</a>{caret_token}' \
                       f'<div class="jsavcontrols"></div>{caret_token}' \
                       f'<p class="jsavoutput jsavline"></p>{caret_token}' \
                       f'<div class="jsavcanvas"></div>{caret_token}' \
                       f'</div>{caret_token}{scripts}{caret_token}'

    def _code_include(self, matchobj):
        options = {}
        lines = []
        content = ''
        tag = None
        caret_token = self._caret_token
        curr_dir = pathlib.Path.cwd().parent
        code_dir = curr_dir.joinpath('OpenDSA/SourceCode')
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
                    tag = options.get('tag')
        file_path = pathlib.Path(path)
        if not str(file_path).endswith(".java"):
            file_path = "{}.java".format(file_path)
        if not str(file_path).startswith('Java'):
            java_dir = pathlib.Path('Java')
            file_path = java_dir.joinpath(file_path)
        file = code_dir.joinpath(file_path).resolve()
        if file.exists():
            lines = self.load_file(file)
        if lines:
            for line in lines:
                if not line:
                    continue
                if tag:
                    start_tag_string = f'/* *** ODSATag: {tag} *** */'
                    end_tag_string = f'/* *** ODSAendTag: {tag} *** */'
                    if line.startswith(start_tag_string):
                        content = ''
                        continue
                    if line.startswith(end_tag_string):
                        return f'{caret_token}```{caret_token}{content}{caret_token}```{caret_token}{caret_token}'
                line = re.sub(r"/\* \*\*\* .*? \*\*\* \*/", "", line)
                content += line
        return f'{caret_token}```{caret_token}{content}{caret_token}```{caret_token}{caret_token}'

    def _enum_lists_parse(self, lines):
        counter = 0
        list_flag = False
        for ind, line in enumerate(lines):
            next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
            if line.startswith('#. '):
                list_flag = True
                counter += 1
                lines[ind] = line.replace("#", str(counter), 1)
            if not next_line[:1] and next_line != '' and not next_line.startswith('#. ') and list_flag:
                list_flag = False
                counter = 0
        return lines

    def get_figure_counter(self):
        return self._figure_counter

    def load_file(self, path):
        with open(path, 'r') as file:
            return file.readlines()

    def to_markdown(self):
        self.lines_array = self._enum_lists_parse(self.lines_array)
        output = '\n'.join(self.lines_array)
        output = re.sub(r"\|---\|", "--", output)
        output = re.sub(r"^\|$", "<br/>", output, flags=re.MULTILINE)
        output = re.sub(r"\+\+", "\\+\\+", output)
        output = self._todo_block_re.sub(self._todo_block, output)
        output = self._inlineav_re.sub(self._inlineav, output)
        output = self._heading1_re.sub(self._heading1, output)
        output = self._heading2_re.sub(self._heading2, output)
        output = self._heading3_re.sub(self._heading3, output)
        output = self._heading4_re.sub(self._heading4, output)
        output = self._list_re.sub(self._list, output)
        output = self._ext_links_re.sub(self._ext_links, output)
        output = self._ref_re.sub(self._ref, output)
        output = self._term_re.sub(self._term, output)
        output = self._math_re.sub(self._math, output)
        output = self._math_block_re.sub(self._math_block, output)
        output = self._paragraph_re.sub(self._paragraph, output)
        output = self._topic_example_re.sub(self._topic_example, output)
        output = self._epigraph_re.sub(self._epigraph, output)
        output = self._sidebar_re.sub(self._sidebar, output)
        output = self._code_lines_re.sub(self._code_lines, output)
        output = self._code_include_re.sub(self._code_include, output)
        output = re.sub(self._caret_token, "\n", output)
        output = self._image_re.sub(self._image, output)
        output = re.sub(self._caret_token, "\n", output)
        return output
