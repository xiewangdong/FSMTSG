import xml.etree.ElementTree as ET

class DecoratorSample:
    def __init__(self, xml_cond):
        self._id = xml_cond.get("id")
        self._code = xml_cond.find("code").text.strip()
        self._istop = xml_cond.get("isTop")
        self._type = xml_cond.get("type")

    @property
    def id(self):
        """ID of the decorator."""
        return self._id

    @property
    def code(self):
        """Code of the decorator."""
        return self._code
    
    @property
    def istop(self):
        """Whether the decorator is a top-level decorator."""
        return self._istop == "true"
    
    @property
    def type(self):
        """Type of the decorator."""
        return self._type


def load_decorator_samples(file_path):
    """Load all decorator from an XML file."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    return [DecoratorSample(x) for x in root.findall('sample')]

