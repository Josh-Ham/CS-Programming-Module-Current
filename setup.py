import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="covid-19-dashboard-pkg-jwh220",
    version="0.0.1",
    author="Joshua Hammond",
    author_email="jwh220@exeter.ac.uk",
    description="Covid-19 online dashboard.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Peter-Bread/CS-Programming-Module-Current",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
],
    python_requires='>=3.10',
)