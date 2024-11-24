import regipy
import subprocess
import os
import re

def format_mac_address(mac):
    return ':'.join(re.findall(r'..', mac.upper()))

def parse_registry_key_to_dict(key, result):
    for subkey in key.iter_subkeys():
        for x in subkey.iter_subkeys():
            ltk_value = next((value.value for value in x.iter_values() if value.name == "LTK"), None)
            if ltk_value is not None:
                formatted_mac = format_mac_address(x.name)
                result[formatted_mac] = ltk_value
            else:
                print(f"Subkey {x.name} does not have an LTK value.")

def parse_registry(reg_path):
    try:
        hive = regipy.RegistryHive(reg_path)
        print(f"Registry file opened successfully: {reg_path}")
    except Exception as e:
        print(f"Error opening registry file: {e}")
        return {}

    try:
        key = hive.get_key("\\ControlSet001\\Services\\BTHPORT\\Parameters\\Keys")
        print("BTHPORT\\Parameters\\Keys key found.")
    except regipy.exceptions.RegistryKeyNotFoundException:
        print("BTHPORT\\Parameters\\Keys key not found.")
        return {}

    result = {}
    parse_registry_key_to_dict(key, result)
    return result

def list_ntfs_mount_points():
    result = subprocess.run(['mount'], capture_output=True, text=True)
    ntfs_mount_points = [
        (parts[0], parts[2]) for line in result.stdout.splitlines()
        if len(parts := line.split()) > 2 and parts[4].lower() in ('ntfs', 'ntfs3')
    ]
    return ntfs_mount_points

def main():
    ntfs_mounts = list_ntfs_mount_points()
    if not ntfs_mounts:
        print("No NTFS mount points found.")
        return

    print("Found the following NTFS mount points:")
    for device, mount_point in ntfs_mounts:
        print(f"Device: {device}, Mount Point: {mount_point}")

    for device, mount_point in ntfs_mounts:
        reg_path = os.path.join(mount_point, "Windows", "System32", "config", "SYSTEM")
        if os.path.exists(reg_path):
            print(f"Found SYSTEM registry file at: {reg_path}")
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

if __name__ == '__main__':
    main()