import asyncio
import hashlib
import os
import shutil
import tarfile

from app.src.constants import PROP_PATH


def hash_string_sha256(input_string):
    blake2b_hash = hashlib.blake2b(digest_size=5)
    blake2b_hash.update(input_string.encode("utf-8"))
    return f".{blake2b_hash.hexdigest()}"


async def extract_tar(tar_path: str, extract_path: str):
    def extract():
        with tarfile.open(tar_path, "r:*") as tar:
            members = tar.getmembers()
            root_dir = os.path.commonprefix([member.name for member in members])
            for member in tar.getmembers():
                member_path = os.path.relpath(member.name, root_dir)
                member.name = member_path
                tar.extract(member, path=extract_path)

    await asyncio.to_thread(extract)


async def clear_opt():
    if os.path.isdir(PROP_PATH):
        await asyncio.to_thread(shutil.rmtree, PROP_PATH)


def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.isfile(filepath):
                total_size += os.path.getsize(filepath)
    return total_size


def get_target_paths(llm_name):
    rfname = hash_string_sha256(llm_name)
    extract_path = os.path.join(PROP_PATH, rfname)
    tar_file_path = f"{extract_path}/{rfname}"
    return extract_path, tar_file_path
