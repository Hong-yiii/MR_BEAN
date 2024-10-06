import os
import requests
from tqdm import tqdm
import time
import re

# Replace this with your Earthdata authentication token
TOKEN = "eyJ0eXAiOiJKV1QiLCJvcmlnaW4iOiJFYXJ0aGRhdGEgTG9naW4iLCJzaWciOiJlZGxqd3RwdWJrZXlfb3BzIiwiYWxnIjoiUlMyNTYifQ.eyJ0eXBlIjoiVXNlciIsInVpZCI6ImJlYXJiM2FyIiwiZXhwIjoxNzMzMzE4MzY4LCJpYXQiOjE3MjgxMzQzNjgsImlzcyI6Imh0dHBzOi8vdXJzLmVhcnRoZGF0YS5uYXNhLmdvdiJ9.NOBppbbqXmGlOiYD7a87BCgoI_uyWP7g9BcSSOj15yxZYKDbgA-W95dPB2OkbGDkJ_9adEWqBQCKTMmR1NNVKprTHAxp4iyt1418BvEB--O4otvFuQo1lWLEEBDSfJToJ1PhXOxpgJudcjEZAJWV9GYFypjKzL2hvpl-Y6KdBgboCNfTLs0OeG6N-qwDDtph68nnm2fQ1oIcBLs51cM5SfJUgUubHFS-c8rN-kjV24ICi3FnISAQ8lFVh5vpp-V3fTyep-P4hw0sa9PT3XP5U0ByvrwFwRB65QmbLJxSx0HUxN_df22V9l339XLxzC1fGa42kEZy_uqVJQNn4ot2bA"

# Directory to save the downloaded files
download_directory = "./MERRA2_Files"

# Create the download directory if it doesn't exist
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Path to the file containing the list of URLs
file_path = "subset_M2T1NXFLX_5.12.4_20241005_141013_.txt"  # Ensure the file path is correct

# Read the file to get the list of URLs
try:
    with open(file_path, "r") as file:
        urls = file.readlines()
    print(f"Total URLs read from file: {len(urls)}")
except FileNotFoundError:
    print(f"File not found: {file_path}")
    exit()

# Filter URLs for .nc4 files (adjust condition)
filtered_urls = [url.strip() for url in urls if ".nc4" in url]
print(f"Total .nc4 URLs found: {len(filtered_urls)}")

# Select every 14th file (every two weeks approximately)
selected_urls = filtered_urls[::14]
print(f"Total URLs selected for download (every two weeks): {len(selected_urls)}")

# Function to extract the date from the URL using a refined regex pattern
def extract_date_from_url(url):
    # Use a regex pattern that looks for the date format YYYYMMDD after 'granules/'
    match = re.search(r'granules/.*?(\d{8})', url)
    if match:
        date_str = match.group(1)
        print(f"Extracted date: {date_str} from URL: {url}")  # Debug: Print the extracted date
        return date_str
    else:
        print(f"Failed to extract date from URL: {url}")  # Debug: Indicate if date extraction failed
        return "unknown_date"

# Function to rename the "lon" file if it exists
def rename_lon_file(local_filename, date_str):
    if os.path.exists(local_filename):
        new_filename = f"MERRA2_{date_str}.nc4"
        new_file_path = os.path.join(download_directory, new_filename)
        os.rename(local_filename, new_file_path)
        print(f"File '{local_filename}' renamed to '{new_filename}'")

# Function to download a file from a given URL using Bearer Token Authentication
def download_file(url, download_path, headers):
    # Create a temporary filename 'lon' for the download
    temp_filename = "lon"
    local_filename = os.path.join(download_path, temp_filename)

    # Extract the date from the URL for naming the file after download
    date_str = extract_date_from_url(url)

    retries = 3
    for attempt in range(retries):
        try:
            print(f"\nAttempting to download: {date_str}.nc4 (Attempt {attempt + 1} of {retries})")
            # Use the headers parameter to pass the Bearer Token for authentication
            with requests.get(url, stream=True, headers=headers) as r:
                print(f"Status Code: {r.status_code}")
                print(f"Headers: {r.headers}")

                if r.status_code == 200:
                    total_size = int(r.headers.get('content-length', 0))
                    print(f"Successfully connected. Content length: {total_size} bytes")

                    with open(local_filename, 'wb') as f, tqdm(
                        desc=date_str,
                        total=total_size,
                        unit='B',
                        unit_scale=True,
                        unit_divisor=1024,
                    ) as bar:
                        for chunk in r.iter_content(chunk_size=262144):
                            if chunk:
                                f.write(chunk)
                                bar.update(len(chunk))

                    print(f"Download completed: {date_str}.nc4\n")

                    # Rename the file from 'lon' to 'MERRA2_<date>.nc4'
                    rename_lon_file(local_filename, date_str)
                    break

                elif r.status_code == 401:
                    print(f"Unauthorized access: HTTP Status Code {r.status_code}. Check your token.")
                    break
                else:
                    print(f"Failed to download {date_str}.nc4. HTTP Status Code: {r.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error downloading {date_str}.nc4: {e}")
            time.sleep(2)

    else:
        print(f"Failed to download {date_str}.nc4 after {retries} attempts.")

# Create headers with the Bearer Token
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

# Download each selected file with the Bearer Token Authentication
for url in selected_urls:
    print(f"Starting download for: {url}")
    download_file(url, download_directory, headers)
