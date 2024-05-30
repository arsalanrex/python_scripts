import os
import tarfile
import subprocess
import tempfile


def extract_tarball(tarball_path, extract_path):
    def is_within_directory(directory, target):
        # Returns True if the target is within the directory
        abs_directory = os.path.abspath(directory)
        abs_target = os.path.abspath(target)
        prefix = os.path.commonprefix([abs_directory, abs_target])
        return prefix == abs_directory

    def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        # Safely extract members from tarball, skipping symbolic links
        for member in tar.getmembers():
            member_path = os.path.join(path, member.name)
            if not is_within_directory(path, member_path):
                raise Exception("Attempted Path Traversal in Tar File")
        tar.extractall(path, members, numeric_owner=numeric_owner)

    with tarfile.open(tarball_path, "r:*") as tar:
        safe_extract(tar, extract_path)
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz')):
                nested_tar_path = os.path.join(extract_path, member.name)
                nested_extract_path = os.path.join(extract_path, member.name + "_contents")
                os.makedirs(nested_extract_path, exist_ok=True)
                print(f"Extracting nested tarball {nested_tar_path} into {nested_extract_path}")
                extract_tarball(nested_tar_path, nested_extract_path)


def list_contents_in_tree_format(path, output_file):
    try:
        result = subprocess.run(['tree', path], check=True, capture_output=True, text=True)
        with open(output_file, 'w') as file:
            file.write(result.stdout)
        print(f"Tree output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while listing contents with tree: {e}")


def main(tarball_path):
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temporary directory at {temp_dir}")
        extract_tarball(tarball_path, temp_dir)
        
        # Generate the output file name
        output_file = os.path.splitext(tarball_path)[0] + '.txt'
        list_contents_in_tree_format(temp_dir, output_file)


if __name__ == "__main__":
    tarball_path = "example.tar.gz"  # Replace with your tarball file path
    main(tarball_path)
