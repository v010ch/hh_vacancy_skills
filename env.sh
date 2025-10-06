#!/bin/bash

source activate base

conda activate hh_vacancy
pip install -r requirements.txt
conda deactivate
