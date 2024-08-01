from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import time
import multiprocessing
from db_blueprint import connect_to_db
def get_date_now() -> datetime:
    return datetime.now()

def change_int_into_datetime(day: int)-> datetime:
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    if day < current_date.day:
        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1
    return datetime(year=current_year, month=current_month, day=day)

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

    # Dictionary to hold arrays of text from <td> elements based on <tr> id
    tr_id_to_td_texts = {}

    for wind_data_to_tr_placeholder in wind_data_to_tr:
        tr_id = wind_data_to_tr_placeholder.get('id')
        if tr_id:  # Check if the <tr> has an id attribute
            wind_data_to_td = wind_data_to_tr_placeholder.find_all('td')
            td_texts = [td.text for td in wind_data_to_td]
            # Store the texts in the dictionary under the key of the tr's id
            tr_id_to_td_texts[tr_id] = td_texts

    # row has 110 elements standard
    # Rows discription
    # 1 infomration about day and hour of the mesurment
    # 2 info about normal wind strength
    # 3 info about wind gust strength
    # 4 info about winf direction
    # 5 info about tempeture
    # 6 info about cloud cover
    # 7 info about rain

    day_array = []
    hour_array = []
    normal_wind_array = []
    gust_wind_array = []
    wind_direction_array = []
    temperature_array = []
    cloud_cover_array = []
    rain_array = []
    #cale trzwba z reworkowac gowno jebane
    '''
    for index in range(len(array_of_clear_data)):
        if index < 107:
            pattern = r"(\d+)\.(\d+)"
            match = re.search(pattern, array_of_clear_data[index])
            before_period = int(match.group(1))
            after_period = int(match.group(2))
            print(index)
            day_array.append(change_int_into_datetime(before_period))
            hour_array.append(after_period)
        elif index < 213:
            print(index)
            normal_wind_array.append(array_of_clear_data[index])
        elif index < 319:
            print(index)
            gust_wind_array.append(array_of_clear_data[index])
        elif index < 425:
            print(index)
            print(array_of_clear_data[index])
            pattern = r"(\d+)°"
            match = re.search(pattern, array_of_clear_data[index])
            #if match is None:
                #wind_direction_array.append(array_of_clear_data[index])
            #else:
            number = int(match.group(1))
            wind_direction_array.append(number)
        elif index < 531:
            print(index)
            temperature_array.append(array_of_clear_data[index])
        elif index < 637:
            print(index)
            original_string = array_of_clear_data[index]
            modified_string = re.sub(r'\xa0', '00', original_string)
            final_int = float(modified_string.replace('\\', ''))
            cloud_cover_array.append(final_int)
        elif index < 743:
            print(index)
            original_string = array_of_clear_data[index]
            modified_string = re.sub(r'\xa0', '0', original_string)
            final_int = float(modified_string.replace('\\', ''))
            rain_array.append(final_int)

    for index in range(len(day_array)):
        uplaod_data_to_db(url, place, day_array[index], hour_array[index], normal_wind_array[index], gust_wind_array[index],
                          wind_direction_array[index], temperature_array[index], cloud_cover_array[index],
                          rain_array[index])
    '''

def uplaod_data_to_db(site,place, date, hour , normal_wind, gust_wind, wind_direction, temperature, cloud_cover, rain):
    c, conn = connect_to_db()
    time_of_parcing = get_date_now()
    c.execute(f'''INSERT INTO wind_data (site, place, time_of_parsing, date, hour, normal_wind, gust_wind, wind_direction, temperature, cloud_cover, rain)
                        VALUES ('{site}','{place}','{time_of_parcing}','{date}','{hour}','{normal_wind}','{gust_wind}','{wind_direction}','{temperature}','{cloud_cover}','{rain}');''')
    conn.commit()
    conn.close()

def single_scrappe_main(url):
    place, html_content = scraping_windguru(url)
    print(html_content)
    #beautifulsoup_html_parsing(url, place, html_content)


if __name__ == "__main__":
    url = 'https://www.windguru.cz/279709'
    single_scrappe_main(url)
