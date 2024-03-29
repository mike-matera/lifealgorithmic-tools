import setuptools

setuptools.setup(
    name="lifealgorithmic",
    version="0.1.0",
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
        'pyyaml', 
        'jupyter',
        'pynacl',
        'psutil',
    ],

    packages=[
        'lifealgorithmic', 
        'lifealgorithmic.linux',
        'rosters',
    ],
    
    scripts=[
        'lifealgorithmic/extract-notebooks', 
        'lifealgorithmic/secrets.py',
        'rosters/get-rosters',
    ],
)
