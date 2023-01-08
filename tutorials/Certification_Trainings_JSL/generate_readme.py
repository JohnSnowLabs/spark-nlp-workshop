import glob
import re
from natsort import natsorted

folders = ['Finance', 'Legal']


def create_readme():
    for folder in folders:
        rows = []
        print(f"# {folder} NLP notebooks")
        for f in glob.glob(f"{folder}/*.ipynb"):
            with open(f, 'r', encoding='utf-8') as fr:
                content = fr.read()
                for m in re.finditer(r'\[\!\[Open In Colab\]\(.*\)\]\((.*)\)', content):
                    fileurl = m.group(1)
                    filename = fileurl.split('/')[-1]
                    rows.append(f"[{filename}]({fileurl})")
        print("\n".join(natsorted(rows)))
        print()


if __name__ == "__main__":
    create_readme()
