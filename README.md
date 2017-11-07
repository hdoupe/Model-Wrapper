Model Wrapper
==============================

This package provides a simple set of scripts for running a model in AWS.
The goal for these scripts is to take care of the tedious and repetitive tasks
of writing the same function to copy data from some GitHub repo to an AWS node,
setting up the environment, and running some script.

These were written with [OG-USA](https://github.com/open-source-economics/OG-USA/)
in mind.

The script `model_wrapper.py` takes arguments over the commandline or as
environment variables.  It copies the specified repo into the current
directory.  This is then zipped, copied to the node, and unzipped.  Next,
`env_setup.sh` is copied to the node and run.  This scipt is intended to
install the necessary packages and perform other miscellaneous environment
setup tasks.  Finally, `run_model.sh` is copied over to the node and run.  

Example:
```
python model_wrapper.py \
    --handle hdoupe \
    --repo OG-USA \
    --branch reg_dev \
    --remote origin \
    --logfile log.out \
    --pem path/to/pemfile.pem \
    --ip NODE_IP_ADDRESS
```
