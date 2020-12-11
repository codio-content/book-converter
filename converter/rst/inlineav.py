import re
from converter.guides.tools import slugify
from string import Template
from collections import namedtuple

Figure = namedtuple('Figure', ['position', 'tag'])
IframeImage = namedtuple('IframeImage', ['src', 'path', 'content'])
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


class InlineAv(object):
    def __init__(self, source_string,
                 caret_token, workspace_dir,
                 chapter_num, subsection_num,
                 open_dsa_cdn, figure_counter):
        self.str = source_string
        self._caret_token = caret_token
        self._workspace_dir = workspace_dir
        self._chapter_num = chapter_num
        self._subsection_num = subsection_num
        self._open_dsa_cdn = open_dsa_cdn
        self._figure_counter = figure_counter
        self._iframe_images = list()
        self._figures = list()
        self._inlineav_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n^$\n)?\.\.[ ]inlineav::[ ](?P<name>.*?)[ ]
                (?P<type>.*?)(?P<options>:.*?:[ ].*?\n)+(?=\S|$)(?P<caption>(.*?\n))?(?=\S|$)""",
            flags=re.MULTILINE + re.DOTALL + re.VERBOSE
        )

    def _inlineav(self, matchobj):
        images = {}
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
        script_opt = images.get('scripts', '')
        script_opt = script_opt.split()
        css_opt = images.get('links', '')
        css_opt = css_opt.split()
        self._figure_counter += 1
        caption = self._get_caption(matchobj.group('caption'))

        tag = matchobj.group('tag') if matchobj.group('tag') is not None else False
        if tag:
            self._figures.append(Figure(self._figure_counter, matchobj.group('tag')))

        scripts = ''.join(list(map(lambda x: f'<script type="text/javascript" src="{self._open_dsa_cdn}/{x}">'
                                             f'</script>{caret_token}', script_opt)))
        css_links = ''.join(list(map(lambda x: f'<link rel="stylesheet" type="text/css" '
                                               f'href="{self._open_dsa_cdn}/{x}"/>{caret_token}', css_opt)))
        iframe_name = slugify(name)
        """
        reason for subpath - some dynamic images have relative imports like ../../../SourceCode/target_file
        and it allow load it in correct way from cdn root
        """

        iframe_src = f'{self._open_dsa_cdn}/{JSAV_IFRAME_SUBPATH}{iframe_name}.html'
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
            css_path = self._workspace_dir.joinpath(css_name)
            iframe_height_by_path = self._get_iframe_height_by_path(css_path, image_id)
            if css_path.exists() and iframe_height_by_path:
                return iframe_height_by_path
        return 250

    def _get_iframe_height_by_path(self, css_path, image_id):
        with open(css_path, 'r') as file:
            css_content = file.read().replace('\n', '')
            result = re.match(rf"""#{image_id}(?P<content>.*?)}}""", css_content)
            result_height = self._get_result_height_by_css_height_opt(result) if result is not None else False
            iframe_height = int(result_height.group('height')) if result_height else None
        return iframe_height

    @staticmethod
    def _get_result_height_by_css_height_opt(result):
        css_height_opt = result.group('content')
        return re.match(r""".*{.*height(\s)*:(\s)*(?P<height>\d+)px""", css_height_opt)

    def _get_caption(self, raw_caption):
        counter = f'{self._chapter_num}.{self._subsection_num}.{self._figure_counter}'
        caption = ': '
        if raw_caption:
            caption = raw_caption.replace('\n', ' ')
            caption = re.sub(r'\s+', ' ', caption)
        return f'<center>Figure {counter}{caption}</center><br/>{self._caret_token}{self._caret_token}'

    def _set_figure_links_by_tag(self, output):
        for figure in self._figures:
            output = output.replace(f'Figure :num:`Figure #{figure.tag}`',
                                    f'Figure {self._chapter_num}.{self._subsection_num}.{figure.position}')
        return output

    def convert(self):
        output = self.str
        output = self._inlineav_re.sub(self._inlineav, output)
        output = self._set_figure_links_by_tag(output)
        return output, self._figure_counter, self._iframe_images
