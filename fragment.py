import xml.etree.ElementTree as ET

class FragmentSample:
    def __init__(self, element):
        self._id = element.get('id')
        self._code = element.find('code').text.strip()
        self._type = element.get('type')

    @property
    def id(self):
        return self._id
    
    @property
    def code(self):
        return self._code
    
    @property
    def type(self):
        return self._type

def load_fragment_samples(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return [FragmentSample(x) for x in root.findall('sample')]
