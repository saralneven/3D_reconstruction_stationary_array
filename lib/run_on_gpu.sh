#!/bin/sh
module load 2021
module load PyTorch/1.10.0-foss-2021a-CUDA-11.3.1
module load TensorFlow/2.6.0-foss-2021a-CUDA-11.3.1
module load CUDA/11.3.1  
module load torchvision/0.11.1-foss-2021a-CUDA-11.3.1

#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --gpus=1
#SBATCH --partition=gpu_shared
#SBATCH --time=01:00:00
srun python3 $HOME/ML_jackdetect/fish_detector.py
