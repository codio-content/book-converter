import yaml
from collections import OrderedDict

from pathlib import Path

from converter.convert import get_toc
from converter.guides.item import CHAPTER


def ordered_dump(data, stream=None, **kwds):
    class OrderedDumper(yaml.SafeDumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def ref_dict(config):
    toc = get_toc(Path(config['workspace']['directory']), Path(config['workspace']['tex']))
    refs = make_refs(toc)

    out = {'refs': {'chapter_counter_from': 0, 'overrides': refs}}

    print(ordered_dump(out, default_flow_style=False))


def get_ref_chapter_counter_from(config):
    ref_section = config.get('refs')
    if not ref_section:
        return 1

    chapter_counter_from = ref_section.get('chapter_counter_from', 1)
    if not isinstance(chapter_counter_from, int):
        return 1

    return chapter_counter_from


def override_refs(refs, config):
    ref_section = config.get('refs')
    if not ref_section:
        return refs

    ref_overriders = ref_section.get('overrides')
    if not ref_overriders:
        return refs

    return {**refs, **ref_overriders}


def make_refs(toc, chapter_counter_from=1):
    refs = OrderedDict()
    chapter_counter = 0
    section_counter = 0
    exercise_counter = 0
    figs_counter = 0
    is_figure = False
    is_exercise = False

    for item in toc:
        if item.section_type == CHAPTER:
            if not chapter_counter:
                chapter_counter = chapter_counter_from
            else:
                chapter_counter += 1
            section_counter = 0
            figs_counter = 0
            exercise_counter = 0
        else:
            section_counter += 1
        for line in item.lines:
            if line.startswith("\\begin{figure}"):
                figs_counter += 1
                is_figure = True
            elif line.startswith("\\end{figure}"):
                is_figure = False
            elif line.startswith("\\begin{exercise}"):
                exercise_counter += 1
                is_exercise = True
            elif line.startswith("\\end{exercise}"):
                is_exercise = False
            elif line.startswith("\\label{"):
                label = line[7:-1]
                refs[label] = {
                    'pageref': item.section_name
                }
                if is_figure:
                    refs[label]["ref"] = '{}.{}'.format(chapter_counter, figs_counter)
                elif is_exercise:
                    refs[label]["ref"] = '{}.{}'.format(chapter_counter, exercise_counter)
                elif item.section_type == CHAPTER:
                    refs[label]["ref"] = '{}'.format(chapter_counter)
                else:
                    refs[label]["ref"] = '{}.{}'.format(chapter_counter, section_counter)

    return refs
