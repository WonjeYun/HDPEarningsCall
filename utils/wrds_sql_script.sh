#!/bin/bash
#$ -cwd
#$ -o wrds_sql_script.out -e wrds_sql_script.err
#$ -pe onenode 1
#$ -l m_mem_free=32G

# this file is used to run the wrds_sql_script.py file in the WRDS Cloud HPC cluster
python3 wrds_sql_script.py