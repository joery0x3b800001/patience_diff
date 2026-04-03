from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='patience_diff_algo',
    version='1.0.2',
    author='Shaun Joe',
    author_email='shaunjoeroy1234@gmail.com',
    description='Patience Diff Algorithm - An implementation of Bram Cohen\'s diff algorithm',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/joery0x3b800001/patience_diff',
    project_urls={
        'Bug Tracker': 'https://github.com/joery0x3b800001/patience_diff/issues',
        'Source': 'https://github.com/joery0x3b800001/patience_diff',
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    packages=find_packages(),
    python_requires='>=3.7',
    keywords='diff algorithm patience sorting sequence',
    license='GPLv2+',
)