import csv
import os
import re
import time
import datetime
import numpy as np
import pytesseract
import requests
import cv2
from io import BytesIO
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup

def scrape_links(start_year, start_month, start_day):
    driver = webdriver.Chrome()
    base_url = "https://spaceweather.com/images"
    csv_file = "scraped_data2.csv"
    last_visited_date_file = "last_visited_date.txt"
    image_folder = "downloaded_images"

    if not os.path.exists(image_folder):
        os.makedirs(image_folder)

    if os.path.exists(last_visited_date_file):
        with open(last_visited_date_file, "r") as file:
            last_visited_date_str = file.read().strip()
            last_visited_date = datetime.datetime.strptime(last_visited_date_str, "%Y-%m-%d").date()
    else:
        last_visited_date = datetime.date(start_year, start_month, start_day)

    with open(csv_file, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        current_date = datetime.datetime.now().date()
        while last_visited_date <= current_date:
            url = f"{base_url}{last_visited_date.year}/{last_visited_date.strftime('%d%b%y').lower()}/hmi4096_blank.jpg"
            driver.get(url)
            time.sleep(1)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            image = soup.find_all('img', src=lambda src: src.endswith("/hmi4096_blank.jpg"))
            if image:
                writer.writerow([last_visited_date.strftime("%Y/%m/%d"), url])
                image_url = url
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_path = os.path.join(image_folder, f"{last_visited_date.strftime('%Y%m%d')}.jpg")
                    with open(image_path, "wb") as image_file:
                        image_file.write(response.content)
            else:
                writer.writerow([last_visited_date.strftime("%Y/%m/%d")])
            last_visited_date += datetime.timedelta(days=1)
            with open(last_visited_date_file, "w") as file:
                file.write(str(last_visited_date))
    driver.quit()

