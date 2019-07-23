#!/bin/bash -l
source $HOME/.reporter_bash
cd $prod_lib
# run python
$env_bin/python consume_reporter.py
