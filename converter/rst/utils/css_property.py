import re


def get_property_by_css(css_names, element_id, property_name, workspace_dir):
    for css_name in css_names:
        css_path = workspace_dir.joinpath(css_name)
        css_property = \
            _get_css_property_by_path(css_path, element_id, property_name) if css_path.exists() else None
        return css_property


def get_property_by_html(file_name, property_name, workspace_dir):
    html_path = workspace_dir.joinpath(file_name)
    css_property = \
        _get_property_by_html(html_path, property_name) if html_path.exists() else None
    return css_property


def _get_css_property_by_path(css_path, element_id, property_name):
    try:
        with open(css_path, 'r') as file:
            css_content = file.read().replace('\n', '')
            properties = re.search(rf"""#{element_id} *{{(?P<content>.*?)}}""", css_content)
            css_property = re.search(rf"""{property_name}:\s*(?P<property>[^;]*);?""", properties.group('content'))
            css_property = css_property.group('property')
    except BaseException as e:
        css_property = None
    return css_property


def _get_property_by_html(html_path, property_name):
    try:
        with open(html_path, 'r') as file:
            html_content = file.read().replace('\n', '')
            properties = re.search(r"""<body *(?P<content>.*?)>""", html_content)
            css_property \
                = re.search(rf'''data-{property_name} *= *"(?P<property>\d*)"''', properties.group('content'))
            css_property = css_property.group('property')
    except BaseException as e:
        css_property = None
    return css_property
