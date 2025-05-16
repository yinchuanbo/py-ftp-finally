# FTP File Upload Tool

This is a simplified FTP file upload tool for retrieving changed files from local Git repositories and uploading them to remote servers.

## Features

- Support for multi-language environment configuration
- Automatic identification of Git commit file changes
- Support for specific commit IDs or recent commits
- Automatic verification of file size and content after upload
- Progress bar displaying upload status
- Simplified batch script execution

## Requirements

- Python 3.6+
- Git command line tool

## Installation

1. Install the necessary Python dependencies:

```bash
pip install -r requirements.txt
```

## Usage

This tool provides two main functions:

1. Getting a list of files changed in Git commits
2. Uploading changed files to a remote server

### Configuration Files

- `.env.test`: Test environment configuration
- `.env.pro`: Production environment configuration

Configuration files contain the following parameters:

- `onlyLan`: Specify languages to process (comma-separated)
- `isFilter`: Whether to filter duplicate items
- `*commit`: Specify commit IDs for a language (e.g., `twcommit=f9cd5ca5,990533b3`)

### Command Line Usage

```bash
# Get file list for test environment
python ftp_manager.py get test

# Get file list for production environment
python ftp_manager.py get pro

# Upload files to test environment
python ftp_manager.py upload test

# Upload files to production environment
python ftp_manager.py upload pro
```

### Batch Script

Use the provided batch script for easier operation:

```bash
# Run the menu-driven interface
ftp_manager.bat
```

## Notes

1. Ensure Git repository paths are configured correctly
2. Confirm the list of changed files before uploading
3. If upload fails, check error messages and retry
