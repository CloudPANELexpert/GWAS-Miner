import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GWAS_Miner",  # Replace with your own username
    version="0.0.1",
    author="Thomas Rowlands",
    author_email="thomas.s.rowlands@gmail.com",
    description="A python package for extracting key information from GWAS publications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Thomas-Rowlands/GWAS-Miner/tree/Dev1",
    packages=setuptools.find_packages(),
    install_requires=[
       "python-dateutil>=2.8.1",
       "jsonschema>=3.2.0",
       "networkx>=2.5",
       "spacy>=3.2.1",
       "en_core_sci_lg @ https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.4.0/en_core_sci_lg-0.4.0.tar.gz",
       "svglib>=1.0.1",
       "reportlab>=3.5.49",
       "PyQt5>=5.15.0",
        "bs4"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
