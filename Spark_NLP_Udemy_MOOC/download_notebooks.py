import gdown
import pandas as pd
import argparse
import time


def get_gid(url):
    """Get the Google ID of the file.
    """
    url = url.split("?")[0].split("#")[0].replace("/view", "")
    return url.split("/")[-1]


def download_notebooks(quiet=False):
    """Download the file from Google drive/colab.
    """
    df = pd.read_excel("links.xlsx")
    df["ID"] = df.link.apply(get_gid)
    print(f"Starting to download {df.shape[0]} notebooks")
    for i, row in df.iterrows():
        annotator = row.annotator.replace("\n", "_")
        gdown.download(id=row.ID, output=f"{annotator}.ipynb", quiet=quiet)
        time.sleep(1.0)
    print("DONE")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--quiet', action=argparse.BooleanOptionalAction, help='turn verbosity on, printing download messages for every file')
    args = parser.parse_args()
    download_notebooks(args.quiet)
