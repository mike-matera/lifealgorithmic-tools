import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lifealgorithmic",
    version="0.0.1",
    author="Mike Matera",
    author_email="matera@lifealgorithmic.com",
    description="My Course Tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.lifealgorithmic.com",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        'filetype', 'selenium', 'pexpect', 'canvasapi', 'python-Levenshtein', 'pyyaml', 'boto3'
    ],
    packages=['lifealgorithmic', 'cis15.tests', 'lifealgorithmic.linux'],
    scripts=['cis54/extract_notebooks.py', 'cis15/test_subs.py', 'cis15/projtest','lifealgorithmic/armor', 'lifealgorithmic/decode-cfm',
             'lifealgorithmic/notebook', 'lifealgorithmic/aws-roster', 'cis15/upload_results.py'],

)