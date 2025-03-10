## SDDFClient

### Simple setup
The easiest way to setup client is to download `installer/SDDFInstaller` file into your machine navigate to the directory containing downloaded file and run the following commands.
```bash
chmod +x SDDFInstaller
./SDDFInstaller
```
After that `sddfactory` script will be available for use. You'll just need to download project specific `config.json` file from website (like in this [page](https://sddfactory.cloud/projects/dftresp)) and run the following command.
```bash
sddfactory config.json
```

### Manual setup
In case of manual setup, first we'll need to clone this repo, then if you are familiar with conda environments, the next thing to do is to setup our environment. We'll skip the installation of anaconda/miniconda/micromamba, and move forward. 

**NOTE**: All commands should be run from repo directory.
```bash
conda env create -f environment.yml
```
Then you'll need to download project specific `config.json` file into repo directory and run the following commands.
```bash
conda activate sddf-client-env
scripts/sddfactory_manual config.json
```

**NOTE**: If you are planning to run this script on remote machines, make sure that your session doesn't expire. Consider using `nohup` or `tmux`.
