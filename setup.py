from distutils.core import setup
import os

name = 'gino-stubs'
description = 'Experimental Gino stubs'


def find_stub_files():
    result = []
    for root, _, files in os.walk(name):
        for file in files:
            if file.endswith('.pyi'):
                if os.path.sep in root:
                    sub_root = root.split(os.path.sep, 1)[-1]
                    file = os.path.join(sub_root, file)
                result.append(file)
    return result


setup(
    name='gino-stubs',
    version='0.1',
    description=description,
    long_description=description,
    author='Bryan Forbes',
    author_email='bryan@reigndropsfall.net',
    license='BSD 3-Clause License',
    py_modules=[],
    install_requires=['typing-extensions>=3.6.5'],
    packages=['gino-stubs'],
    package_data={'gino-stubs': find_stub_files()},
)
