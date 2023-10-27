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

        json_url = 'https://novaalcyone.com/storage/lanceur/novaclient/novaclient-version-info.json'
        download_file(json_url, os.path.join(nova_directory, 'novaclient-version-info.json'))

        exe_url = 'https://novaalcyone.com/storage/lanceur/novaclient/NovaClient.exe'
        download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))

    else:
        local_json_path = os.path.join(nova_directory, 'novaclient-version-info.json')
        remote_json_url = 'https://novaalcyone.com/storage/lanceur/novaclient/novaclient-version-info.json'

        with open(local_json_path, 'r') as f:
            local_json = json.load(f)

        remote_json = requests.get(remote_json_url).json()

        local_version = local_json['latest_version']
        remote_version = remote_json['latest_version']

        if remote_version > local_version:
            exe_url = 'https://novaalcyone.com/storage/lanceur/novaclient/NovaClient.exe'
            download_file(exe_url, os.path.join(nova_directory, 'NovaClient.exe'))

            download_file(remote_json_url, local_json_path)

    subprocess.run([os.path.join(nova_directory, 'NovaClient.exe')])

    root.destroy()  # Close the window after launching Nova Client


def main():
    loading_screen_url = 'https://github.com/Muyga/NovaImages/blob/main/LoadingScreen.png?raw=true'
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