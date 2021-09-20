import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eefpcaTBX-pkg-Ryan-Hamilton",
    version="0.0.1",
    author="Ryan Hamilton",
    author_email="ryangilberthamilton@gmail.com",
    description="Standalone EE FPCA data getter scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)