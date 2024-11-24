import os
import re
import subprocess
import regipy

def format_mac_address(mac):
    return ':'.join(re.findall(r'..', mac.upper()))

def parse_registry_key_to_dict(key, result):
    for subkey in key.iter_subkeys():
        for x in subkey.iter_subkeys():
            ltk_value = next((value.value for value in x.iter_values() if value.name == "LTK"), None)
            if ltk_value is not None:
                formatted_mac = format_mac_address(x.name)
                result[formatted_mac] = ltk_value

def parse_registry(reg_path):
    try:
        hive = regipy.RegistryHive(reg_path)
    except Exception as e:
        print(f"Error opening registry file: {e}")
        return {}

    try:
        key = hive.get_key("\\ControlSet001\\Services\\BTHPORT\\Parameters\\Keys")
    except regipy.exceptions.RegistryKeyNotFoundException:
        print("BTHPORT\\Parameters\\Keys key not found.")
        return {}

    result = {}
    parse_registry_key_to_dict(key, result)
    return result

def get_device_directory():
    result = subprocess.run(['sudo', 'ls', '/var/lib/bluetooth/'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error listing device directory: {result.stderr}")
        return None
    device_dir = result.stdout.strip().split('\n')
    if not device_dir:
        print("No device directory found")
        return None
    return device_dir[0]

def read_file_with_sudo(file_path):
    result = subprocess.run(['sudo', 'cat', file_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error reading file: {file_path}, {result.stderr}")
        return None
    return result.stdout

def write_file_with_sudo(file_path, content):
    with subprocess.Popen(['sudo', 'tee', file_path], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL) as proc:
        proc.communicate(input=content.encode())

def process_device(device_path, ltk_map):
    result = subprocess.run(['sudo', 'ls', device_path], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error listing device directory: {result.stderr}")
        return
    devices = result.stdout.strip().split('\n')

    for device in devices:
        if ':' not in device:
            continue

        info_file = os.path.join(device_path, device, "info")
        content = read_file_with_sudo(info_file)
        if content is None:
            print(f"Info file not found: {info_file}")
            continue

        name_match = re.search(r'^Name=(.*)$', content, re.MULTILINE)
        name = name_match.group(1) if name_match else ""

        if not name:
            print(f"Device Name not found in {info_file}")
            continue

        for mac, ltk in ltk_map.items():
            if device[:8] == mac[:8]:
                updated_content = re.sub(r'^Key=.*$', f'Key={ltk}', content, flags=re.MULTILINE)
                write_file_with_sudo(info_file, updated_content)

                new_device_name = mac
                new_device_path = os.path.join(device_path, new_device_name)
                if device == new_device_name:
                    print(f"Directory {device} already has the correct name, no need to rename.")
                elif os.path.exists(new_device_path):
                    print(f"Directory {new_device_path} already exists, skipping rename.")
                else:
                    subprocess.run(['sudo', 'mv', os.path.join(device_path, device), new_device_path])
                    print(f"Renamed directory from {device} to {new_device_name}")

                break

def main():
    ntfs_mounts = list_ntfs_mount_points()
    if not ntfs_mounts:
        print("No NTFS mount points found.")
        return

    for device, mount_point in ntfs_mounts:
        reg_path = os.path.join(mount_point, "Windows", "System32", "config", "SYSTEM")
        if os.path.exists(reg_path):
            content = parse_registry(reg_path)
            if content:
                print("Parsed content:")
                for mac, ltk in content.items():
                    print(f"{mac} = {ltk}")
            else:
                print("No content to display.")
            break  # Only process the first found SYSTEM file
    else:
        print("No NTFS mount points contain the SYSTEM registry file.")
        return

    device_dir = get_device_directory()
    if not device_dir:
        return

    device_path = os.path.join("/var/lib/bluetooth", device_dir)
    process_device(device_path, content)

def list_ntfs_mount_points():
    result = subprocess.run(['mount'], capture_output=True, text=True)
    ntfs_mount_points = [
        (parts[0], parts[2]) for line in result.stdout.splitlines()
        if len(parts := line.split()) > 2 and parts[4].lower() in ('ntfs', 'ntfs3')
    ]
    return ntfs_mount_points

if __name__ == '__main__':
    main()