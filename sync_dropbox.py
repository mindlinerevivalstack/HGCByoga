import os
import dropbox
from dropbox.exceptions import ApiError
from dropbox.files import FileMetadata, FolderMetadata

# Load token from GitHub Actions secret
DROPBOX_TOKEN = os.getenv('DROPBOX_TOKEN')

# EXACT Dropbox folder name
DROPBOX_FOLDER = '/Brittany Buckner Yoga by AREXPRESSIONS.COM'

# Local folder inside GitHub repo
LOCAL_FOLDER = 'images'

dbx = dropbox.Dropbox(DROPBOX_TOKEN)

def download_folder(dropbox_path, local_path):
    os.makedirs(local_path, exist_ok=True)

    try:
        result = dbx.files_list_folder(dropbox_path, recursive=False)
    except ApiError as e:
        print(f"Dropbox error: {e}")
        return

    entries = result.entries

    # Pagination support
    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        entries.extend(result.entries)

    for entry in entries:
        if isinstance(entry, FileMetadata):
            local_file = os.path.join(local_path, entry.name)

            # Skip unchanged files
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

# Start sync
download_folder(DROPBOX_FOLDER, LOCAL_FOLDER)
