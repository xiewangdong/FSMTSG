import xml.etree.ElementTree as ET

class SequenceSample:
    def __init__(self, element):
        self._id = element.get('id')
        self._type = element.get('type')
        self._vulnerability = element.get('vulnerability')
        self._discrimination_group = element.get('discrimination_group')
        self._code = element.find('code').text.strip()

    @property
    def id(self):
        return self._id
    
    @property
    def type(self):
        return self._type

    @property
    def vulnerability(self):
        return self._vulnerability == 'true'
    
    def vulnerable(self):
        return 'vuln' if self._vulnerability == 'true' else 'non-vuln'

    @property
    def discrimination_group(self):
        return self._discrimination_group
    
    def discrimination_group_name(self):
        name = 'disc-' + self.vulnerable()
        if self._discrimination_group == 'CV.VS':
            return name + '-cv-vs'
        elif self._discrimination_group == 'CV.IS.VS':
            return name + '-cv-is-vs'

    @property
    def code(self):
        return self._code
    
    # @code.setter
    # def code(self, value):
    #     self._code = value


def load_sequence_samples(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return [SequenceSample(x) for x in root.findall('sample')]
