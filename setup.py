from setuptools import setup

setup(
    name="reviewme",
    version='1.0',
    py_modules=['reviewme'],
    entry_points={
        'console_scripts': ['reviewme=reviewme:main'],
    },
)