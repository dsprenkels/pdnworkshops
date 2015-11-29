import os
import subprocess

from django.core import management
from django.test import TestCase


class UsageTest(TestCase):
    fixtures = ['usagetest']

    def test_model(self):
        management.call_command('calculate')
        self.assertEqual(md5('model.sol'), b'7b929c43ac77f9242ef70ab5c5a6d154')

    def test_solution(self):
        management.call_command('calculate')
        out = subprocess.check_output(['glpsol', '-m', 'model.sol'])
        self.assertIn('totalprofit.val = 995', str(out))

def md5(filename):
    out = subprocess.check_output(['md5sum', filename])
    return out.split(None, 1)[0]
