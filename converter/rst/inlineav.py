import re
import os
from converter.guides.tools import slugify
from string import Template
from collections import namedtuple
from converter.rst.utils import css_property

IframeImage = namedtuple('IframeImage', ['src', 'path', 'content'])
GUIDES_CDN = '//static-assets.codio.com/guides/opendsa/v1'
MATHJAX_CDN = '//cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1'
JSAV_IFRAME_SUBPATH = 'jsav/iframe/v1/'


def read_template(relative_path):
    current_dirname = os.path.dirname(__file__)
    with open(os.path.join(current_dirname, relative_path)) as file:
        return file.read()


jsav_image_iframe = read_template('templates/iframe_image_tpl.html')
mathjax_in_av_container_script = read_template('templates/mathjax_in_av_container_script_tpl.js')


class InlineAv(object):
    def __init__(self, source_string, caret_token, workspace_dir, open_dsa_cdn):
        self.str = source_string
        self._caret_token = caret_token
        self._workspace_dir = workspace_dir
        self._open_dsa_cdn = open_dsa_cdn
        self._iframe_images = list()
        self._inlineav_re = re.compile(
            r"""(\.\.[ ]_(?P<tag>[^\n]+):\n^$\n)?\.\.[ ]inlineav::[ ]:figure_number:(?P<figure_number>[0-9.]*):[ ]
            (?P<name>[^\n]+)[ ](?P<type>[^\n]+)\n(?P<options>.*?)\n(\n {3}(?P<caption>.*?)(?!\n)\n)?
            (?=\S|(?![^$]+$))""", flags=re.MULTILINE + re.DOTALL + re.VERBOSE)

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
                             f'{mathjax_in_av_container_script}\n'
        if av_type == 'ss':
            iframe_content = f'{css_links}\n' \
                             f'<div style="margin: 0" id="{name}" class="ssAV avcontainer">\n' \
                             f'<span class="jsavcounter"></span>\n' \
                             f'<a class="jsavsettings" href="#">Settings</a>\n' \
                             f'<div class="jsavcontrols"></div>\n' \
                             f'<p class="jsavoutput jsavline"></p>\n' \
                             f'<div class="jsavcanvas"></div>\n' \
                             f'</div>\n{scripts}\n' \
                             f'{mathjax_in_av_container_script}\n'

        iframe_content = re.sub(caret_token, '\n', iframe_content)
        dict_for_iframe_body = dict(title=name,
                                    content=iframe_content,
                                    name=name,
                                    guides_cdn=GUIDES_CDN,
                                    mathjax_cdn=MATHJAX_CDN)
        iframe_body = Template(jsav_image_iframe).substitute(dict_for_iframe_body)

        self._iframe_images.append(IframeImage(iframe_src, f'{JSAV_IFRAME_SUBPATH}{iframe_name}.html', iframe_body))

        iframe_height = css_property.get_property_by_css(css_opt, name, 'height', self._workspace_dir)
        iframe_height = 250 if iframe_height is None else re.sub(r'\d+', self._increase_size, iframe_height)
        iframe_width = css_property.get_property_by_css(css_opt, name, 'width', self._workspace_dir)
        iframe_width = 950 if iframe_width is None else re.sub(r'\d+', self._increase_size, iframe_width)

        return f'{caret_token}<iframe id="{name}_iframe" src="{iframe_src}" ' \
               f'width="{iframe_width}" height="{iframe_height}" scrolling="yes" ' \
               f'style="position: relative; top: 0px; border: 0; margin: 0; overflow: hidden;">' \
               f'Your browser does not support iframes.</iframe>{caret_token}' \
               f'<br/>{caret_token}{caption}{caret_token}'

    def _get_caption(self, raw_caption, figure_number):
        if not raw_caption:
            return ''
        caption = raw_caption.strip().replace('\n', ' ')
        caption = re.sub(r'\s+', ' ', caption)
        return f'<center>Figure {figure_number}: {caption}</center><br/>{self._caret_token}{self._caret_token}'


    @staticmethod
    def _increase_size(match_obj):
        return str(int(match_obj.group(0)) + 50)

    def convert(self):
        output = self.str
        output = self._inlineav_re.sub(self._inlineav, output)
        return output, self._iframe_images
