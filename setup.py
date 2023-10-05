
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
    # Give a short description about your library
    description='scanline',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Kyle Morris',
    author_email='kyle@banana.dev',
    url='',
    keywords=[],
    setup_requires=['wheel'],
    install_requires=[
        "anthropic==0.3.11",
        "openai==0.27.2",
        "python-dotenv==1.0.0",
        "PyYAML==6.0.1",
        "PyYAML==6.0.1",
        "setuptools==68.1.2",
    ],
    entry_points={
        'console_scripts': [
            'reviewme = reviewme:cli',
        ],
    },
    classifiers=[
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)