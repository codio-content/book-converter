SECTION = "section"
CHAPTER = "chapter"


class SectionItem(object):
    def __init__(self, section_name, section_type=SECTION, line_pos=0):
        self.section_type = section_type
        self.section_name = section_name
        self.line_pos = line_pos
        self.lines = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str({
            'section_name': self.section_name,
            'section_type': self.section_type,
            'line_pos': self.line_pos
        })
