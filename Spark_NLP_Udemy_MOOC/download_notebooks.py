import gdown
import pandas as pd
import argparse
import time
import os


def get_gid(url):
    """Get the Google ID of the file.
    """
    url = url.split("?")[0].split("#")[0].replace("/view", "")
    return url.split("/")[-1]


def download_notebooks(destiny_folder=".", quiet=False):
    """Download the file from Google drive/colab.
    """
    df = pd.read_excel("links.xlsx")
    df["ID"] = df.link.apply(get_gid)
    if not quiet:
        print(f"Starting to download {df.shape[0]} notebooks")
    for _, row in df.iterrows():
        annotator = row.annotator.replace("\n", "_")
        gdown.download(id=row.ID, output=os.path.normpath(f"{destiny_folder}/{annotator}.ipynb"), quiet=quiet)
        time.sleep(5.0)
    
    if not quiet:
        print("DONE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', action=argparse.BooleanOptionalAction, help='turn verbosity on, printing download messages for every file')
    parser.add_argument('-o', '--destiny-folder', type=str, default=".", help='Folder to save the notebooks')
    args = parser.parse_args()
    download_notebooks(args.destiny_folder, args.quiet)
