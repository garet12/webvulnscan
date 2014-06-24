from ..utils import attack, modify_parameter

OPENID_URL = "http://localhost:8080"


def search(page):
    for form in page.get_forms():
        yield (form,)


@attack(search)
def billion_laughs(client, log, form):
    parameters = dict(form.get_parameters())
    for parameter in parameters:
        attack_parameters = modify_parameter(parameters, parameter,
                                             OPENID_URL)
        result = form.send(client, attack_parameters)
