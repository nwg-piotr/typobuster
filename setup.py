import os

from setuptools import setup, find_packages


def read(f_name):
    return open(os.path.join(os.path.dirname(__file__), f_name)).read()


setup(
    name='typobuster',
    version='0.1.8',
    description='lightweight editor with text transformations and auto-correction',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["langs/*", "icons/dark/*", "icons/light/*"]
    },
    url='https://github.com/nwg-piotr/nwg-shell-config',
    license='GPL3',
    author='Piotr Miller',
    author_email='nwg.piotr@gmail.com',
    python_requires='>=3.5.0',
    install_requires=[],
    entry_points={
        'gui_scripts': [
            'typobuster = typobuster.main:main'
        ]
    }
)
