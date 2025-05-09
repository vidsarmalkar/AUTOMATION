import os
import pyzipper
import argparse

def create_password_protected_zip(zip_filename, dir_to_zip, password, exclude_files=None):
    """Create a password-protected ZIP file of an entire directory, excluding specified files."""
    if exclude_files is None:
        exclude_files = []

    with pyzipper.AESZipFile(zip_filename, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zip_file:
        zip_file.setpassword(password.encode('utf-8'))  # Set the password
        
        # Walk through the directory
        for root, _, files in os.walk(dir_to_zip):
            for file in files:
                # Check if the file should be excluded
                if file in exclude_files:
                    continue
                
                # Create the full path to the file
                file_path = os.path.join(root, file)
                # Write the file to the ZIP file, preserving the directory structure
                zip_file.write(file_path, os.path.relpath(file_path, dir_to_zip))

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Create a password-protected ZIP file of a directory.')
    parser.add_argument('zip_filename', type=str, help='Path to the output ZIP file.')
    parser.add_argument('dir_to_zip', type=str, help='Path to the directory to zip.')
    parser.add_argument('password', type=str, help='Password for the ZIP file.')
    parser.add_argument('--exclude', type=str, nargs='*', default=[], 
                        help='List of files to exclude from the ZIP (space-separated).')

    # Parse the arguments
    args = parser.parse_args()

    # Create the password-protected ZIP file
    create_password_protected_zip(args.zip_filename, args.dir_to_zip, args.password, args.exclude)
    print(f"Created {args.zip_filename} with password protection, excluding {args.exclude}.")

if __name__ == "__main__":
    main()
