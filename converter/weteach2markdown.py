import re


def normalize_output(output, media_directory):
    lines = output.replace('\r', '').split('\n')
    normalized_lines = []
    unit_name = None
    topic_name = None

    for line in lines:
        lower_line = line.lower()
        if 'WeTeach_AP'.lower() in lower_line:
            continue
        if 'All Rights Reserved'.lower() in lower_line:
            continue
        topic_or_unit_found = False
        if not unit_name and 'Unit' in line:
            unit_name = line
            topic_or_unit_found = True
        if not topic_name and 'Topic' in line:
            topic_name = line
            topic_or_unit_found = True
        if topic_or_unit_found:
            continue

        # {width="2.8952384076990376in" height="0.7772451881014873in"}
        line = re.sub(r'{width="(\d)+\.(\d)+in" height="(\d)+\.(\d)+in"\}', '', line)
        line = line.replace(f'{media_directory}/', '')
        line = line.strip('> ')
        if line.startswith('!['):
            close_image_tag = line.find(')')
            if close_image_tag > -1 and len(line) > close_image_tag + 1 and line[close_image_tag + 1].isalpha():
                line = line[close_image_tag + 1:] + '\n' + line[0:close_image_tag + 1]

        normalized_lines.append(line.strip())

    if normalized_lines and normalized_lines[0].startswith('============'):
        normalized_lines.pop(0)

    return unit_name, topic_name, '\n'.join(normalized_lines).strip()
