from PIL import Image
from pathlib import Path
import os

def grayscale_folder(image_dir:Path, outputfold:Path)->None:
    """
    Takes a folder of images, converts them to grayscale, 
    and then creates a new folder with these images
    Parameters
    ----------
    image_dir: Path
        The path to the images that are being analyzed
    outputfold: Path
        The path to the output folder for the images found by this analysis
    log_filename: Path
        The path to the logfile being generated
    Returns 
    -------
    """
    image_dir = Path(image_dir)
    outputfold = Path(outputfold)
    # for each time point stored in the folder
    for time in sorted(next(os.walk(image_dir))[1]):
        Path.mkdir(outputfold/time, parents = True, exist_ok=True)
        for im_name in Path(image_dir/time).glob("*.tif"):
            im = Image.open(im_name).convert("L")
            im.save(str(outputfold/time/im_name.name))
""""
output = Path("/Users/ConradOakes/CellBaum/testgray/XY01")
bigfolder = Path("/Users/ConradOakes/CellBaum/testing/XY01")
grayscale_folder(bigfolder, output)
"""