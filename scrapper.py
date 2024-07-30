from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import time
import multiprocessing
from db_blueprint import connect_to_db
def get_date_now() -> datetime:
    return datetime.now()

def scraping_windguru(url):
    chrome_options = Options()
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    #test if its winguru site
    assert "Windguru" in driver.title
    driver.implicitly_wait(15)
    try:
        accept_button = WebDriverWait(driver, 11).until(EC.element_to_be_clickable((By.ID, 'accept-choices')))
        accept_button.click()
    except Exception as e:
        print(f"Accept button not found or not clickable: {e}")
        print("Page source for debugging:")
        print(driver.page_source)
    #click to change the arrows to degres
    element = WebDriverWait(driver, 11).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[8]/div[2]/div[4]/div[1]/table/tbody/tr[4]/td[1]/span')))
    element.click()
    #select a table with the data
    parent_element = driver.find_element(By.XPATH, '/html/body/div[8]/div[2]/div[4]/div[1]/div[2]/table/tbody')
    title = driver.title
    place = title.replace("Windguru - ", "")
    html_content = parent_element.get_attribute('outerHTML')
    driver.quit()
    return place, html_content

def beautifulsoup_html_parsing(url, place, html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    wind_data_to_tr = soup.find_all('tr')
    array_of_all_elements = []
    for wind_data_to_tr_placeholder in wind_data_to_tr:
        wind_data_to_td = wind_data_to_tr_placeholder.find_all('td')
        for td in wind_data_to_td:
            array_of_all_elements.append(td.text)

    # row has 110 elements standard
    # Rows discription
    # 1 infomration about day and hour of the mesurment
    # 2 info about normal wind strength
    # 3 info about wind gust strength
    # 4 info about winf direction
    # 5 info about tempeture
    # 6 info about cloud cover
    # 7 info about rain
    array_of_clear_data = array_of_all_elements[:-127]
    day_array = []
    hour_array = []
    normal_wind_array = []
    gust_wind_array = []
    wind_direction_array = []
    temperature_array = []
    cloud_cover_array = []
    rain_array = []
    for index in range(len(array_of_clear_data)):
        if index < 110:
            # regex here  'We31.03h' add logic for date time with the 31 and get regex for .03h = 3 -godzina
            day_array.append()
            hour_array.append()
        if index < 220:
            normal_wind_array.append(array_of_clear_data[index])
        if index < 330:
            gust_wind_array.append(array_of_clear_data[index])
        if index < 440:
            # regex here delete the ° from '288°'
            wind_direction_array.append()
        if index < 550:
            temperature_array.append(array_of_clear_data[index])
        if index < 660:
            # chyba regex ogarnac te gowno '70\xa05', '69\xa0\xa0', '99\xa0\xa0', '46279', '1007832', '1008348'
            cloud_cover_array.append(array_of_clear_data[index])
        if index < 770:
            # regex exlude '\xa0'
            rain_array.append(array_of_clear_data[index])

    for index in range(len(day_array)):
        uplaod_data_to_db(url,place, day_array[index], hour_array[index], normal_wind_array[index], gust_wind_array[index],
                          wind_direction_array[index], temperature_array[index], cloud_cover_array[index],
                          rain_array[index])


def uplaod_data_to_db(site,place, date, hour , normal_wind, gust_wind, wind_direction, temperature, cloud_cover, rain):
    c, conn = connect_to_db()
    time_of_parcing = get_date_now()
    c.execute(f'''INSERT INTO wind_data (site, place, time_of_parsing, date, hour, normal_wind, gust_wind, wind_direction, temperature, cloud_cover, rain)
                        VALUES ('{site}','{place}','{time_of_parcing}','{date}','{hour}','{normal_wind}','{gust_wind}','{wind_direction}','{temperature}','{cloud_cover}','{rain}');''')
    conn.commit()
    conn.close()

def single_scrappe_main(url):
    place, html_content = scraping_windguru(url)
    beautifulsoup_html_parsing(url, place, html_content)


if __name__ == "__main__":
    url = 'https://www.windguru.cz/279709'
    single_scrappe_main(url)
