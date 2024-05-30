import os
import tarfile
import subprocess
import shutil

def extract_tarball(tarball_path, extract_path, max_depth, current_depth=1):
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

    try:
        with tarfile.open(tarball_path, "r:*") as tar:
            safe_extract(tar, extract_path)
            if current_depth < max_depth:
                for member in tar.getmembers():
                    if member.isfile() and member.name.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz')):
                        nested_tar_path = os.path.join(extract_path, member.name)
                        nested_extract_path = os.path.join(extract_path, member.name + "_contents")
                        os.makedirs(nested_extract_path, exist_ok=True)
                        print(f"Extracting nested tarball {nested_tar_path} into {nested_extract_path}")
                        extract_tarball(nested_tar_path, nested_extract_path, max_depth, current_depth + 1)
    except Exception as e:
        print(f"Skipping {tarball_path} due to error: {e}")

def list_contents_in_tree_format(path, output_file):
    try:
        result = subprocess.run(['tree', path], check=True, capture_output=True, text=True)
        with open(output_file, 'w') as file:
            file.write(result.stdout)
        print(f"Tree output saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while listing contents with tree: {e}")

def main(tarball_path, max_depth):
    extract_dir = os.path.splitext(os.path.basename(tarball_path))[0]
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)
    
    try:
        extract_tarball(tarball_path, extract_dir, max_depth)
        
        # Generate the output file name
        output_file = os.path.splitext(tarball_path)[0] + '.txt'
        list_contents_in_tree_format(extract_dir, output_file)
    
    finally:
        # Clean up the extract directory
        shutil.rmtree(extract_dir)
        print(f"Cleaned up directory {extract_dir}")

if __name__ == "__main__":
    tarball_path = "example.tar.gz"  # Replace with your tarball file path
    max_depth = int(input("Enter the maximum depth of nested tarballs to extract: "))
    main(tarball_path, max_depth)
