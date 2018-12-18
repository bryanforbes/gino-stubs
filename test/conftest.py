import os

os.environ['MYPY_TEST_PREFIX'] = os.path.dirname(os.path.realpath(__file__))
pytest_plugins = ['mypy.test.data']
