from ..utils import attack, modify_parameter
import time
import multiprocessing
from ..openID_test import main

OPENID_URL = "http://localhost:8080"
OPENID_URL_BILLION_LAUGHS = "http://localhost:8080/db"
OPENID_URL_QUADRATIC_BLOWUP = "http://localhost:8080/dq"


def search(page):
    for form in page.get_forms():
        yield (form,)


@attack(search)
def billion_laughs(client, log, form):
    parameters = dict(form.get_parameters())
    server = multiprocessing.Process(target=main)
    server.start()
    for parameter in parameters:
        print(parameters)
        print(parameter)
        if parameter == '':
            continue
        if parameters[parameter] == 'abcdefgh':
            xml_page = OPENID_URL_BILLION_LAUGHS
        else:
            xml_page = parameters[parameter]
        attack_parameters = modify_parameter(parameters, parameter,
                                             OPENID_URL)
        startTime = time.time()
        server.join(0.001)
        result = form.send(client, attack_parameters)
        endTime = time.time()
        elapsedTime = endTime - startTime
        attack_parameters = modify_parameter(parameters, parameter,
                                             xml_page)

        p = multiprocessing.Process(
            target=form.send, args=(client, attack_parameters))
        p.start()

        p.join(elapsedTime + 1)
        if p.is_alive():
            log('vuln', result.url, "Billion Laughs",
                "in URL parameter " + parameter)
            p.terminate()
            p.join()

    server.terminate()
    server.join()
