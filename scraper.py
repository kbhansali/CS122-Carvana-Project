from tabnanny import check
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
import fake_useragent as fk
import re

vin_set = set()
zip_codes = [('AK', 99654),
('AL', 35242),
 ('AR', 72401),
 ('AZ', 85364),
 ('CA', 90011),
 ('CO', 80013),
 ('CT', 6902),
 ('DC', 20011),
 ('DE', 19720),
 ('FL', 33024),
 ('GA', 30043),
 ('HI', 96706),
 ('IA', 50613),
 ('ID', 83646),
 ('IL', 60629),
 ('IN', 47906),
 ('KS', 66062),
 ('KY', 40475),
 ('LA', 70726),
 ('MA', 2301),
 ('MD', 20906),
 ('ME', 4401),
 ('MI', 48197),
 ('MN', 55106),
 ('MO', 63376),
 ('MS', 39503),
 ('MT', 59901),
 ('NC', 27610),
 ('ND', 58103),
 ('NE', 68516),
 ('NH', 3103),
 ('NJ', 8701),
 ('NM', 87121),
 ('NV', 89108),
 ('NY', 11368),
 ('OH', 45011),
 ('OK', 73099),
 ('OR', 97006),
 ('PA', 19120),
 ('RI', 2860),
 ('SC', 29483),
 ('SD', 57106),
 ('TN', 37013),
 ('TX', 77449),
 ('UT', 84095),
 ('VA', 22193),
 ('VT', 5401),
 ('WA', 99301),
 ('WI', 53215),
 ('WV', 26554),
 ('WY', 82001)]

def scrape(zip_codes, quota):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    d = webdriver.Chrome(executable_path="/home/hwarzecha/chrome/chromedriver.exe", chrome_options=chrome_options)
    d.get("https://www.carvana.com/cars?page=1")
    print(d.execute_script("return navigator.userAgent"))
    time.sleep(1)
    for zip_code in zip_codes:
        d.find_element_by_css_selector("#searchToolsWrapper > div.column.right > button").click()
        time.sleep(1)
        d.find_element_by_xpath("/html/body/div[7]/div/div[2]/div[2]/div[1]/div[1]/div/div/div/input").send_keys(zip_code)
        d.find_element_by_xpath("/html/body/div[7]/div/div[2]/div[2]/div[1]/div[1]/button").click()
        time.sleep(3)
        d.find_element_by_xpath("/html/body/div[2]/main/div[1]/div/div[2]/div/button").click()
        time.sleep(1)
        d.find_element_by_xpath("/html/body/div[2]/main/div[1]/div/div[2]/div/div[2]/div[2]/button").click()
        time.sleep(1)
        count = 0
        page = 1
        url1 = "https://www.carvana.com/cars?page="
        df_rows = []
        df_cols = ["price", "model year", "manufacturer", "model", "type", "mileage", "basic info", "installed packages", "installed options", "zipcode", "150-pt"]
        while count < quota:
            listings = d.find_elements_by_class_name("result-tile")
            page_listings = []
            page += 1
            for car in listings:
                print(car.find_elements_by_tag_name("div")[0].text)
                if "CARVANA CERTIFIED" in car.find_elements_by_tag_name("div")[0].text:
                    page_listings.append(car.find_element_by_tag_name("a").get_attribute("href") + "#vehicle-details")
            for url in page_listings:
                try:
                    d.get(url)
                    print("Listing # " + str(count))
                    time.sleep(3)
                    print("Listing Page")
                    print(url)
                    listing = bs(d.page_source, "lxml")
                    listing_rows = parse_listing(listing, zip_code)
                    d.get(url[:31] + "/inspection/" + url[32:39])
                    time.sleep(2)
                    print(url[:31] + "/inspection/" + url[32:39])
                    print("150pt")
                    bs_checklist = bs(d.page_source, "lxml")
                    checklist = get_150_checklist(bs_checklist)
                    df_rows.append(tuple(listing_rows + [checklist]))
                    count += 1
                except:
                    print("skipped")
                    continue
                        
            try:
                d.get(url1 + str(page))
                
            except:
                print("INITIALIZING NEW DRIVE")
                d.close()
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                d = webdriver.Chrome(executable_path="/home/hwarzecha/chrome/chromedriver.exe", chrome_options=chrome_options)
                d.get(url1 + str(page))
            time.sleep(3)
        print("Generating DF")
        to_df(df_rows, df_cols, zip_code)

