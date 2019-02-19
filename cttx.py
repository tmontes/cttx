"""
cttx: CSV Trajectory to XML conversion script.
"""

import csv
import os
import sys



CSV_DELIMITER = ','

XML_TEMPLATE = {
    'head': [
        '<?xml version="1.0" encoding="UTF-8"?>\n',
        '<Trajectory name="trajectoria1" closed="true" order="0">\n',
    ],
    'row': '    <P {attrs} />\n',
    'tail': [
        '</Trajectory>\n'
    ],
}



def replace_extension(filename, expected_ext, new_ext):
    """
    Returns `filename` with its extension replaced with `new_ext`.
    Prints a warning to stdout if the `filename`'s extension is not
    `expected_ext`, in a case-insensitive comparison.
    """
    basename, extension = os.path.splitext(filename)
    if extension.lower() != expected_ext.lower():
        print(f'Warning: {filename} does not have a {expected_ext} extension.')
    return basename + new_ext



def read_csv_rows(csv_filename, csv_delimiter=CSV_DELIMITER):
    """
    Produces one dict per row in the CSV file named `csv_filename`,
    with columns separated by `csv_delimiter`. Each such dict will have
    keys per the first header row in the CSV file, and values per the
    respective CSV file row.
    """
    with open(csv_filename, mode='rt', encoding='latin1') as f:
        yield from csv.DictReader(f, delimiter=csv_delimiter)



def write_xml_rows(rows, xml_filename, xml_template=XML_TEMPLATE):
    """
    Writes `rows`, an iterable of dicts, to an XML document in a file
    named `xml_filename`. The document will be created with:
    - All the lines in `xml_template['head']` which should be a list of lines.
    - One line of `xml_template['row']` per each item of `rows`.
    - All the lines in `xml_template['tail']` which should be a list of lines.
    The xml_template['`row`] argument should be a str template with a single
    `{attrs}` field which will be replaced with the key/value pairs from each
    row's dict.
    """
    xml_head = xml_template['head']
    xml_row_template = xml_template['row']
    xml_tail = xml_template['tail']

    with open(xml_filename, mode='xt', encoding='UTF-8') as f:
        f.writelines(xml_head)
        for row in rows:
            xml_attr_str = ' '.join(
                f'{key}="{value}"' for key, value in row.items()
            )
            f.write(xml_row_template.format(attrs=xml_attr_str))
        f.writelines(xml_tail)



if __name__ == '__main__':

    if len(sys.argv) != 2:
        sys.exit("Need a single command line argument: trajectory CSV file.")

    csv_filename = sys.argv[1]
    xml_filename = replace_extension(csv_filename, '.csv', '.xml')

    try:
        rows = read_csv_rows(csv_filename)
        write_xml_rows(rows, xml_filename)
    except IOError as exc:
        sys.exit(f'CSV/XML file error: {exc}')
    else:
        print(f'XML file created: {xml_filename}')

