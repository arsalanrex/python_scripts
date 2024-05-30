import os
import tarfile
import subprocess
import tempfile

def extract_tarball(tarball_path, extract_path):
    with tarfile.open(tarball_path, "r:*") as tar:
        tar.extractall(path=extract_path)
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz')):
                nested_tar_path = os.path.join(extract_path, member.name)
                nested_extract_path = os.path.join(extract_path, member.name + "_contents")
                os.makedirs(nested_extract_path, exist_ok=True)
                print(f"Extracting nested tarball {nested_tar_path} into {nested_extract_path}")
                extract_tarball(nested_tar_path, nested_extract_path)

def list_contents_in_tree_format(path):
    try:
        result = subprocess.run(['tree', path], check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while listing contents with tree: {e}")

def main(tarball_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory at {temp_dir}")
        extract_tarball(tarball_path, temp_dir)
        list_contents_in_tree_format(temp_dir)

if __name__ == "__main__":
    tarball_path = "example.tar.gz"  # Replace with your tarball file path
    main(tarball_path)
