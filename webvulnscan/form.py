from .compat import urlencode, urljoin
from .utils import add_get_params

from .form_input import FormInput
from .textarea import TextArea


class Form(object):

    def __init__(self, url, document):
        self.document = document
        self.action = urljoin(url, document.attrib.get('action'))
        self.parameters = {}

    @property
    def method(self):
        return self.document.attrib.get('method', 'get').lower()

    def get_inputs(self):
        for input_element in self.get_input_elements():
            yield FormInput(input_element)

        for textarea in self.get_textarea_elements():
            yield TextArea(textarea)

    def get_parameters(self, no_guessing=False):
        for item in self.get_inputs():
            if item.get_type == 'hidden' or not no_guessing:
                value = item.guess_value()
            else:
                value = ''
            yield (item.get_name, value)

    def get_input_elements(self):
        for form_input in self.document.findall('.//input'):
            yield form_input

    def get_textarea_elements(self):
        for textarea in self.document.findall('.//textarea'):
            yield textarea

    def send(self, client, parameters, **kwargs):
        if self.method == "get":
            url = add_get_params(self.action, parameters)
            return client.download_page(url, **kwargs)
        else:
            return client.download_page(self.action, parameters, **kwargs)
