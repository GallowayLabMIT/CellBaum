import pandas as pd
import pathlib
from pathlib import Path

"""
Merges 2 cell location csvs 

dir: directory with the csvs
well: well being merged
dpi_first: which dpi type comes first
dpi_second: which dpi type comes second
"""
def merge_dpi(dir, well, dpi_first, dpi_next):
    #gets and reads both csvs
    dpi_a = Path(dir) / dpi_first / (well+"cell_data") / "cell_locationsIdentifyPrimaryObjects.csv"
    dpi_b = Path(dir) / dpi_next / (well+"cell_data") / "cell_locationsIdentifyPrimaryObjects.csv"
    dpi_a = pd.read_csv(dpi_a)
    dpi_b = pd.read_csv(dpi_b)
    #changes time points
    dpi_b['Metadata_time'] = dpi_b['Metadata_time'] + max(dpi_a['Metadata_time'])
    # merges csvs
    final = pd.concat([dpi_a, dpi_b])
    # saves the csvs
    outdir = Path(dir)/('merged'+well+'cell_data')
    if not Path.exists(outdir):
        Path(outdir).mkdir()
    final.to_csv(str(outdir/"cell_locationsIdentifyPrimaryObjects.csv"))
    print("Done")

output = Path("/Users/ConradOakes/CellBaum/output")
well_list = ['XY01', 'XY02', 'XY03', 'XY04']
dpi_a = '2dpi'
dpi_b = '3dpi'
for w in well_list:
    merge_dpi(output, w, dpi_a, dpi_b)
