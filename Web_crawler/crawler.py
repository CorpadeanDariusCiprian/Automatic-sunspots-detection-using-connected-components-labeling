import csv
import os
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()
initial_url = ""
last_visited_url_file = "last_visited_url.txt"

if os.path.exists(last_visited_url_file):
    with open(last_visited_url_file, "r") as file:
        initial_url = file.readline().strip()

if not initial_url:
    initial_url = "https://www.spaceweatherlive.com/en/archive/2012/01/01/dayobs.html"

driver.get(initial_url)

try:
    agree_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@mode='primary' and @size='large']//span[text()='AGREE']")))
    agree_button.click()
    print("Clicked the 'AGREE' button.")
except:
    print("No 'AGREE' button found or couldn't click it.")

header = "date|nrOfSpots|newRegs|imageURL"
csv_file = "scraped_data.csv"


while True:
    try:
        next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                  "//a[contains(@class, 'btn') and contains(@href, '/archive') and contains(@href, '/dayobs.html') and contains(span, 'Next day')]")))
        next_button.click()
        time.sleep(1)
        pattern = r"(?P<date>(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2}))"
        current_url = driver.current_url
        match = re.search(pattern, current_url)
        if match:
            date = match.group("date")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        tables = soup.find_all('table', class_='table table-sm table-bordered')
        for table in tables:
            image_url = ''
            rows = table.find_all('tr')
            for row in rows:
                row_text = ''
                div_col = soup.find('div', class_='col-md-8 pb-5')
                if div_col:
                    img_tag = div_col.find('img')
                    if img_tag and 'src' in img_tag.attrs:
                        image_data = img_tag.attrs
                        if 'Archief' in image_data['src']:
                            image_url = img_tag['src']
                for cell in row.find_all(['th', 'td']):
                    if cell.find('span', class_='badge bg-success'):
                        cell.find('span', class_='badge bg-success').decompose()
                    elif cell.find('span', class_='badge bg-danger'):
                        cell.find('span', class_='badge bg-danger').decompose()
                    if not cell.get_text(strip=True) == '':
                        row_text += cell.get_text(strip=True) + '|'

                if re.match(r'^\d', row_text.strip()):
                    final_row =date + "|" +  row_text.strip() + image_url
                    flare_value=''
                    TABLES = soup.find_all('table', class_='table table-bordered')
                    for table in TABLES:
                        rows = table.find_all('tr')
                        for row in rows:
                            td_elements = row.find_all('td', class_='text-center')
                            for td in td_elements:
                                flare_span = td.find('span', class_='flare')
                                if flare_span:
                                    flare_value = flare_span.get_text(strip=True)
                                    break
                    final_row += "|" + flare_value
                    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([final_row])

        with open(last_visited_url_file, "w") as file:
            file.write(driver.current_url)
    except:
        print("No more 'Next' button found.")
        break


