from ..utils import attack,modify_parameter

OPENID_URL= "httpl://localhost:8080"

def attack_post(client,log,form):
    parameters = dict(form.get_parameters())
    for parameter in parameters:
        attack_parameters = modify_parameter(parameters, parameter,
                                             OPENID_URL)
        print "test"
        result = form.send(client, attack_parameters)
        log('warn', form.action,
                'HTTP Errors occurs when confronted with html input',
                "in parameter TEST")
def search(page):
    for form in page.get_forms():
        yield form

@attack(search)
def billion_laughs(client, log, forms):
    print forms
    globals()['attack_post'](client, log, forms)
    print "test3"