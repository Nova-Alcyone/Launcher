import json
import os
import subprocess
import tkinter as tk
from io import BytesIO
import requests
from PIL import Image, ImageTk
from requests.exceptions import RequestException, ConnectionError, HTTPError, Timeout
from json.decoder import JSONDecodeError

def download_file(url, dest_path):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(dest_path, 'wb') as f:
            f.write(response.content)
    except (RequestException, ConnectionError, HTTPError, Timeout) as e:
        print(f"An error occurred while downloading the file from {url}: {e}")

def check_and_download_components(nova_directory):
    # Define a list of component download URLs and their corresponding file names
    component_urls = [
        ('https://github.com/Nova-Alcyone/Client/releases/latest/download/NovaClient.exe', 'NovaClient.exe'),
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

            try:
                response = requests.get(component_url)
                response.raise_for_status()  # Raise an exception for HTTP errors

                if response.status_code == 200:
                    # Check if the component is 'NovaClient.exe' (binary file)
                    if component_filename == 'NovaClient.exe':
                        with open(download_path, 'wb') as f:
                            f.write(response.content)
                    else:
                        try:
                            component_info = response.json()
                        except JSONDecodeError as e:
                            print(f"JSON decoding error for {component_filename}: {e}")
                            component_info = {}  # Set an empty dictionary in case of JSON decoding error

                        if 'latest_version' in component_info:
                            # Handle 'data.json' specifically
                            with open(download_path, 'w') as f:
                                json.dump(component_info, f)
                        else:
                            print(f"Invalid data received for {component_filename}.")
                else:
                    print(f"Failed to retrieve data from {component_url}. Status code: {response.status_code}")
            except (RequestException, ConnectionError, HTTPError, Timeout) as e:
                print(f"An error occurred while downloading {component_filename}: {e}")



def launch_nova_client(root, nova_directory):
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, 'NovaLauncher')
    exe_path = os.path.join(nova_directory, 'NovaClient.exe')

    try:
        if not os.path.exists(nova_directory):
            os.mkdir(nova_directory)

            json_url = 'https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json'
            local_json_path = os.path.join(nova_directory, 'data.json')

            download_file(json_url, local_json_path)  # Download the JSON file

            with open(local_json_path, 'r') as f:
                local_json = json.load(f)

            # Get the latest release from the GitHub repository
            release_url = 'https://github.com/Nova-Alcyone/Client/releases/latest/download/NovaClient.exe'
            release_response = requests.get(release_url)
            release_response.raise_for_status()  # Raise an exception for HTTP errors

            try:
                release_info = release_response.json()
            except JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                return  # Exit the function if JSON decoding fails

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

            remote_json = requests.get('https://raw.githubusercontent.com/Nova-Alcyone/Repo/main/Launcher/data/data.json')

            try:
                remote_json_data = remote_json.json()
            except JSONDecodeError as e:
                print(f"JSON decoding error: {e}")
                return  # Exit the function if JSON decoding fails

            print(remote_json_data)

            local_version = local_json['latest_version']
            remote_version = remote_json_data.get('latest_version')

            if remote_version and remote_version > local_version:
                release_url = 'https://github.com/Nova-Alcyone/Client/releases/latest/download/NovaClient.exe'
                release_response = requests.get(release_url)
                release_response.raise_for_status()  # Raise an exception for HTTP errors

                try:
                    release_info = release_response.json()
                except JSONDecodeError as e:
                    print(f"JSON decoding error: {e}")
                    return  # Exit the function if JSON decoding fails

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

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"An error occurred: {e}")

def main():
    appdata_path = os.getenv('APPDATA')
    nova_directory = os.path.join(appdata_path, 'NovaLauncher')

    try:
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

    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
