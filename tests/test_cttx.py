"""
Text cttx.py
"""

import contextlib
import io
import pathlib
import tempfile
import unittest
import xml.etree.ElementTree as ET

import cttx



class TestCTTX(unittest.TestCase):

    _REPLACE_TESTS = [
        ('trajectory.csv', '.csv', '.xml', 'trajectory.xml', False),
        ('trajectory.csv', '.txt', '.xml', 'trajectory.xml', True),
    ]
    def test_replace_extension(self):
        for fname, expect_ext, new_ext, expected, warns in self._REPLACE_TESTS:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = cttx.replace_extension(fname, expect_ext, new_ext)
            self.assertEqual(expected, result)
            stdout.seek(0)
            wrote_to_stdout = len(stdout.read()) > 0
            self.assertEqual(wrote_to_stdout, warns)


    _TEST_DATA_DIR = pathlib.Path(__file__).parent / 'data'
    _TEST_DATA_ROWS = [
        dict(x=-1, y=1, z=0, end=0),
        dict(x=1, y=-1, z=0, end=0),
        dict(x=1, y=1, z=0, end=0),
        dict(x=-1, y=-1, z=0, end=0),
    ]

    def _dict_values_as_floats(self, d):
        return {k: float(v) for k, v in d.items()}


    def test_read_csv_rows(self):
        """
        Reading the test data 'trajectoria1.csv' file produces
        the rows we expect, with numeric values: self._TEST_DATA_ROWS.
        """
        rows_filename = self._TEST_DATA_DIR / 'trajectoria1.csv'
        # Convert each read dict value (a string) to a float.
        real_rows = [
            self._dict_values_as_floats(row)
            for row in cttx.read_csv_rows(rows_filename)
        ]
        expected_rows = self._TEST_DATA_ROWS
        self.assertEqual(real_rows, expected_rows)

        
    def _assert_xml_file_contents(self, xml_filename):
        """
        Assert that `xml_filename` is an XML file with:
        - A top level <Trajectory> tag.
          With the expected 'name', 'closed', and 'order' attributes.
        - Only <P> child tags.
          Matching the attributes in self._TEST_DATA_ROWS.
        """
        tree = ET.parse(xml_filename)
        root = tree.getroot()

        # Root element is a Trajectory tag.
        self.assertEqual(root.tag, 'Trajectory')
        # Trajectory tag has the expected attributes.
        self.assertEqual(
            root.attrib,
            dict(name='trajectoria1', closed='true', order='0'),
        )

        # All Trajectory child elements are P tags.
        root_child_tags = {child.tag for child in root}
        self.assertEqual(root_child_tags, {'P'})

        # P tags have the expected numeric attributes.
        p_attrs = [
            self._dict_values_as_floats(child.attrib)
            for child in root
        ]
        self.assertEqual(self._TEST_DATA_ROWS, p_attrs)


    def test_xml_test_data(self):
        """
        The test data 'trajectoria1.xml' contains the rows we
        know about, with numeric values.
        """
        xml_filename = self._TEST_DATA_DIR / 'trajectoria1.xml'
        self._assert_xml_file_contents(xml_filename)


    def test_write_xml_rows(self):
        """
        Writing an XML file from our self._TEST_DATA_ROWS produces
        the correct XML document.
        """
        with tempfile.TemporaryDirectory() as temp_dir_name:
            xml_filename = pathlib.Path(temp_dir_name) / 'output.xml'
            cttx.write_xml_rows(self._TEST_DATA_ROWS, xml_filename)
            self._assert_xml_file_contents(xml_filename)

