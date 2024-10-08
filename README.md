## SDDFClient

### Simple setup
The easiest way to setup client is to download `dpkg/sddfclient.deb` file into your machine and run the following command.
```bash
sudo dpkg -i sddfclient.deb
```
After that `sddfactory` script will be available for use under root user. You'll just need to download project specific `config.json` file from website and run the following command.
```bash
sudo sddfactory config.json
```

### Manual setup
In case of manual setup, first we'll need to clone this repo, then if you are familiar with conda environments, the next thing to do is to setup our environment. We'll skip the installation of anaconda/miniconda/micromamba, and move forward.
```bash
conda env create -f environment.yml
```
Then you'll need to download project specific `config.json` file from website change working directory into the repo directory and run the following command.
```bash
scripts/sddfactory_manual config.json
```
