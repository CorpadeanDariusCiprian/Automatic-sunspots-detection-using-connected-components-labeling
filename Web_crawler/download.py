import requests
import os
from datetime import datetime

date = datetime(2011, 12, 31)
url = f'https://spaceweather.com/images{date.year}/{date.strftime("%d%b%y").lower()}/hmi4096_blank.jpg'
response = requests.get(url)

if response.status_code == 200:
    if not os.path.exists('../ComputeSunspots/images'):
        os.makedirs('../ComputeSunspots/images')

    image_filename = f'hmi4096_{date.strftime("%Y-%m-%d")}.jpg'
    image_path = os.path.join('../ComputeSunspots/images', image_filename)
    with open(image_path, 'wb') as file:
        file.write(response.content)
    print(f"Image successfully downloaded and saved to {image_path}")
else:
    print(f"Failed to retrieve image. Status code: {response.status_code}")