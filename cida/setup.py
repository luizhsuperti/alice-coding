import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name="cida",
                 version="0.0.1",
                 author="Luiz H Superti",
                 author_email="luiz.alice@com.br",
                 description="a icd carecost calc",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/pypa/sampleproject",
                 project_urls={
                     "Bug Tracker":
                     "https://github.com/pypa/sampleproject/issues",
                 },
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ])
