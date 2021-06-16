# CellBaum

## Installation
To create a local environment with every (Python) package you need, run:

```
{conda,mamba} env create --prefix ./cenv --file env.yml
```
e.g. if you have Conda installed, use:
```
conda env create --prefix ./cenv --file env.yml
```
This will create a local environment within whatever directory you ran the command. If you'd instead
like to make a (user-global) named environment, you can use the `-n` flag and name the environment
instead of specifying its prefix:
```
{conda,mamba} env create --name cenv_name --file env.yml
```

You will need to install CellProfiler and Fiji (with the MIST plugin) for CellBaum to work.
Normally, you'll want to do this outside of the environment, as both tools are useful
as GUI tools.

If you need to install CellProfiler within Conda (e.g. on a cluster), you should update the environment
with the CellProfiler addons:

```
{conda,mamba} env update --prefix ./cenv --file cp_addons.yml
```
if you are using a named/user-global environment, specify the name instead of the prefix:
```
{conda,mamba} env update --name --file cp_addons.yml
```


Afterwards, you can activate the local environment with:
```
{conda,mamba} activate ./cenv
```
Note that you *must* use a relative or absolute path (e.g. include the `./`), this is how Conda identifies locally installed environments versus named, global environments.

