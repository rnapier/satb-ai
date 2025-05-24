from setuptools import setup, find_packages

setup(
    name="satb-split",
    version="0.1.0",
    description="Split closed-score SATB MuseScore files into separate parts",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "ms3",
    ],
    entry_points={
        "console_scripts": [
            "satb-split=satb_splitter.main:main",
        ],
    },
    author="SATB Splitter",
    author_email="",
    url="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Musicians",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
