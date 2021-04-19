#!/bin/sh
#SBATCH --partition=short
#SBATCH --time=3:00:00
#SBATCH --mem-per-cpu=2G
#SBATCH --job-name=save_timeseries
#SBATCH --output=Job_Logs/%x_%j.out
#SBATCH --error=Job_Logs/%x_%j.err

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1

#SBATCH --array=1-200


cd ${SLURM_SUBMIT_DIR}

python save_timeseries.py