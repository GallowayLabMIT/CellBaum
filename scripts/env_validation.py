from pathlib import Path

def val_env(cp_dir, fiji_dir):
    cp_path = Path(cp_dir)
    fiji_path = Path(fiji_dir)
    
    for search in [str(Path('CellProfiler*/**/cp')), str(Path('**/CellProfiler.exe'))]:
        found_files = cp_path.glob(search)
        for file in found_files:
            if file.exists():
                cp_run = file
                break
    if cp_run.exists() == False:
        raise RuntimeError('Unable to locate Cell profiler binary')
    
    fiji_ops = fiji_path.glob('Fiji.app')
    for fpath in fiji_ops:
        if fpath.exists():
            fiji_run = fpath
            break
    if fiji_run.exists() == False:
        raise RuntimeError('Unable to locate Fiji app')

    java_ops = fiji_path.glob(str(Path('Fiji*/java/**/bin/java*')))
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
cp, fiji, java = val_env("/Applications", "/Applications")
print(cp, fiji, java)
"""