import requests
import zipfile

def download_large_file(file_id, destination):
    """
    Download a large Google Drive file, bypassing the virus scan warning.
    """
    base_url = "https://drive.usercontent.google.com/download"
    params = {"id": file_id, "confirm": "t"}

    with requests.get(base_url, params=params, stream=True) as response:
        response.raise_for_status()
        with open(destination, "wb") as f:
            for chunk in response.iter_content(chunk_size=32768):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)
    print(f"File downloaded successfully: {destination}")

def unzip_file(zip_file, extract_to):
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
        print(f"Unzipped the file to {extract_to}")

try:
    file_id = "1qO4T-YVSrDKiShAgc3nA4nsbq3lRcJ1k"  # Replace with your file ID
    destination = "fine_tuned_camembert.zip"
    download_large_file(file_id, destination)

    # Step 2: Unzip the downloaded file
    extract_to = "fine_tuned_camembert2"  # Directory where the contents will be extracted
    
    unzip_file(destination, extract_to) 
except Exception as e:
    print(f"Error during download: {e}")

