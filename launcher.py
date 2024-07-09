import json
import os
import platform
import requests
import subprocess
import tkinter as tk
from io import BytesIO
from PIL import Image, ImageTk
from datetime import datetime


def download_file(url, dest_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(dest_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {url} => {dest_path}")
        log_action(f"Downloaded: {url} => {dest_path}")
    else:
        print(f"Failed to download file from {url}.")


def install_java():
    system = platform.system()
    java_download_url = ""
    java_installer_path = ""

    if system == "Windows":
        java_download_url = "https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe"
        java_installer_path = os.path.join(os.getenv('TEMP'), 'jdk-17_windows-x64_bin.exe')
    elif system == "Darwin":
        java_download_url = "https://download.oracle.com/java/17/latest/jdk-17_macos-x64_bin.dmg"
        java_installer_path = os.path.join(os.getenv('TEMP'), 'jdk-17_macos-x64_bin.dmg')
    elif system == "Linux":
        java_download_url = "https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz"
        java_installer_path = os.path.join(os.getenv('TEMP'), 'jdk-17_linux-x64_bin.tar.gz')
    else:
        print(f"Unsupported operating system: {system}")
        return

    download_file(java_download_url, java_installer_path)

    if system == "Windows":
        subprocess.run([java_installer_path, '/s', '/L', os.path.join(os.getenv('TEMP'), 'java_install.log')])
    elif system == "Darwin":
        subprocess.run(["hdiutil", "attach", java_installer_path])
        subprocess.run(["cp", "-R", "/Volumes/JDK 17/", "/Library/Java/JavaVirtualMachines/"])
        subprocess.run(["hdiutil", "detach", "/Volumes/JDK 17/"])
    elif system == "Linux":
        subprocess.run(["tar", "zxvf", java_installer_path, "-C", "/opt/"])

    os.remove(java_installer_path)


def check_java():
    java_path = subprocess.run(['java', '-version'], capture_output=True, text=True)
    if "17." not in java_path.stdout:
        install_java()


def launch_nova_client(root, nova_directory):
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, '.novaclient')
    exe_path = os.path.join(nova_directory, 'NovaClient.exe')

    if not os.path.exists(nova_directory):
        os.makedirs(nova_directory)
        print(f"Created directory: {nova_directory}")
        log_action(f"Created directory: {nova_directory}")

        json_url = 'https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json'
        local_json_path = os.path.join(nova_directory, 'data.json')

        download_file(json_url, local_json_path)
        log_action(f"Downloaded: {json_url} => {local_json_path}")

        with open(local_json_path, 'r') as f:
            local_json = json.load(f)

        release_url = 'https://api.github.com/repos/Nova-Alcyone/NovaClient/releases/latest'
        release_info = requests.get(release_url).json()

        if 'assets' in release_info:
            for asset in release_info['assets']:
                if asset['name'] == 'NovaClient.exe':
                    exe_url = asset['browser_download_url']
                    download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))
                    log_action(f"Downloaded: {exe_url} => {os.path.join(nova_directory, 'NovaClient.exe')}")
                    break

        local_json['latest_version'] = release_info['tag_name']

        with open(local_json_path, 'w') as f:
            json.dump(local_json, f)

    else:
        local_json_path = os.path.join(nova_directory, 'data.json')

        with open(local_json_path, 'r') as f:
            local_json = json.load(f)

        remote_json = requests.get('https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json').json()

        local_version = local_json['latest_version']
        remote_version = remote_json['latest_version']

        if remote_version > local_version:
            release_url = 'https://api.github.com/repos/Nova-Alcyone/NovaClient/releases/latest'
            release_info = requests.get(release_url).json()

            if 'assets' in release_info:
                for asset in release_info['assets']:
                    if asset['name'] == 'NovaClient.exe':
                        exe_url = asset['browser_download_url']
                        download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))
                        log_action(f"Downloaded: {exe_url} => {os.path.join(nova_directory, 'NovaClient.exe')}")
                        break

            local_json['latest_version'] = release_info['tag_name']

            with open(local_json_path, 'w') as f:
                json.dump(local_json, f)

    # Prepare the log file path
    log_file_path = os.path.join(nova_directory, 'logs.txt')

    # Launch NovaClient.exe and capture console output
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"================ Launching NovaClient.exe at {datetime.now()} ================\n")
        process = subprocess.Popen([os.path.join(nova_directory, 'NovaClient.exe')], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        log_file.write(stdout.decode('utf-8'))
        log_file.write(stderr.decode('utf-8'))
        log_file.write("\n\n")
        print(f"Launched NovaClient.exe at {datetime.now()}")
        log_action(f"Launched NovaClient.exe at {datetime.now()}")


def log_action(message):
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, '.novaclient')
    log_file_path = os.path.join(nova_directory, 'logs.txt')

    with open(log_file_path, 'a') as log_file:
        log_file.write(f"[{datetime.now()}] {message}\n")


def main():
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, 'NovaLauncher')

    if not os.path.exists(nova_directory):
        os.makedirs(nova_directory)

    loading_screen_url = 'https://github.com/Nova-Alcyone/Repo/blob/main/Launcher/images/loadingscreen.png?raw=true'
    loading_screen_response = requests.get(loading_screen_url)

    if loading_screen_response.status_code == 200:
        loading_screen_image = Image.open(BytesIO(loading_screen_response.content))
        loading_screen_image = loading_screen_image.convert("RGBA")
        image_width, image_height = loading_screen_image.size
    else:
        print(f"Failed to load image from {loading_screen_url}.")
        loading_screen_image = None
        image_width, image_height = 550, 900

    root = tk.Tk()
    root.overrideredirect(True)

    if loading_screen_image is not None:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_position = (screen_width - image_width) // 2
        y_position = (screen_height - image_height) // 2
        root.geometry(f"{image_width}x{image_height}+{x_position}+{y_position}")
        root.attributes("-topmost", True)

        loading_screen_tk = ImageTk.PhotoImage(loading_screen_image)
        loading_label = tk.Label(root, image=loading_screen_tk)
        loading_label.pack()

        check_and_download_components(nova_directory)
        root.after(500, lambda: launch_nova_client(root, nova_directory))

        root.mainloop()
    else:
        check_and_download_components(nova_directory)
        launch_nova_client(root, nova_directory)


def check_and_download_components(nova_directory):
    component_urls = [
        ('https://api.github.com/repos/Nova-Alcyone/NovaClient/releases/latest', 'NovaClient.exe'),
        ('https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json', 'data.json'),
    ]

    missing_components = []

    for component_url, component_filename in component_urls:
        component_path = os.path.join(nova_directory, component_filename)
        if not os.path.exists(component_path):
            missing_components.append((component_url, component_filename))

    if missing_components:
        for component_url, component_filename in missing_components:
            download_path = os.path.join(nova_directory, component_filename)

            if 'NovaClient.exe' in component_filename:
                release_info = requests.get(component_url).json()
                if 'assets' in release_info:
                    for asset in release_info['assets']:
                        if asset['name'] == 'NovaClient.exe':
                            exe_url = asset['browser_download_url']
                            download_file(exe_url, download_path)
                            continue

            else:
                download_file(component_url, download_path)


if __name__ == "__main__":
    main()
