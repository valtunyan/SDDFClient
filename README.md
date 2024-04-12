## EnergyClient

For running we'll first need to setup Conda environment by running
```bash
conda env create -f environment.yml
```

Then we'll need to run energy calculation service on background. Just open a `tmux` terminal for convenience, activate conda environment and start service from root directory of this repo.
```bash
conda activate energy-calc-env
python -m src.Client.run
```
