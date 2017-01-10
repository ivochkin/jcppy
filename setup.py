from setuptools import setup

setup(
    name="jcppy",
    setup_requires=["vcversioner"],
    vcversioner={
        'version_module_paths': ['jcppy/_version.py'],
    },
    author="Stanislav Ivochkin",
    author_email="isn@extrn.org",
    description=("C++ code generator for JSON Schema"),
    license="MIT",
    url="https://github.com/ivochkin/jcppy",
    packages=["jcppy"],
    include_package_data=True,
    package_data={"jcppy": ["data/*.c", "data/templates/*"]},
    entry_points={
        "console_scripts": [
            "jcppy= jcppy.cli:main"
        ]
    },
    install_requires=[
        "click>=6.0",
        "Jinja2>=2.7",
    ],
)
