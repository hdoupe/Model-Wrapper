#!/bin/bash
export PATH="/home/ubuntu/miniconda3/bin:$PATH"
conda config --set always_yes true
cd ~/OG-USA
source deactivate
if conda env list | grep ospcdyn
then
    echo env ospcdyn is already installed
    echo removing...
    conda env remove --name ospcdyn
    conda env create
else
    echo env is not installed
    echo creating...
    conda env create
fi
source activate ospcdyn
python setup.py develop
echo done...
