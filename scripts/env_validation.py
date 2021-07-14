from pathlib import Path

"""
Looks for existence of cell profiler, fiji, Java, and MIST, raising errors if any are missing

cp_dir: directory of cell profiler
fiji_dir: directory of the fiji application
"""
def val_env(cp_dir, fiji_dir):
    cp_path = Path(cp_dir)
    fiji_path = Path(fiji_dir)
    
    if cp_path.exists() == False:
        raise RuntimeError('Unable to locate the Cellprofiler folder')

    cp_run = None
    for search in ['**/cp', '**/CellProfiler.exe', '**/cellprofiler']:
        found_files = cp_path.glob(search)
        for file in found_files:
            if file.exists():
                cp_run = file
                break
    if (cp_run is not None) and (cp_run.exists() == False):
        raise RuntimeError('Unable to locate Cell profiler binary')
    
    if fiji_path.exists() == False:
        raise RuntimeError('Unable to locate Fiji app')

    java_ops = fiji_path.glob('java/**/bin/java*')
    for jpath in java_ops:
        if jpath.stem == 'java' and jpath.suffix in ['', '.exe']:
            java_run = jpath
            break
    else:
        raise RuntimeError("Explosion; no Java found")

    if (fiji_path / 'plugins' / 'MIST_.jar').exists() == False:
        raise RuntimeError('Unable to locate MIST plugin for Fiji. Is it installed?')

    try:
        import btrack
    except:
        ("Error; btrack not installed")

    return(cp_run, fiji_path, java_run)

"""
cp, fiji, java = val_env("/Applications", "/Applications/Fiji.app")
print(cp, fiji, java)
"""
