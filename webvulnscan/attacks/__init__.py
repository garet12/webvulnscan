""" This modules provides various attacks and functions to run them. """
from .xss import xss
from .csrf import csrf
from .crlf import crlf
from .breach import breach
from .clickjack import clickjack
from .cookiescan import cookiescan
from .exotic_characters import exotic_characters
from .utf7_check import utf7_check


def all_attacks():
    return [xss, csrf, crlf, breach, clickjack, cookiescan, exotic_characters,utf7_check]
