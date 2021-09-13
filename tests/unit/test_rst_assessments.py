import unittest
from unittest.mock import patch

from pathlib import Path

from converter.rst.model.assessment_data import AssessmentData
from converter.convert import convert_assessment, write_assessments


class TestSuite(unittest.TestCase):
    def test_convert_custom(self):
        assessment1 = AssessmentData('id1', 'name1', 'custom', 1, {'question': 'Resolve the challenge above'})
        assessment2 = AssessmentData('id2', 'name2', 'custom', 1, {'question': 'Resolve the challenge above'})
        converted1 = convert_assessment(assessment1)
        self.assertEqual(converted1['type'], 'custom')
        self.assertEqual(converted1['taskId'], assessment1.id)
        self.assertEqual(converted1['source']['name'], assessment1.name)
        self.assertEqual(converted1['source']['instructions'], assessment1.options['question'])

        converted2 = convert_assessment(assessment2)
        self.assertEqual(converted2['type'], 'custom')
        self.assertEqual(converted2['taskId'], assessment2.id)
        self.assertEqual(converted2['source']['name'], assessment2.name)
        self.assertEqual(converted2['source']['instructions'], assessment2.options['question'])

    @patch('converter.convert.write_json')
    def test_convert_unique(self, write_json_mock):
        assessment1 = AssessmentData('id1', 'name1', 'custom', 1, {'question': 'Resolve the challenge above'})
        assessment2 = AssessmentData('id2', 'name2', 'custom', 1, {'question': 'Resolve the challenge above'})
        assessment2d = AssessmentData('id2', 'name2', 'custom', 1, {'question': 'Resolve the challenge above'})
        a_list = [assessment1, assessment2, assessment2d]
        write_assessments(Path('test'), a_list)

        assert write_json_mock.called
        write_path = str(write_json_mock.call_args[0][0])
        self.assertEqual(write_path, 'test/assessments.json')
        write_list = write_json_mock.call_args[0][1]

        self.assertEqual(len(write_list), 2)

        converted1 = write_list[0]

        self.assertEqual(converted1['type'], 'custom')
        self.assertEqual(converted1['taskId'], assessment1.id)
        self.assertEqual(converted1['source']['name'], assessment1.name)
        self.assertEqual(converted1['source']['instructions'], assessment1.options['question'])
