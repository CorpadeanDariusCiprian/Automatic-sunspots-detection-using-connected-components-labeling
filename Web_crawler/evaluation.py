import csv

file_path = r'C:\Users\dcorp\PycharmProjects\sunspots\web_crawler\scraped_data.csv'
days_count = 0
total_spots = 0
dates_counted = set()
date_appearance_counts = {}
skip_dates = {
    "2012/07/10", "2012/07/13", "2012/07/16", "2012/07/18", "2012/07/22",
    "2012/08/02", "2012/08/04", "2012/08/11", "2012/08/12", "2012/08/16", "2012/08/19",
    "2012/09/05", "2012/09/07", "2012/09/13", "2012/09/15"
}
start_date = "2012/06/01"

with open(file_path, mode='r') as file:
    reader = csv.reader(file, delimiter='|')
    next(reader)
    for row in reader:
        date, nr_of_spots = row[0], int(row[1])
        if date in skip_dates:
            continue
        if date >= start_date:
            print(nr_of_spots)
            if date in date_appearance_counts:
                date_appearance_counts[date] += 1
            else:
                date_appearance_counts[date] = 1
            total_spots += nr_of_spots
            if date not in dates_counted:
                print(date)
                days_count += 1
                print("total sunspots ",total_spots)
                dates_counted.add(date)
            if days_count == 100:
                break
total_appearances = sum(date_appearance_counts.values())

print("Total spots:", total_spots)
print("Date appearance counts:",total_appearances, date_appearance_counts)