#!/bin/bash
export PATH="/home/ubuntu/miniconda3/bin:$PATH"
cd ~/OG-USA/regression
source activate ospcdyn
python run_reg_reforms.py --ref_idxs=0,1,2 --use_cps --cpu_count=1 > output.txt
