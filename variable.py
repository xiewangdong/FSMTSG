import xml.etree.ElementTree as ET

class VariableSample:
    def __init__(self, element):
        self._id = element.get('id')
        self._code = element.find('code').text.strip()
        self._controllable = element.get('controllable')

    @property
    def id(self):
        return self._id

    @property
    def code(self):
        return self._code

    @property
    def controllable(self):
        return self._controllable == 'true'

def load_variable_samples(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return [VariableSample(x) for x in root.findall('sample')]
