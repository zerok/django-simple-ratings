#!/usr/bin/env python
import sys
from os.path import dirname, abspath

from django.conf import settings

if len(sys.argv) > 1 and 'postgres' in sys.argv:
    sys.argv.remove('postgres')
    db_engine = 'django.db.backends.postgresql_psycopg2'
    db_name = 'test_main'
else:
    db_engine = 'django.db.backends.sqlite3'
    db_name = ''

if not settings.configured:
    settings.configure(
        DATABASES={
            'default': {
                 'ENGINE': 'django.db.backends.sqlite3',
            }
        },
        DATABASE_ENGINE = db_engine,
        DATABASE_NAME = db_name,
        INSTALLED_APPS = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'ratings',
            'ratings.ratings_tests',
        ],
        ROOT_URLCONF='ratings.ratings_tests.urls',
    )

try:
    from django.test.simple import run_tests
    def runtests(*test_args):
        if not test_args:
            test_args = ['ratings_tests']
        parent = dirname(abspath(__file__))
        sys.path.insert(0, parent)
        failures = run_tests(test_args, verbosity=1, interactive=True)
        sys.exit(failures)

    if __name__ == '__main__':
        runtests(*sys.argv[1:])

except:
    from django.test.utils import get_runner
    def runtests(*test_args):
        if not test_args:
            test_args = ['ratings_tests']
        parent = dirname(abspath(__file__))
        sys.path.insert(0, parent)
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=1, interactive=True)
        failures = test_runner.run_tests(test_args)
        sys.exit(failures)

    if __name__ == '__main__':
        runtests(*sys.argv[1:])
