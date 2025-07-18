# Directory Scripts

This repository contains various Python scripts for monitoring and managing files in a specified directory. Each script has its own functionality, and this README provides an overview of each one.

## Scripts Overview

| Filename                  | Usage                                                                                          | Syntax                                             |
|---------------------------|------------------------------------------------------------------------------------------------|----------------------------------------------------|
| `dir_change_tracker.py`   | This script monitors a specified directory for changes in files by computing their hashes. It keeps track of the current and previous states of the files in a SQLite database. | `python dir_change_tracker.py <directory_path>`   |
| `secure_zip_creator.py`   | This script creates a password-protected ZIP file of a specified directory, with options to exclude certain files. | `python secure_zip_creator.py <zip_filename> <dir_to_zip> <password> [--exclude <file1> <file2> ...]` |
