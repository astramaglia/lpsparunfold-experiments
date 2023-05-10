# "curdir" should contain script run.py, file timeout and folder "models" with
# the models to be run.

#!/bin/bash

curdir=`pwd`

rev_master_name=MCRL2_master
rev_master=289ef116e3a917feb126b004001353c21e1f3e01

rev_parunfold_name=MCRL2_parunfold
rev_parunfold=4782e4c85a98b651a92c4eea32b01f0d6e9548a5

echo "Installing mCRL2 master at commit ${rev_master}"
mkdir -p "${curdir}/tools/${rev_master_name}"
cd "${curdir}/tools/${rev_master_name}"
git clone https://github.com/mCRL2org/mCRL2.git src
cd src
git checkout ${rev_master}
cd ..
mkdir build
cd build
cmake ../src -DCMAKE_BUILD_TYPE=Release -DMCRL2_ENABLE_GUI_TOOLS=OFF -DCMAKE_INSTALL_PREFIX="${curdir}/tools/${rev_master_name}/install"
make -j install

cd "${curdir}"

echo "Installing mCRL2 parunfold branch at commit ${rev_parunfold}"
mkdir -p "${curdir}/tools/${rev_parunfold_name}"
cd "${curdir}/tools/${rev_parunfold_name}"
git clone --branch parunfold-case-placement --single-branch https://github.com/mCRL2org/mCRL2.git src
cd src
git checkout ${rev_parunfold}
cd ..
mkdir build
cd build
cmake ../src -DCMAKE_BUILD_TYPE=Release -DMCRL2_ENABLE_GUI_TOOLS=OFF -DCMAKE_INSTALL_PREFIX="${curdir}/tools/${rev_parunfold_name}/install"
make -j install

cd "${curdir}"
