import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(name="redshift_export",
                 version="1.0.0",
                 author="Luiz H Superti",
                 author_email="luiz.superti@alice.com.br",
                 description="A general export project, to import small redshift datasets, make transformations and export to the data science folder",
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
