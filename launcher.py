import json
import os
import subprocess
import tkinter as tk
from io import BytesIO
import requests
from PIL import Image, ImageTk


def download_file(url, dest_path):
    response = requests.get(url)
    if response.status_code == 200:  # Check if the download is successful
        with open(dest_path, 'wb') as f:
            f.write(response.content)
    else:
        print(f"L'image à l'URL {url} n'a pas été trouvée.")
        return  # Exit the function if the image is not found


def launch_nova_client(root, nova_directory):
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, 'NovaLauncher')
    exe_path = os.path.join(nova_directory, 'NovaClient.exe')

    if not os.path.exists(nova_directory):
        os.mkdir(nova_directory)

        json_url = 'https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json'
        local_json_path = os.path.join(nova_directory, 'data.json')

        download_file(json_url, local_json_path)  # Download the JSON file

        with open(local_json_path, 'r') as f:
            local_json = json.load(f)

        # Get the latest release from the GitHub repository
        release_url = 'https://github.com/Nova-Alcyone/Client/releases/latest/download/NovaClient.exe'
        release_info = requests.get(release_url).json()

        if 'assets' in release_info:
            # Find the asset with the name 'NovaClient.exe'
            for asset in release_info['assets']:
                if asset['name'] == 'NovaClient.exe':
                    exe_url = asset['browser_download_url']
                    download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))
                    break

        local_json['latest_version'] = release_info['tag_name']

        # Update the "latest_version" field in the local JSON file
        with open(local_json_path, 'w') as f:
            json.dump(local_json, f)

    else:
        local_json_path = os.path.join(nova_directory, 'data.json')

        with open(local_json_path, 'r') as f:
            local_json = json.load(f)

        remote_json = requests.get('https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json').json()
        print(remote_json)

        local_version = local_json['latest_version']
        remote_version = remote_json['latest_version']

        if remote_version > local_version:
            release_url = 'https://api.github.com/repos/Nova-Alcyone/Client/releases/latest'
            release_info = requests.get(release_url).json()

            if 'assets' in release_info:
                # Find the asset with the name 'NovaClient.exe'
                for asset in release_info['assets']:
                    if asset['name'] == 'NovaClient.exe':
                        exe_url = asset['browser_download_url']
                        download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))
                        break

            local_json['latest_version'] = release_info['tag_name']

            # Update the "latest_version" field in the local JSON file
            with open(local_json_path, 'w') as f:
                json.dump(local_json, f)

    subprocess.run([os.path.join(nova_directory, 'NovaClient.exe')])

    root.destroy()  # Close the window after launching Nova Client


def main():
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, 'NovaLauncher')

    if not os.path.exists(nova_directory):
        os.mkdir(nova_directory)

    loading_screen_url = 'https://github.com/Nova-Alcyone/Repo/blob/main/Launcher/images/LoadingScreen.png?raw=true'
    loading_screen_response = requests.get(loading_screen_url)

    if loading_screen_response.status_code == 200:
        loading_screen_image = Image.open(BytesIO(loading_screen_response.content))
        # Ensure transparency is preserved when opening the image
        loading_screen_image = loading_screen_image.convert("RGBA")
        image_width, image_height = loading_screen_image.size
    else:
        print(f"L'image à l'URL {loading_screen_url} n'a pas été trouvée.")
        loading_screen_image = None
        image_width, image_height = 550, 900  # Default window size if image is not found

    root = tk.Tk()
    # Hide the root window drag bar and close button
    root.overrideredirect(True)

    if loading_screen_image is not None:
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_position = (screen_width - image_width) // 2
        y_position = (screen_height - image_height) // 2
        root.geometry(f"{image_width}x{image_height}+{x_position}+{y_position}")

        # Create the ImageTk PhotoImage object after the root window is created
        loading_screen_tk = ImageTk.PhotoImage(loading_screen_image)

        loading_label = tk.Label(root, image=loading_screen_tk)  # Set the background to transparent
        loading_label.pack()

        # Check for 'NovaLauncher.exe' and components after creating the directory
        check_and_download_components(nova_directory)

        root.after(500, lambda: launch_nova_client(root, nova_directory))  # Launch Nova Client after 500 milliseconds

        root.mainloop()
    else:
        # Check for 'NovaLauncher.exe' and components without displaying a window
        check_and_download_components(nova_directory)
        launch_nova_client(root, nova_directory)  # Continue the process without displaying a window


def check_and_download_components(nova_directory):
    # Define a list of component download URLs and their corresponding file names
    component_urls = [
        ('https://api.github.com/repos/Nova-Alcyone/Client/releases/latest', 'NovaClient.exe'),
        ('https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json', 'data.json'),
    ]

    missing_components = []

    for component_url, component_filename in component_urls:
        component_path = os.path.join(nova_directory, component_filename)
        if not os.path.exists(component_path):
            # Component is missing, add it to the missing_components list
            missing_components.append((component_url, component_filename))

    # If either the .json or .exe is missing, download both
    if missing_components:
        for component_url, component_filename in missing_components:
            download_path = os.path.join(nova_directory, component_filename)

            if 'NovaClient.exe' in component_filename:
                release_info = requests.get(component_url).json()
                if 'assets' in release_info:
                    # Find the asset with the name 'NovaClient.exe'
                    for asset in release_info['assets']:
                        if asset['name'] == 'NovaClient.exe':
                            exe_url = asset['browser_download_url']
                            download_file(exe_url, download_path)
                            continue

            else:
                download_file(component_url, download_path)


if __name__ == "__main__":
    main()