# CellBaum

## Installation
To create a local environment with every (Python) package you need, run:

```
{conda,mamba} env create -f env.yml -p ./cenv
```
e.g. if you have Conda installed, use:
```
conda env create -f env.yml -p ./cenv
```

You will need to install CellProfiler and Fiji (with the MIST plugin) for CellBaum to work.
Normally, you'll want to do this outside of the environment, as both tools are useful
as GUI tools.

If you need to install CellProfiler within Conda (e.g. on a cluster), you should update the environment
with the CellProfiler addons:

```
{conda,mamba,micromamba} env update --name ./cenv --file cp_addons.yml
```


Afterwards, you can activate the local environment with:
```
{conda,mamba,micromamba} activate ./cenv
```

