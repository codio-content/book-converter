import logging
import pathlib
import re
import uuid

from converter.guides.tools import slugify
from string import Template
from collections import namedtuple

from converter.rst.table import Table
from converter.rst.image import Image
from converter.rst.sidebar import Sidebar
from converter.rst.external_link import ExternalLink
from converter.rst.footnote import Footnote

AssessmentData = namedtuple('AssessmentData', ['id', 'name', 'type', 'points', 'ex_data'])
IframeImage = namedtuple('IframeImage', ['src', 'path', 'content'])
OPEN_DSA_CDN = 'https://global.codio.com/opendsa/v3'
GUIDES_CDN = '//static-assets.codio.com/guides/opendsa/v1'
MATHJAX_CDN = '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1'
JSAV_IFRAME_SUBPATH = 'jsav/iframe/v6/'
JSAV_IMAGE_IFRAME = f"""
<html>
<head>
<title>$title</title>
<link rel="stylesheet" href="{GUIDES_CDN}/haiku.css" type="text/css" />
<link rel="stylesheet" href="{GUIDES_CDN}/normalize.css" type="text/css" />
<link rel="stylesheet" href="{GUIDES_CDN}/JSAV.css" type="text/css" />
<link rel="stylesheet" href="{GUIDES_CDN}/odsaMOD-min.css" type="text/css" />
<link rel="stylesheet" href="{GUIDES_CDN}/jquery-ui.css" type="text/css" />
<link rel="stylesheet" href="{GUIDES_CDN}/odsaStyle-min.css" type="text/css" />

<script type="text/javascript" src="{GUIDES_CDN}/jquery-2.1.4.min.js"></script>
<script type="text/javascript" src="{MATHJAX_CDN}/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/javascript" src="{GUIDES_CDN}/jquery-ui.min.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/jquery.transit.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/raphael.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/JSAV-min.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/odsaUtils-min.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/odsaMOD-min.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/d3.min.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/d3-selection-multi.v1.min.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/dataStructures.js"></script>
<script type="text/javascript" src="{GUIDES_CDN}/conceptMap.js"></script>
</head>
<body>
$content
<script>
window.addEventListener("load", sendPostMessage);
var element = document.getElementById('$name');
if (element) {{
    element.addEventListener("resize", sendPostMessage);
    element.addEventListener("click", sendPostMessage);
}}
var height;
function sendPostMessage() {{
    if (height !== element.offsetHeight && element) {{
        height = element.offsetHeight;
        window.parent.postMessage(
            JSON.stringify({{frameHeight: height, frameId: "$name", status: 'iframe', av: "$name"}}), '*'
        );
    }}
}}
</script>
</body>
</html>
"""


