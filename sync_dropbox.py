import os
import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata, FolderMetadata

DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')
DROPBOX_FOLDER = '/Brittany Buckner Yoga by AREXPRESSIONS.COM'
LOCAL_FOLDER = 'images'
INDEX_FILE = 'images_index.txt'

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

def download_folder(dropbox_path, local_path):
    os.makedirs(local_path, exist_ok=True)

    try:
        result = dbx.files_list_folder(dropbox_path, recursive=False)
    except ApiError as e:
        print(f"Dropbox error: {e}")
        return

    entries = result.entries

    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        entries.extend(result.entries)

    for entry in entries:
        if isinstance(entry, FileMetadata):
            local_file = os.path.join(local_path, entry.name)

            if os.path.exists(local_file):
                print(f"Skipping unchanged file: {entry.name}")
                continue

            try:
                metadata, response = dbx.files_download(entry.path_display)
                with open(local_file, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {entry.name}")
            except ApiError as e:
                print(f"Error downloading {entry.name}: {e}")

        elif isinstance(entry, FolderMetadata):
            new_dropbox_path = entry.path_display
            new_local_path = os.path.join(local_path, entry.name)
            download_folder(new_dropbox_path, new_local_path)

def generate_index_file():
    with open(INDEX_FILE, 'w') as index:
        for root, dirs, files in os.walk(LOCAL_FOLDER):
            for file in files:
                raw_url = f"https://raw.githubusercontent.com/mindlinerevivalstack/HGCByoga/main/{root}/{file}"
                index.write(raw_url + "\n")
    print("Generated images_index.txt")

download_folder(DROPBOX_FOLDER, LOCAL_FOLDER)
generate_index_file()
