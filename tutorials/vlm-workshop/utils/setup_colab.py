"""Colab bootstrap — downloads source files, dependencies, and cached data."""
import os, sys, subprocess, tarfile, urllib.request

# ── S3 URLs ──────────────────────────────────────────────────────────────────
# TODO: replace with public URLs once repo is on GitHub / auxdata bucket
_PRESIGNED = {
    "git_downloads.tar.gz": (
        "https://ckl-emr-bucket.s3.us-east-1.amazonaws.com/vlm-workshop/git_downloads.tar.gz"
        "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        "&X-Amz-Credential=ASIASYFSRA74G7RFHHEG%2F20260317%2Fus-east-1%2Fs3%2Faws4_request"
        "&X-Amz-Date=20260317T210542Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host"
        "&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEC0aCXVzLWVhc3QtMSJIMEYCIQC8kS3LTvJWnNIYwIPKpT2yLWxio0t6T%2B5ohMwvKENYIAIhAKln22NJNdWO6E37TGZsLDZfjSm2e567LG65fI0bQZ%2FeKqQCCPb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQAhoMMTg5MzUyOTcwMjMyIgxmF%2BAgRrQxdXCF1Rwq%2BAGgNrz0tpROA6%2BeY3zjCBGrYv%2B7uPFwQX9eo9Qqimpch56o32GIkusbgvgDfb%2Fwq3OOCKesI%2FLncgP8JJbpc8ElIS9p0HNLfQb2FhhG5wwpK4CEj3ubqbrwXnbzw6NPc6CSssf2yKk9x6WOqwiMxMWqQRa2FbKP6%2Bq4TDTV9YXQXBZPN0P5Zus91vAOJ2f9cXouTMGG%2BEW83NX3ThQhxR7rPnqXcpkkevHPtllk9D0opDLNyNjhvo%2BQ92l8R8N5iYQi8Z2sGWjkAHPJFFSSmR8jIFRkYr7Ql89WySpHXsQntSZuyRkjA9RHUihfy9O0B7nvr%2BOqLGYQXTCa%2FebNBjqcAYHvs9QEUza8j6pjxzs0WvpN6thP1o%2FbpfLyqf4vrQ3v%2Bpl8%2BniRXCImB2szLnfDx77WP8%2F116XQR2dXbcTCYjjYtpt5p3U%2B%2FcPINdlQIoIQs0mf%2BPlActCnTJeDFVtvgNTndXECTBeYksAKGyfiyz6i5ARzFLpUjroEAADSPWqqg1l8KHn1bSJWIPzC%2Fh4NqtLaHXgtfpmi6hdgjQ%3D%3D"
        "&X-Amz-Signature=1043c28e667d3a179d25b726b2f48cbf4540ea6a72455cfc9bd3383a6eddf4b7"
    ),
    "nb1_visual_deid_data.tar.gz": (
        "https://ckl-emr-bucket.s3.us-east-1.amazonaws.com/vlm-workshop/nb1_data.tar.gz"
        "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
        "&X-Amz-Credential=ASIASYFSRA74G7RFHHEG%2F20260317%2Fus-east-1%2Fs3%2Faws4_request"
        "&X-Amz-Date=20260317T210543Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host"
        "&X-Amz-Security-Token=IQoJb3JpZ2luX2VjEC0aCXVzLWVhc3QtMSJIMEYCIQC8kS3LTvJWnNIYwIPKpT2yLWxio0t6T%2B5ohMwvKENYIAIhAKln22NJNdWO6E37TGZsLDZfjSm2e567LG65fI0bQZ%2FeKqQCCPb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQAhoMMTg5MzUyOTcwMjMyIgxmF%2BAgRrQxdXCF1Rwq%2BAGgNrz0tpROA6%2BeY3zjCBGrYv%2B7uPFwQX9eo9Qqimpch56o32GIkusbgvgDfb%2Fwq3OOCKesI%2FLncgP8JJbpc8ElIS9p0HNLfQb2FhhG5wwpK4CEj3ubqbrwXnbzw6NPc6CSssf2yKk9x6WOqwiMxMWqQRa2FbKP6%2Bq4TDTV9YXQXBZPN0P5Zus91vAOJ2f9cXouTMGG%2BEW83NX3ThQhxR7rPnqXcpkkevHPtllk9D0opDLNyNjhvo%2BQ92l8R8N5iYQi8Z2sGWjkAHPJFFSSmR8jIFRkYr7Ql89WySpHXsQntSZuyRkjA9RHUihfy9O0B7nvr%2BOqLGYQXTCa%2FebNBjqcAYHvs9QEUza8j6pjxzs0WvpN6thP1o%2FbpfLyqf4vrQ3v%2Bpl8%2BniRXCImB2szLnfDx77WP8%2F116XQR2dXbcTCYjjYtpt5p3U%2B%2FcPINdlQIoIQs0mf%2BPlActCnTJeDFVtvgNTndXECTBeYksAKGyfiyz6i5ARzFLpUjroEAADSPWqqg1l8KHn1bSJWIPzC%2Fh4NqtLaHXgtfpmi6hdgjQ%3D%3D"
        "&X-Amz-Signature=da8b8528238586cc1dd2ede2800d9591718657196d755be2e6ac95962e4bbe0f"
    ),
}

PACKAGES = [
    "pandas", "numpy", "tqdm", "pillow", "datasets", "matplotlib", "seaborn",
    "scikit-learn", "openai", "python-dotenv", "faiss-cpu", "requests", "PyMuPDF",
]


def _pip(*pkgs):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *pkgs])


def _fetch(url, name):
    print(f"  Downloading {name} ...")
    urllib.request.urlretrieve(url, name)
    with tarfile.open(name) as t:
        t.extractall()
    os.remove(name)


def setup(nb_name: str):
    """Run full Colab setup for a given notebook.

    Args:
        nb_name: e.g. 'nb1_visual_deid', 'nb2_visual_document_mining_and_routing'
    """
    print("Installing Python packages ...")
    _pip(*PACKAGES)

    print("Downloading source files ...")
    _fetch(_PRESIGNED["git_downloads.tar.gz"], "git_downloads.tar.gz")

    data_key = f"{nb_name}_data.tar.gz"
    print(f"Downloading cached predictions + datasets ...")
    _fetch(_PRESIGNED[data_key], data_key)

    print("Setup complete.")
