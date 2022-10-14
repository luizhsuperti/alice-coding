from setuptools import setup, find_packages

setup(
    name="toolbelt",
    version="0.0.1",
    install_requires=[],
    packages=find_packages(where=".", ),
    entry_points={
        "console_scripts": [
            "init_project = src_toolbelt.create_project:init_project",
        ]
    },
    include_package_data=True,
)