"""Setup script for python-curses-syntax-highlighting."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="curses-syntax-highlighting",
    version="0.1.0",
    author="Grim",
    description="Syntax highlighting for Python curses applications using Pygments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/grimandgreedy/python_curses_syntax_highlighting",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Editors :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pygments>=2.0.0",
        "wcwidth>=0.2.0",
    ],
    keywords="curses syntax highlighting terminal tui pygments",
)
