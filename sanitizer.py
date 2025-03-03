import xml.etree.ElementTree as ET

class SanitizerSample:
    def __init__(self, element):
        self._id = element.get('id')
        self._variable_type = element.get('variable_type')
        self._code = element.find('code').text.strip()

    @property
    def id(self):
        return self._id
    
    @property
    def variable_type(self):
        return self._variable_type

    @property
    def code(self):
        return self._code



def load_sanitizer_samples(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return [SanitizerSample(x) for x in root.findall('sample')]
