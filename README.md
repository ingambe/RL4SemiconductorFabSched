# Semiconductor Fab Scheduling with Self-Supervised and Reinforcement Learning

This repository contains the code for the paper "Semiconductor Fab Scheduling with Self-Supervised and Reinforcement Learning".

Please follow the instruction to reproduce the results of the paper.

## Installation

**This package has been tested only with Python 3.9**.  
The primary OS target is Ubuntu, but MacOS works too. We never tested this approach on Windows and cannot provide support for this OS.  
Certain dependencies might not work if you use another version of Python.  
We also used Conda has package manager.  
You will also need to create a free account on [Weights & Biases](https://wandb.ai), this will be used to log the results.

### Conda environment

```bash
conda create --name <env> --file requirements.txt
```

Replace `<env>` with the name of your new environment.
Then activate your environment

```bash
conda activate <env>
```

## Reproduce

You first have to go to the directory containing the methods:

```bash
cd simulation/es
```

### Static dispatching

If you want to run the static dispatching rules you have to run the `parallel_dispatch_greedy.py` file.  
You can change the dispatching strategy used by swapping line 25 with another function from the `Dispatchers` class.

```bash
python parallel_dispatch_greedy.py --dataset <HVLM or LVHM> --days 365
```

### Reinforcement learning dispatcher

If you want to run the reinforcement learning dispatcher you have to run the `parallel_greedy_es.py` file.  
The pre-trained weights are already present in the folder.

```bash
python parallel_greedy_es.py --dataset <HVLM or LVHM> --days 365
```

## Training
Although pre-train weights are already present, if you want to train from scratch you can do so.  
The code to train the agent is located in the Python file `train_es.py`

```bash
python train_es.py --dataset <HVLM or LVHM> --days 180 --sigma 0.005 --alpha 0.01 --popsize 128 --l2 0.0
```

Training can take multiple days, but in the end, you will get a Pytorch pre-trained.pt` file containing the weights of the pre-trained network.
You then have to rename it `pretrained_HVLM.pt` or `pretrained_LVHM.pt` to replace the original pre-train files.

## Cite Us

You found our work interesting and useful? Please, don't forget to cite us

```bibtex
@misc{tassel2023semiconductor,
      title={Semiconductor Fab Scheduling with Self-Supervised and Reinforcement Learning}, 
      author={Pierre Tassel and Benjamin Kovács and Martin Gebser and Konstantin Schekotihin and Patrick Stöckermann and Georg Seidel},
      year={2023},
      eprint={2302.07162},
      archivePrefix={arXiv},
      primaryClass={cs.AI}
}
```