import re
from converter.guides.tools import slugify
from string import Template
from collections import namedtuple
from converter.rst.utils import css_property

IframeImage = namedtuple('IframeImage', ['src', 'path', 'content'])
GUIDES_CDN = '//static-assets.codio.com/guides/opendsa/v1'
MATHJAX_CDN = '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1'
JSAV_IFRAME_SUBPATH = 'jsav/iframe/v1/'
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
MATHJAX_IN_AV_CONTAINER_SCRIPT = r"""
<script>
  if (typeof MathJax !== 'undefined') {
      MathJax.Hub.Config({
        tex2jax: {
          inlineMath: [
            ['$', '$'],
            ['\\(', '\\)']
          ],
          displayMath: [
            ['$$', '$$'],
            ["\\[", "\\]"]
          ],
          processEscapes: true
        },
        "HTML-CSS": {
          scale: "80"
        }
      });
      $('.avcontainer').on("jsav-message", function() {
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
      });
      $(".avcontainer").on("jsav-updatecounter", function() {
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
      });
    }
</script>
"""


class InlineAv(object):
    def __init__(self, source_string, caret_token, workspace_dir, open_dsa_cdn):
        self.str = source_string
        self._caret_token = caret_token
        self._workspace_dir = workspace_dir
        self._open_dsa_cdn = open_dsa_cdn
        self._iframe_images = list()
        self._inlineav_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>.*?):\n^$\n)?\.\.[ ]inlineav::[ ]:figure_number:(?P<figure_number>[0-9.]*):[ ]
                (?P<name>.*?)[ ](?P<type>.*?)(?P<options>:.*?:[ ].*?\n)+(?=\S|$)(?P<caption>(.*?\n))?(?=\S|$)""",
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

        figure_number = matchobj.group('figure_number') if matchobj.group('figure_number') is not None else ''
        caption = self._get_caption(matchobj.group('caption'), figure_number)

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
                             f'{scripts}\n' \
                             f'{MATHJAX_IN_AV_CONTAINER_SCRIPT}\n'
        if av_type == 'ss':
            iframe_content = f'{css_links}\n' \
                             f'<div style="margin: 0" id="{name}" class="ssAV avcontainer">\n' \
                             f'<span class="jsavcounter"></span>\n' \
                             f'<a class="jsavsettings" href="#">Settings</a>\n' \
                             f'<div class="jsavcontrols"></div>\n' \
                             f'<p class="jsavoutput jsavline"></p>\n' \
                             f'<div class="jsavcanvas"></div>\n' \
                             f'</div>\n{scripts}\n' \
                             f'{MATHJAX_IN_AV_CONTAINER_SCRIPT}\n'

        iframe_content = re.sub(caret_token, '\n', iframe_content)
        iframe_body = Template(JSAV_IMAGE_IFRAME).substitute(title=name, content=iframe_content, name=name)

        self._iframe_images.append(IframeImage(iframe_src, f'{JSAV_IFRAME_SUBPATH}{iframe_name}.html', iframe_body))

        iframe_height = css_property.get_property_by_css(css_opt, name, 'height', self._workspace_dir)
        iframe_height = 250 if iframe_height is None else iframe_height
        iframe_width = css_property.get_property_by_css(css_opt, name, 'width', self._workspace_dir)
        iframe_width = 900 if iframe_width is None else iframe_width

        return f'{caret_token}<iframe id="{name}_iframe" src="{iframe_src}" ' \
               f'width="{iframe_width}" height="{iframe_height}" scrolling="no" ' \
               f'style="position: relative; top: 0px; border: 0; margin: 0; overflow: hidden;">' \
               f'Your browser does not support iframes.</iframe>{caret_token}' \
               f'<br/>{caret_token}{caption}{caret_token}'

    def _get_caption(self, raw_caption, figure_number):
        caption = ': '
        if raw_caption:
            caption = raw_caption.replace('\n', ' ')
            caption = re.sub(r'\s+', ' ', caption)
        return f'<center>Figure {figure_number}{caption}</center><br/>{self._caret_token}{self._caret_token}'

    def convert(self):
        output = self.str
        output = self._inlineav_re.sub(self._inlineav, output)
        return output, self._iframe_images
