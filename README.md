# Tools For My Classes

This is a hodgepodge of tools I use to automate classes. 

## Content Directories 

Content is divided into directoires by class and one "generic" directory. 

### cis15 

The modules here are the "projtest" program that students use to run unit tests on their assignments to see if they meet my requirements. There's infrastructure for grading Canvas download bundles and uploading the grader resutls back into Canvas. 

### cis54 

The `extract_notebooks.py` tool converts notebooks in a Canvas ZIP to HTML for easier grading. 

### cis191

Contains Vagrantfiles for the VMs used in CIS-191. The last two midterms and finals are in there too. 

### cis192

Experiments for moving CIS-192 from Cabrillo's VMware infrastructure to Amazon or self-hosted Vagrant. 

### cis194

The AWS CloudFormation Stack that I used for CIS-194 students.

### lifealgorithmic 

Infrastructure that's designed to be used as a Python package. 

`armor.py` - Protects the source of a Python script my making it an executable C program. 
`aws-roster` - Generate Cloud9 accounts from a JSON roster file. 
`canvas.py` - Helpers for working with Canvas ZIP files. 
`decode-cfm` - Decoder for my embedded confirmation numbers. 
`notebook` - Helper for running Jupyter Lab in Cloud9

## Under Construction 

This code is actively developed. 