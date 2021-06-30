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
        'jupyter',
        'pynacl',
    ],

    packages=[
        'lifealgorithmic', 
        'lifealgorithmic.linux',
        'rosters',
    ],
    
    scripts=[
        'lifealgorithmic/extract-notebooks', 
        'lifealgorithmic/armor', 
        'lifealgorithmic/decode-cfm',
        'rosters/get-rosters',
    ],
)
