import csv
import os
import requests

base_url = "https://www.spaceweatherlive.com"
csv_file = "scraped_data.csv"
image_folder = "images_with_labels"
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

last_link_index_file = "last_link_index.txt"

if os.path.exists(last_link_index_file):
    with open(last_link_index_file, "r") as file:
        last_link_index = int(file.readline().strip())
else:
    last_link_index = 0

with open(csv_file, "r") as file:
    reader = csv.DictReader(file, delimiter="|")
    for i, row in enumerate(reader):
        if i < last_link_index:
            continue
        image_url = row["labelImageURL"]
        if image_url:
            full_image_url = base_url + image_url
            filename = os.path.basename(image_url)
            response = requests.get(full_image_url)
            if response.status_code == 200:
                with open(os.path.join(image_folder, filename), "wb") as image_file:
                    image_file.write(response.content)
                print(f"Downloaded: {filename}")
                with open(last_link_index_file, "w") as file:
                    file.write(str(i))
            else:
                print(f"Failed to download: {filename}")
