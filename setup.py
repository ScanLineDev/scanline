from setuptools import setup, find_packages

setup(
    name="reviewme",
    version='1.0',
    packages=find_packages(),
    package_data={
        'ailinter': ['config.yaml'],
    },
    install_requires=[
        'python-dotenv',
    ],
    py_modules=['main'],
    entry_points={
        'console_scripts': ['reviewme=main:main'],
    },
)