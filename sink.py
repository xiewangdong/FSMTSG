import xml.etree.ElementTree as ET


class SinkSample:
    def __init__(self, element):
        self._id = element.get("id")
        self._type = element.get("type")
        self._valid = element.get("valid")
        self._variable_type = element.get("variable_type")
        self._sanitizers = [SanitizerOfSink(x) for x in element.findall("sanitizer")]
        self._code = element.find("code").text.strip()

    @property
    def code(self):
        return self._code

    @property
    def sanitizers(self):
        return self._sanitizers

    @property
    def id(self):
        return self._id

    @property
    def type(self):
        return self._type

    @property
    def valid(self):
        return self._valid == "true"

    @property
    def variable_type(self):
        return self._variable_type

    @property
    def sufficient_sanitizers_count(self):
        return len([x for x in self._sanitizers if x.sufficient])

    @property
    def insufficient_sanitizers_count(self):
        return len([x for x in self._sanitizers if not x.sufficient])


class SanitizerOfSink:
    def __init__(self, element):
        self._sufficient = element.get("sufficient")
        self._code = element.text.strip()
        self._embedded = element.get("embedded")
        self._id = element.get("id")

    @property
    def code(self):
        return self._code

    @property
    def sufficient(self):
        return self._sufficient == "true"

    @property
    def embedded(self):
        return self._embedded

    @property
    def id(self):
        return self._id


def load_sink_samples(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return [SinkSample(x) for x in root.findall("sample")]