def parse_listing(bsoup, zip_code):
    rows = []
    header_inf = bsoup.find(class_="Headerstyles__VehicleDetailsAndPrice-sc-1ojpw3c-7 hrEZiT")
    rows.append((header_inf.find(class_="Headerstyles__TextLabel-sc-1ojpw3c-1 Headerstyles__TextLabelRight-sc-1ojpw3c-2 Headerstyles__Price-sc-1ojpw3c-12 kWKvvO bLkqoh BEUiv").text[1:].replace(",","")))
    
    title = header_inf.find_all("div", class_="Headerstyles__TextLabel-sc-1ojpw3c-1 Headerstyles__TextLabelLeft-sc-1ojpw3c-3 Headerstyles__MakeModel-sc-1ojpw3c-9 kWKvvO gMdmwn gPJIqU")
    rows.append(title[0].text[:4])
    rows.append(title[0].text[5:])
    rows.append(title[1].text)
    rows.append(re.findall(r"[a-zA-Z0-9 ]+ [0-9]D", header_inf.find("div", class_="Headerstyles__TextLabel-sc-1ojpw3c-1 Headerstyles__TextLabelLeft-sc-1ojpw3c-3 Headerstyles__TrimAndMileage-sc-1ojpw3c-10 kWKvvO gMdmwn kmeaaA").text)[0])
    if header_inf.find(class_="Headerstyles__TextLabel-sc-1ojpw3c-1 Headerstyles__TextLabelRight-sc-1ojpw3c-2 Headerstyles__Mileage-sc-1ojpw3c-14 kWKvvO bLkqoh kZmJfP") != None:
        rows.append(header_inf.find(class_="Headerstyles__TextLabel-sc-1ojpw3c-1 Headerstyles__TextLabelRight-sc-1ojpw3c-2 Headerstyles__Mileage-sc-1ojpw3c-14 kWKvvO bLkqoh kZmJfP").text[:-5].strip().replace(",",""))
    else:
        rows.append(re.findall(r"([0-9,]+) miles", bsoup.find(class_="Headerstyles__TextLabel-sc-1ojpw3c-1 Headerstyles__TextLabelLeft-sc-1ojpw3c-3 Headerstyles__TrimAndMileage-sc-1ojpw3c-10 kWKvvO gMdmwn kmeaaA").text)[0].replace(",",""))
    rows.append([i.text for i in bsoup.find(class_="Specificationsstyles__Section-fj3m3o-0 fRjDxY py-24 py-sm-32").find_all("li") if not ":" in i.text and "PDF" not in i.text])
    try: 
        rows.append([i.text for i in bsoup.find("div", {"data-qa":"installed-packages"}).find_all("h4")])
    except:
        rows.append([])
    try:
        rows.append([" ".join(i.text.split(" ")[:5]) for i in bsoup.find("div", {"data-qa":"installed-options"}).find_all("li")])
    except:
        rows.append([])
    rows.append(zip_code)
    return rows

def to_df(rows, cols, zip_code):
    df = pd.DataFrame(rows, columns=cols)
    df.to_csv(r"car_data_{}.csv".format(zip_code), index=False)

def get_150_checklist(soup):
    rv = []
    
    inspec_points = soup.find_all(class_='InspectionItemstyles__InspectionItemWrapper-sc-1nj88m1-0 kAXALC')
    for a in inspec_points:
        if a.find(class_="BlueCheck__Check-ilym78-0 kByKaJ") != None:
            rv.append(True)
        else:
            rv.append(False)
    return rv

scrape_codes = ['99654',
 '35242',
 '72401',
 '85364',
 '90011',
 '80013',
 '06902',
 '20011',
 '19720',
 '30043',
 '96706',
 '50613',
 '83646',
 '60629',
 '47906',
 '66062',
 '40475']


scrape(scrape_codes[17:], 1000)
 