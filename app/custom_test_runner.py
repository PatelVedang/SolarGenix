import os
import sys
import unittest

import django

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")
django.setup()

# Import test classes
from auth_api.tests import AuthTest
from todos.tests import TodoTest
from users.tests import UserTestCase


def load_suite():
    suite = unittest.TestSuite()

    # Add test classes in custom order
    suite.addTest(unittest.makeSuite(AuthTest))
    suite.addTest(unittest.makeSuite(UserTestCase))
    suite.addTest(unittest.makeSuite(TodoTest))

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(load_suite())

    # Optional: exit with proper code for CI/CD
    sys.exit(not result.wasSuccessful())
