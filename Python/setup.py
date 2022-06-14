from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = [x.rstrip() for x in f]

setup(
    name="mlt",
    version="0.0.1",
    description="Test mykrobe species/lineage calls",
    packages=find_packages(),
    author="Martin Hunt",
    author_email="mhunt@ebi.ac.uk",
    url="https://github.com/Mykrobe-tools/mykrobe-lineage-test",
    entry_points={"console_scripts": ["mlt = mlt.__main__:main"]},
    install_requires=install_requires,
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
    ],
)