class Rst2Markdown(object):
    def __init__(self, lines_array, exercises, workspace_dir=pathlib.Path('.'), chapter_num=0, subsection_num=0):
        self._caret_token = str(uuid.uuid4())
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._figure_counter = 0
        self._assessments = list()
        self._iframe_images = list()
        self.lines_array = lines_array
        self._exercises = exercises
        self.workspace_dir = workspace_dir
        self._heading1_re = re.compile(r"""^(?P<content>.*?\n)?(?:=)+\s*$""", flags=re.MULTILINE)
        self._heading2_re = re.compile(r"""^(?P<content>.*?\n)?(?:-)+\s*$""", flags=re.MULTILINE)
        self._heading3_re = re.compile(r"""^(?P<content>.*?\n)?(?:~)+\s*$""", flags=re.MULTILINE)
        self._heading4_re = re.compile(r"""^(?P<content>.*?\n)?(?:")+\s*$""", flags=re.MULTILINE)
        self._list_re = re.compile(r"""^( *)(?P<type>[*+\-]|[0-9#]+[\.]) [^\n]*(?:\n(?!\1\2|\S)[^\n]*)*""",
                                   flags=re.MULTILINE)
        self._ext_links_re = re.compile(r"""`(?P<name>.*?)\n?<(?P<ref>https?:.*?)>`_""")
        self._ref_re = re.compile(r""":(ref|chap):`(?P<name>.*?)(?P<label_name><.*?>)?`""", flags=re.DOTALL)
        self._term_re = re.compile(r""":term:`(?P<name>.*?)(<(?P<label_name>.*?)>)?`""", flags=re.DOTALL)
        self._math_re = re.compile(r""":math:`(?P<content>.*?)`""")
        self._math_block_re = re.compile(r""" {,3}.. math::\n^[\s\S]*?(?P<content>.*?)(?=\n{2,})""",
                                         flags=re.MULTILINE + re.DOTALL)
        self._todo_block_re = re.compile(r"""\.\. TODO::\n(?P<options>^ +:.*?: \S*\n$)(?P<text>.*?\n^$\n(?=\S*)|.*)""",
                                         flags=re.MULTILINE + re.DOTALL)
        self._paragraph_re = re.compile(r"""^(?!\s|\d\. |#\. |\* |- |\.\. ).*?(?=\n^\s*$)""",
                                        flags=re.MULTILINE + re.DOTALL)
        self._topic_re = re.compile(
            r"""^\.{2} topic:{2} +(?P<type>.*?)\n(?P<content>(?:\n* +[^\n]+\n*)*)""", flags=re.MULTILINE + re.DOTALL)
        self._tip_re = re.compile(
            r"""^\.{2} tip:{2} *\n(?P<content>(?:\n* +[^\n]+\n*)*)""", flags=re.MULTILINE)
        self._epigraph_re = re.compile(r"""[ ]*\.\. epigraph:: *\n*(?P<content>(?: +[^\n]+\n*)*)""")
        self._inlineav_re = re.compile(
            r"""(\.\. _.*?:\n^$\n)?\.\. inlineav:: (?P<name>.*?) (?P<type>.*?)(?P<options>:.*?: .*?\n)+(?=\S|$)""",
            flags=re.MULTILINE + re.DOTALL
        )
        self._avembed_re = re.compile(
            r"""\s*\.\. avembed:: (?P<name>.*?) (?P<type>[a-z]{2})\n(?P<options>(\s+:.*?:\s+.*\n)+)?"""
        )
        self._code_include_re = re.compile(r"""\.\. codeinclude:: (?P<path>.*?)\n(?P<options>(?: +:.*?: \S*\n)+)?""")
        self._extrtoolembed_re = re.compile(
            r"""^$\n^.*?\n-+\n\n?\.\. extrtoolembed:: '(?P<name>.*?)'\n( *:.*?: .*?\n)?(?=\S|$)""", flags=re.MULTILINE)
        self._term_def_re = re.compile(r"""^:(?P<term>[^:\n]+): *\n(?P<content>(?: +[^\n]+\n*)*)""", flags=re.MULTILINE)
        self._lineblock_re = re.compile(r"""^((?: {2,})?\|)[^\n]*(?:\n(?:\1| {2,})[^\n]+)*""", flags=re.MULTILINE)

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
        content = matchobj.group(0)
        content = content.strip()
        items = []
        match_all_items = list(re.finditer(r'^( *)([*+-]|[0-9#]+[.]) [\s\S]+?(?:\n{2,}(?! )(?!\1\2 |\S)\n*|\s*$)',
                                           content, flags=re.MULTILINE))
        if len(match_all_items) > 1:
            for item in match_all_items:
                item = f'{item.group(0)}{caret_token}'
                item = self._clearing_line_breaks(item)
                items.append(item)
            content = '\n'.join(items)
        else:
            content = self._clearing_text_spaces(content)
            content = self._clearing_line_breaks(content)
        return f'{content}{caret_token}'

    def _clearing_text_spaces(self, data):
        space = re.search('\n *', data)
        if space:
            space_count = len(space.group(0))
            space_regex = f"\n^ {{{space_count}}}"
            data = re.sub(space_regex, '', data, flags=re.MULTILINE)
        return data

    def _clearing_line_breaks(self, data):
        out = []
        for line in data.split('\n'):
            out.append(line)
        return ' '.join(out)

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

    def _topic(self, matchobj):
        caret_token = self._caret_token
        topic_type = matchobj.group('type')
        content = matchobj.group('content')
        content = re.sub(r"\n +", "\n ", content)
        self._figure_counter += 1
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**{topic_type} {self._chapter_num}.{self._subsection_num}.' \
               f'{self._figure_counter}**<br/><br/>' \
               f'{caret_token}{caret_token}{content}</div><br/>{caret_token}{caret_token}'

    def _tip(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        return f'<div style="padding: 20px; border: 1px; border-style: solid; border-color: silver;">' \
               f'{caret_token}{caret_token}**Tip**{caret_token}{caret_token}{content}' \
               f'</div><br/>{caret_token}{caret_token}'

    def _epigraph(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group('content')
        content = content.strip()
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(line)
        content = '\n'.join(out)
        return f'<div style="padding: 10px 30px;">{caret_token}{content}{caret_token}</div>{caret_token}{caret_token}'

    def _lineblock(self, matchobj):
        caret_token = self._caret_token
        content = matchobj.group(0)
        content = re.sub(r'^( *\| ?| {2,})', '', content, flags=re.MULTILINE)
        out = []
        for line in content.split('\n'):
            line = line.strip()
            out.append(f' {line}')
        content = '\n'.join(out)
        return f' <div style="padding-left: 50px;">{caret_token}{content}{caret_token} </div>{caret_token}'

    def _todo_block(self, matchobj):
        return ''

    def _term_def(self, matchobj):
        caret_token = self._caret_token
        term = matchobj.group('term')
        content = matchobj.group('content')
        space = re.search('\n *', content)
        space_count = len(space.group(0)) - 1
        space_regex = f"\n^ {{{space_count}}}"
        content = re.sub(space_regex, '', content, flags=re.MULTILINE)
        content = content.strip()
        return f'{caret_token}**{term}**: {content}{caret_token}{caret_token}'

    def _code_lines(self, data):
        flag = False
        lines = data.split("\n")
        for ind, line in enumerate(lines):
            prev_line = lines[ind - 1]
            next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
            indent_size = len(line) - len(line.lstrip())
            if not prev_line.strip() and line.strip():
                if indent_size == 2 or indent_size == 3:
                    flag = True
            if flag and not line.strip().startswith(":"):
                lines[ind] = line.replace(line, f"```{line}```")
            if flag:
                if not next_line.strip() or indent_size < 2:
                    flag = False
        return "\n".join(lines)

    def _extrtoolembed(self, matchobj):
        name = matchobj.group('name').lower()
        ex_data = self._exercises.get(name.lower(), {})
        assessment_id = f'test-{name.lower()}'
        if not ex_data:
            return ''
        assessment = AssessmentData(assessment_id, name, 'test', 20, ex_data)
        self._assessments.append(assessment)
        return ''

    def _avembed(self, matchobj):
        caret_token = self._caret_token
        file_name = matchobj.group('name')
        # todo: check different type
        av_type = matchobj.group('type')
        # todo: verify options
        # options = matchobj.group('options')
        name = pathlib.Path(file_name).stem

        # todo: future todos: upload and use cdn path

        assessment_id = f'custom-{name.lower()}'
        assessment = AssessmentData(assessment_id, name, 'custom', 1, {'question': 'Resolve the challenge above'})
        self._assessments.append(assessment)

        return f'{caret_token}<iframe id="{name}_iframe" src="{OPEN_DSA_CDN}/{file_name}' \
               f'?selfLoggingEnabled=false&localMode=true&JXOP-debug=true&JOP-lang=en&JXOP-code=java' \
               f'&scoringServerEnabled=false&threshold=5&amp;points=1.0&required=True" ' \
               f'class="embeddedExercise" width="950" height="800" data-showhide="show" scrolling="yes" ' \
               f'style="position: relative; top: 0px;">Your browser does not support iframes.</iframe>' \
               f'{caret_token}{caret_token}{{Check It!|assessment}}({assessment_id}){caret_token}{caret_token}'

    def _inlineav(self, matchobj):
        images = {}
        caption = ""
        caret_token = self._caret_token
        option_re = re.compile(':([^:]+): (.+)')
        name = matchobj.group('name')
        av_type = matchobj.group('type')
        av_type = av_type.strip()
        options = matchobj.group('options')
        options = options.split('\n')
        for line in options:
            line = line.strip()
            opt_match = option_re.match(line)
            if opt_match:
                images[opt_match[1]] = opt_match[2]
            elif line.strip():
                caption += f'{line} '
        script_opt = images.get('scripts', '')
        script_opt = script_opt.split()
        css_opt = images.get('links', '')
        css_opt = css_opt.split()
        self._figure_counter += 1
        counter = f'{self._chapter_num}.{self._subsection_num}.{self._figure_counter}'
        if caption:
            caption = caption.strip()
            caption = f'<center>{counter} {caption}</center><br/>{caret_token}{caret_token}'
        scripts = ''.join(list(map(lambda x: f'<script type="text/javascript" src="{OPEN_DSA_CDN}/{x}">'
                                             f'</script>{caret_token}', script_opt)))
        css_links = ''.join(list(map(lambda x: f'<link rel="stylesheet" type="text/css" href="{OPEN_DSA_CDN}/{x}"/>'
                                               f'{caret_token}', css_opt)))
        iframe_name = slugify(name)
        """
        reason for subpath - some dynamic images have relative imports like ../../../SourceCode/target_file
        and it allow load it in correct way from cdn root
        """

        iframe_src = f'{OPEN_DSA_CDN}/{JSAV_IFRAME_SUBPATH}{iframe_name}.html'
        iframe_content = ''

        if av_type == 'dgm':
            iframe_content = f'{css_links}\n' \
                             f'<div style="margin: 0" id="{name}"></div>\n' \
                             f'{scripts}\n'
        if av_type == 'ss':
            iframe_content = f'{css_links}\n' \
                             f'<div style="margin: 0" id="{name}" class="ssAV">\n' \
                             f'<span class="jsavcounter"></span>\n' \
                             f'<a class="jsavsettings" href="#">Settings</a>\n' \
                             f'<div class="jsavcontrols"></div>\n' \
                             f'<p class="jsavoutput jsavline"></p>\n' \
                             f'<div class="jsavcanvas"></div>\n' \
                             f'</div>\n{scripts}\n'

        iframe_content = re.sub(caret_token, '\n', iframe_content)
        iframe_body = Template(JSAV_IMAGE_IFRAME).substitute(title=name, content=iframe_content, name=name)

        self._iframe_images.append(IframeImage(iframe_src, f'{JSAV_IFRAME_SUBPATH}{iframe_name}.html', iframe_body))
        iframe_height = self.detect_height_from_css(css_opt, name)

        return f'{caret_token}<iframe id="{name}_iframe" src="{iframe_src}" ' \
               f'width="900" height="{iframe_height}" scrolling="no" ' \
               f'style="position: relative; top: 0px; border: 0; margin: 0; overflow: hidden;">' \
               f'Your browser does not support iframes.</iframe>{caret_token}' \
               f'<br/>{caret_token}{caption}{caret_token}'

    def detect_height_from_css(self, css_names, image_id):
        for css_name in css_names:
            css_path = self.workspace_dir.joinpath(css_name)
            if not css_path.exists():
                continue
            with open(css_path, 'r') as file:
                css_content = file.read().replace('\n', '')
                result = re.match(rf"""#{image_id}(?P<content>.*?)}}""", css_content)
                if result:
                    css_height_opt = result.group('content')
                    result_height = re.match(r""".*{.*height(\s)*:(\s)*(?P<height>\d+)px""", css_height_opt)
                    if result_height:
                        iframe_height = int(result_height.group('height'))
                        return iframe_height + 30
        return 250

    def _code_include(self, matchobj):
        options = {}
        lines = []
        content = ''
        tag = None
        caret_token = self._caret_token
        curr_dir = self.workspace_dir
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
            lines = self.load_file(file)
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

    def _enum_lists_parse(self, lines):
        counter = 0
        list_flag = False
        for ind, line in enumerate(lines):
            next_line = lines[ind + 1] if ind + 1 < len(lines) else ''
            if line.startswith('#. ') or line.startswith('   #. '):
                list_flag = True
                counter += 1
                lines[ind] = line.replace("#", str(counter), 1)
            if next_line[:1].strip() and not next_line.startswith('#. ') \
                    and not next_line.startswith('   #. ') and list_flag:
                list_flag = False
                counter = 0
        return lines

    def get_figure_counter(self):
        return self._figure_counter

    def load_file(self, path):
        with open(path, 'r') as file:
            return file.readlines()

    def get_assessments(self):
        return self._assessments

    def get_iframe_images(self):
        return self._iframe_images

    def to_markdown(self):
        self.lines_array = self._enum_lists_parse(self.lines_array)
        output = '\n'.join(self.lines_array)
        # output = re.sub(r".. _[\S ]+:", "", output)  # todo: line moved below. removes tags for images
        output = re.sub(r"\|---\|", "--", output)
        output = re.sub(r"\+\+", "\\+\\+", output)
        output = re.sub(r"^\|$", "<br/>", output, flags=re.MULTILINE)
        output = self._extrtoolembed_re.sub(self._extrtoolembed, output)
        output = self._heading1_re.sub(self._heading1, output)
        output = self._heading2_re.sub(self._heading2, output)
        output = self._heading3_re.sub(self._heading3, output)
        output = self._heading4_re.sub(self._heading4, output)
        output = self._term_def_re.sub(self._term_def, output)
        output = self._lineblock_re.sub(self._lineblock, output)
        output = self._topic_re.sub(self._topic, output)
        output = self._tip_re.sub(self._tip, output)
        output = Image(output, self._caret_token, self._chapter_num, self._subsection_num).convert()
        output = re.sub(r".. _[\S ]+:", "", output)  # todo: line moved below. removes tags for images
        output = self._inlineav_re.sub(self._inlineav, output)
        output = self._avembed_re.sub(self._avembed, output)
        output = self._list_re.sub(self._list, output)
        output = self._ext_links_re.sub(self._ext_links, output)
        output = self._ref_re.sub(self._ref, output)
        output = self._term_re.sub(self._term, output)
        output = self._math_re.sub(self._math, output)
        output = self._math_block_re.sub(self._math_block, output)
        output = self._epigraph_re.sub(self._epigraph, output)
        output = self._paragraph_re.sub(self._paragraph, output)
        output = Sidebar(output, self._caret_token).convert()
        output = Table(output).convert()
        output = ExternalLink(output).convert()
        output = self._code_lines(output)
        output = self._code_include_re.sub(self._code_include, output)
        output = self._todo_block_re.sub(self._todo_block, output)
        output = Footnote(output).convert()
        output = re.sub(self._caret_token, "\n", output)
        return output
