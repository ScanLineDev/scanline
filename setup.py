from distutils.core import setup
import setuptools
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='scanline',
    packages=['reviewme'],
    py_modules=["cli"],
    version='0.0.1',
    license='Apache License 2.0',
    description='scanline',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='ScanLine',
    author_email='scanlinedev@gmail.com',
    url='',
    keywords=[],
    setup_requires=['wheel'],
    install_requires=[
        "openai==0.27.2",
        "python-dotenv==1.0.0",
        "PyYAML==6.0.1",
    ],
    entry_points={
        'console_scripts': [
            'reviewme = reviewme:cli',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache License 2.0',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)