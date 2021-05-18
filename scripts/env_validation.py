import pathlib

def val_env(dir):
    paths = pathlib.Path(dir)

    for search in ['CellProfiler*/**/cp', '**/CellProfiler.exe']:
        found_files = paths.glob(search)
        for file in found_files:
            if file.exists():
                cp_run = file
                break
    if cp_run.exists() == False:
        raise RuntimeError('Unable to locate Cell profiler binary')
    
    fiji_ops = paths.glob('Fiji*')
    for fpath in fiji_ops:
        if fpath.exists():
            fiji_run = fpath
            break
    if fiji_run.exists() == False:
        raise RuntimeError('Unable to locate Fiji app')

    java_ops = paths.glob('Fiji*/java/**/bin/java')
    for jpath in java_ops:
        if jpath.stem == 'java':
            java_run = jpath
            break
    else:
        raise RuntimeError("Explosion; no Java found")

    try:
        import btrack
    except:
        ("Error; btrack not installed")

    return(cp_run, fiji_run, java_run)

"""
cp, fiji, java = val_env("/Applications")
print(cp, fiji, java)
"""