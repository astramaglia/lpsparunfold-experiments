# lpsparunfold-experiments

Repository containing the examples and scripts for the experiments belonging to the paper "Simplifying process parameters by unfolding algebraic data types"

## Usage

Experiments should be run only if the mCRL2 binaries of the different versions are in the PATH.
Then invoke

```
python run.py <outputfile>.yaml
```
to run the experiments. Results are put in the ```.yaml``` file.

## Installation 

To execute the script make sure that PyYAML is installed. The mcrl2 tools can be installed using:

```
./install.sh
```
This install two different versions of mCRL2 which contains different versions of the tool *lpsparunfold*:
- the ```original``` version of lpsparunfold and all the the other tools from the mCRL2 toolset are installed from the master branch of the mCRL2 toolset, revision 289ef116e3a917feb126b004001353c21e1f3e01
- the ```new``` version of lpsparunfold and all the the other tools from the mCRL2 toolset are installed from the parunfold-case-placement branch of mCRL2 toolset, revision 4782e4c85a98b651a92c4eea32b01f0d6e9548a5 .

## Description

In these experiments we ultimately obtain the results of symbolic reachabiliy for the different models experimenting with 4 different workflows.
These workflows are executed for each single model for 10 runs. Then the results of symbolic reachability are compared w.r.t. the sizes and mean times found from the 10 runs.
All the models used for this experiments are contained in folder ```models```.

### Reachability
The code that performs all the steps below is ```run.py```.

As first step for all the different workflows the mCRL2 specification is linearize and an ```.lps``` file is obtained 
``` 
mcrl22lps <case>.mcrl2 <case>.lps
```
In few case we preprocess the obtained ```.lps``` file running ```lpssuminst -sS``` where ```S``` is the sort that needs to be expanded.

Then there are 4 different toolchians that we consider (here is where the four different workflows differ): 

#### 1. Static_only
Static analysis tools are applied to the LPS file:

```lpssuminst -f <case>.lps | lpsconstelm -sft | lpsparelm | lpssumelm > <case>.static_only.lps```
    
where 

```lpssuminst -f``` is used for the instantiation of summation variables of finite sorts,

```lpsconstelm -fst``` eliminates constant,

```lpsparelm``` eliminates redundant variables,

```lpssumelm``` eliminated superfluous summation variables.

#### 2. Original unfolding
First unfolding is performed on the LPS file, with the original version of  ```lpsparunfold``` which applies what we call default case placement and then static analysis tools are applied:

```lpsparunfold -sSORT -nN <case>.lps | [lpsparunfold -sSORT' -nN' |] lpssuminst -f <case>.lps | lpsconstelm -sft | lpsparelm | lpssumelm > <case>.default_master.lps```

where ```N``` is the number of times parameters of sort ```SORT``` need to be unfolded. 

The unfolding can be executed multiple time for different sorts, suggested by ```[lpsparunfold -sSORT' -nN' |]```;

#### 3. New unfolding default case placement

First unfolding is performed on the LPS file, with the new version of ```lpsparunfold``` applying the default case placement and the extension introduced to the technique, and then static analysis tools are applied:

```lpsparunfold -sSORT -nN <case>.lps | [lpsparunfold -sSORT' -nN' |] lpssuminst -f <case>.lps | lpsconstelm -sft | lpsparelm | lpssumelm > <case>.default_parunfold.lps```

here we refer to 2. for the explanation;
     
#### 4. New unfolding alternative case placement
First unfolding is performed on the LPS file, with the new version of ```lpsparunfold``` applying the alternative case placement and the extension introduced to the technique, and then static analysis tools are applied:

```lpsparunfold -a -sSORT -nN <case>.lps | [lpsparunfold -a -sSORT' -nN' |] lpssuminst -f <case>.lps | lpsconstelm -sft | lpsparelm | lpssumelm > <case>.alternative_parunfold.lps```

where ```-a``` indicated the application of the alternative case placement, the rest is as of 2.

#### lpsreach
The final step is that for each and every ```.lps``` (```static_only.lps, default_master.lps, default_parunfold.lps, alternative_parunfold.lps```) obtained symbolic reachability is performed:

```lpsreach --print-exact -m64 --cached --groups=simple <case>.<toolchain_name>.lps```

where ```print-exact``` tells the tool to print exact numbers for the number of states explored instead of scientific notation, ```-m64``` indicates that the memory limit for the tool is 64GB, ```--cached``` uses additional memory to reduce the amount of rewriting required and ```--groups=simple``` is a simple, but often effective, heuristic to merge so-called transition groups, which correspond to the summands of the linear process.

### Unfolding
The sorts ```SORT``` and number of times they are unfolded ```N``` for he different models are as follows:

cylinder: [(```List(State)```, ```4```), (```State```, ```1```)],

fourinarow3-4: [(```Board```, ```3```), (```Row```, ```4```)],

fourinarow3-5: [(```Board```, ```3```), (```Row```, ```5```)],

fourinarow4-3: [(```Board```, ```4```), (```Row```, ```3```)],

fourinarow4-4: [(```Board```, ```4```), (```Row```, ```4```)],

fourinarow4-5: [(```Board```, ```4```), (```Row```, ```5```)],

fourinarow5-3: [(```Board```, ```5```), (```Row```, ```3```)],

fourinarow5-4: [(```Board```, ```5```), (```Row```,  ```4```)],

fourinarow5-5: [(```Board```, ```5```), (```Row```, ```5```)],

onoff: [(```Sys```, ```1```)],

sla7: [(```List(Message)```, ```7```)],

sla10: [(```List(Message)```, ```10```)],

sla13: [(```List(Message)```, ```13```)],

swp2-2: [(```DBuf```, ```2```), (```BBuf```, ```2```)],

swp2-4: [(```DBuf```, ```2```), (```BBuf```, ```2```)],

swp2-6: [(```DBuf```, ```2```), (```BBuf```, ```2```)],

swp2-8: [(```DBuf```, ```2```), (```BBuf```, ```2```)],

swp4-2: [(```DBuf```, ```4```), (```BBuf```, ```4```)],

swp4-4: [(```DBuf```, ```4```), (```BBuf```, ```4```)],

swp4-6: [(```DBuf```, ```4```), (```BBuf```, ```4```)],

swp4-8: [(```DBuf```, ```4```), (```BBuf```, ```4```)],

swp8-2: [(```DBuf```, ```8```), (```BBuf```, ```8```)],

tictactoe3-3: [(```Board```, ```3```), (```Row```, ```3```)],

wms: [(```List(Job)```, ```1```)]

## Table of results

The results can be visualized in a latex table that is automaically generated provided the input file/s (```.yaml```) that must be considered.

To generate the latex table run:

```
python table.py [-s] <inputfile1>.yaml .... <inputfileN>.yaml <outputfile>.txt
```
The script will provide a table with the results of symbolic reachability, for each model and each workflow, in terms of the size and the mean total time stored in the inpufiles (if more than one inputfile is provided, otherwise just the single value). 
The ```-s``` adds to the table the standard deviations of the mean total times, again for each model and each workflow.

