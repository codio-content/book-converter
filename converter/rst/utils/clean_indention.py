import re


def clean_indention(content):
    start_space_len = 0
    cut_content = []
    content = content.lstrip('\n').rstrip()
    content_list = content.split('\n')
    indent_match = re.search(r'^[ \t]*', content_list[0])
    if indent_match:
        start_space_len = len(indent_match.group(0))
    for ind, item in enumerate(content_list):
        offset = 1
        item_space_len = len(re.search(r'^[ \t]*', item).group(0))
        if item_space_len < start_space_len and item_space_len != 0:
            offset = (start_space_len + 1) - item_space_len
        cut_content.append(content_list[ind][start_space_len - offset:])
    return '\n'.join(cut_content)
