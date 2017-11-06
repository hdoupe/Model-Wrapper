#!/bin/bash
export PATH="/home/ubuntu/miniconda3/bin:$PATH"
cd ~/OG-USA/regression
source activate ospcdyn
python run_reg_reforms.py --use_cps --cpu_count=4 > output.txt
