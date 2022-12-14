from pathlib import Path
from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, conlist

class TimeIntervalModel(BaseModel):
    min: int
    max: int
class ConfigModel(BaseModel):
    data_dir: Path
    cp_dir: Path
    fiji_dir: Path
    pipe_dir: Path
    output_dir: Path
    log_dir: Path
    cell_config: Path

    folder_merging_needed: bool = False
    folders_to_merge: Optional[List[str]]

    image_regex: str

    focus_finding_needed: bool  = False
    focus_channels: List[str]
    
    pre_stitch_correction_needed: bool  = False

    example_image_name: str
    stitching: Dict[str, int]
    Prefix: List[str]
    Template: int

    minsize: int
    maxsize: int

    Update_method: Union[Literal['EXACT'], Literal['APPROXIMATE']] = "EXACT"
    Max_search_radius: int  
    Volume: Optional[Union[List[List[int]], Literal['auto']]] = 'auto'
    Step_size: int
    CP_Data_Keep: Optional[Union[List[str], Literal['all']]] = 'all'

    time_interval_to_track: Optional[TimeIntervalModel]