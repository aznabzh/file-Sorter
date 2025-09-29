# Usage Instructions for File Sorter

## Overview

The **File Sorter** is a Python project designed to automate the organization of files in a specified directory based on configurable rules. It allows users to sort files by their extensions or by patterns in their filenames, making it easier to manage downloads and other files.

## Installation

To get started with the File Sorter, follow these steps:

1. **Clone the repository:**
   ```
   git clone https://github.com/yourusername/file-sorter.git
   cd file-sorter
   ```

2. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Configure the sorting rules:**
   Edit the `config/config.json` file to define your sorting rules.

## Configuration

The configuration file `config/config.json` should contain rules in the following format:

```json
{
  "rules": [
    {
      "extensions": [".mp4"],
      "filename_pattern": "\\d{2}h\\d{2}m\\d{2}s",
      "destination": "VOD"
    },
    {
      "extensions": [".mp4"],
      "destination": "Videos"
    },
    {
      "extensions": [".jpg", ".png"],
      "destination": "Photos"
    }
  ]
}
```

### Rule Explanation

- **extensions**: List of file extensions to match.
- **filename_pattern**: Regular expression pattern to match against the filename.
- **destination**: The folder where matching files will be moved.

## Usage

To run the File Sorter, use the command line interface (CLI). The basic command structure is as follows:

```
python -m file_sorter.cli [options]
```

### Options

- `--directory <path>`: Specify the directory to sort (default is the Downloads folder).
- `--dry-run`: Simulate the sorting process without moving any files.
- `--config <path>`: Specify a custom configuration file (default is `config/config.json`).

### Example Commands

1. **Sort files in the Downloads folder:**
   ```
   python -m file_sorter.cli --directory ~/Downloads
   ```

2. **Run in dry-run mode to see what would happen:**
   ```
   python -m file_sorter.cli --directory ~/Downloads --dry-run
   ```

3. **Use a custom configuration file:**
   ```
   python -m file_sorter.cli --config custom_config.json
   ```

## Logging

The File Sorter logs its operations to the console. For detailed logging, you can modify the logging settings in the code.

## Contribution

If you would like to contribute to the File Sorter project, please fork the repository and submit a pull request. Ensure that your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.