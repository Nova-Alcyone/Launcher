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


def launch_nova_client(root):
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, 'NovaLauncher')

    if not os.path.exists(nova_directory):
        os.mkdir(nova_directory)

        json_url = 'https://github.com/Muyga/NovaRepo/blob/main/Launcher/data/novaclient-version-info.json'
        download_file(json_url, os.path.join(nova_directory, 'novaclient-version-info.json'))

        # Get the latest release from the GitHub repository
        release_url = 'https://api.github.com/repos/Muyga/NovaClient/releases/latest'
        release_info = requests.get(release_url).json()

        if 'assets' in release_info:
            # Find the asset with the name 'NovaClient.exe'
            for asset in release_info['assets']:
                if asset['name'] == 'NovaClient.exe':
                    exe_url = asset['browser_download_url']
                    download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))
                    break

    else:
        local_json_path = os.path.join(nova_directory, 'novaclient-version-info.json')

        with open(local_json_path, 'r') as f:
            local_json = json.load(f)

        remote_json = requests.get('https://raw.githubusercontent.com/Muyga/NovaRepo/main/Launcher/data/novaclient-version-info.json').json()
        print(remote_json)

        local_version = local_json['latest_version']
        remote_version = remote_json['latest_version']

        if remote_version > local_version:
            release_url = 'https://api.github.com/repos/Muyga/NovaClient/releases/latest'
            release_info = requests.get(release_url).json()

            if 'assets' in release_info:
                # Find the asset with the name 'NovaClient.exe'
                for asset in release_info['assets']:
                    if asset['name'] == 'NovaClient.exe':
                        exe_url = asset['browser_download_url']
                        download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))
                        break

    subprocess.run([os.path.join(nova_directory, 'NovaClient.exe')])

    root.destroy()  # Close the window after launching Nova Client


def main():
    loading_screen_url = 'https://github.com/Muyga/NovaRepo/blob/main/Launcher/images/LoadingScreen.png?raw=true'
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

        root.attributes("-topmost", True)  # Keep the window on top

        # Create the ImageTk PhotoImage object after the root window is created
        loading_screen_tk = ImageTk.PhotoImage(loading_screen_image)

        loading_label = tk.Label(root, image=loading_screen_tk)  # Set the background to transparent
        loading_label.pack()

        root.after(500, lambda: launch_nova_client(root))  # Launch Nova Client after 500 milliseconds

        root.mainloop()
    else:
        launch_nova_client(root)  # Continue the process without displaying a window


if __name__ == "__main__":
    main()
