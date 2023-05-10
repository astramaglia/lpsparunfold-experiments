# lpsparunfold-experiments

Repository containing the examples and scripts for the experiments belonging to the paper "Simplifying process parameters by unfolding algebraic data types"

# Usage

Experiments should be run only if the mCRL2 binaries of the different versions are in the PATH.
Then invoke

```
python run.py [yamlfile]
```
to run the experiments. If a filename is given on the command line, results are put in that file.

# Installation 

To execute the script make sure that PyYAML is installed. The mcrl2 tools can be installed using:

```
./install.sh
```
This install two different versions of mCRL2 which contains different versions of the tool *lpsparunfold*:
- the *original* version is installed from the master branch of the mCRL2 toolset, revision 289ef116e3a917feb126b004001353c21e1f3e01
- the *new* version is installed from the parunfold-case-placement branch of mCRL2 toolset, revision 4782e4c85a98b651a92c4eea32b01f0d6e9548a5 .

# Description
