from django.core.management import call_command
import django
import os
import sys


def run_django():
    sys.path.append('./WebUi')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebUi.settings')
    django.setup()
    call_command('runserver', use_reloader=False)  # use_reloader=False prevent running start function twice

if __name__ == '__main__':
    run_django()
