SECTION = "section"
CHAPTER = "chapter"


class SectionItem(object):
    def __init__(self, section_name, section_type=SECTION, exercise=False, exercise_path='', line_pos=0):
        self.section_type = section_type
        self.section_name = section_name
        self.exercise = exercise
        self.exercise_path = exercise_path
        self.line_pos = line_pos
        self.lines = []
        self.markdown = None
        self.codio_section = None

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return str({
            'section_name': self.section_name,
            'section_type': self.section_type,
            'exercise': self.exercise,
            'exercise_path': self.exercise_path,
            'line_pos': self.line_pos
        })
