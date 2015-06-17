import os
import sys
import imp
import os.path
import warnings

import django

def setup_virtual_package(name, path):
    modulePath = os.path.abspath(path)
    f, fn, suffix = imp.find_module('__init__', [modulePath])
    imp.load_module(name, f, fn, suffix)
    sys.modules[name].__path__ = [modulePath]

if __name__ != '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pdn.settings")
    path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(
        os.path.realpath(__file__[:-1] if __file__[-4:] in
            ('.pyc', '.pyo') else __file__))), '../../pdn'))
    setup_virtual_package('pdn', path)
    django.setup()
