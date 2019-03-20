import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = "object_tool.tests.settings"
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["object_tool"])
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
