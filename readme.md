# Blue-Sync

## Overview

Blue-Sync is a Python script designed to manage Bluetooth device information on a Linux system.   
It reads the LTK (Long Term Key) values from a Windows registry file and updates the corresponding Bluetooth device information in the `/var/lib/bluetooth` directory.   
The script ensures that the device directories are correctly named and the `info` files contain the correct LTK values.

## Features

- Parses the Windows registry file to extract LTK values.
- Matches Bluetooth devices based on their MAC addresses.
- Updates the `info` files with the correct LTK values.
- Ensures that device directories are correctly named.

## Requirements

- Python 3.6 or higher
- `regipy` library for parsing Windows registry files
- `sudo` access to read and write files in `/var/lib/bluetooth`

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/blue-sync.git
    cd blue-sync
    ```

2. Install the required dependencies:
    ```bash
   pip install -r requirements.txt
    ```

## Usage

1. Mount the NTFS partition containing the Windows registry file.
 
2. Run the script:
    ```bash
    python blue-sync.py
    ```

### Example

# Mount the NTFS partition
sudo mount /dev/sdb1 /mnt/windows

# Run the script
python blue-sync.py

## Configuration

The script does not require any configuration files. It automatically detects the necessary registry file and Bluetooth device directories.

## File Structure
- `blue-sync.py`: The main script file.
- `requirements.txt`: List of required Python packages.
- `README.md`: This file.

## Functions
| Function Name | Description |
| --- | --- |
| `format_mac_address(mac)` | Formats the MAC address to a colon-separated string. |
| `parse_registry_key_to_dict(key, result)` | Parses the registry key to extract LTK values and stores them in a dictionary. |
| `parse_registry(reg_path)` | Parses the Windows registry file to extract LTK values. |
| `get_device_directory()` | Lists the Bluetooth device directories in `/var/lib/bluetooth`. |
| `read_file_with_sudo(file_path)` | Reads a file using `sudo`. |
| `write_file_with_sudo(file_path, content)` | Writes content to a file using `sudo`. |
| `process_device(device_path, ltk_map)` | Processes each Bluetooth device, updates the `info` file, and renames the device directory if necessary. |
| `list_ntfs_mount_points()` | Lists all mounted NTFS partitions. |

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

1. Fork the repository.
2. Create a new branch: git checkout -b feature/your-feature.
3. Make your changes and commit them: git commit -m 'Add some feature'.
4. Push to the branch: git push origin feature/your-feature.
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

If you have any questions or need further assistance, feel free to contact the maintainer:

- Email: yokeen@163.com
- GitHub: @sink