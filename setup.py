import setuptools

setuptools.setup(
    name="lifealgorithmic",
    version="0.0.2",
    author="Mike Matera",
    author_email="matera@lifealgorithmic.com",
    description="My Course Tools",
    url="http://www.lifealgorithmic.com",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],

    install_requires=[
        'filetype', 
        'selenium', 
        'pexpect', 
        'canvasapi', 
        'python-Levenshtein', 
        'pyyaml', 
        'boto3',
    ],

    packages=[
        'lifealgorithmic', 
        'cis15.tests', 
        'lifealgorithmic.linux',
        'rosters',
    ],
    
    scripts=[
        'cis54/extract_notebooks.py', 
        'cis15/test_subs.py', 
        'cis15/projtest',
        'lifealgorithmic/armor', 
        'lifealgorithmic/decode-cfm',
        'lifealgorithmic/notebook', 
        'lifealgorithmic/aws-roster', 
        'cis15/upload_results.py'
        'rosters/get-rosters',
    ],

)