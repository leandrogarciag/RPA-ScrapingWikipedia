from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import mysql.connector
import time
import os

def configure_webdriver():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    chrome_driver_path = os.path.join(dir_path, 'chromedriver.exe')
    service = Service(chrome_driver_path)
    return webdriver.Chrome(service=service)

def connect_to_database():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='123456',
        database='costest',
        port=3306
    )

def extract_web_content(driver):
    driver.get('https://www.google.com.co')

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys("selenium")
    search_box.send_keys(Keys.RETURN)

    wikipedia = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, 'wikipedia')))
    wikipedia.click()

    body_content = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'bodyContent')))
    content_elements = body_content.find_elements(By.XPATH, './/p | .//ul | .//li')

    desired_content = []
    stop_phrase = "Opción de modificarle a la medida con el uso de complementos"

    for element in content_elements:
        if element.tag_name in ('p', 'ul', 'li'):
            text = element.text

            if stop_phrase in text:
                stop_index = text.find(stop_phrase)
                desired_content.append(text[:stop_index + len(stop_phrase)])
                break

            desired_content.append(text)

    return desired_content

def main():
    try:
        driver = configure_webdriver()
        desired_content = extract_web_content(driver)

        posiciones_componentes = [2,3,4,5,6]
        data_to_mysql = {
            "introduccion" : desired_content[0] if len(desired_content) > 0 else "",
            "historia": desired_content[1] if len(desired_content) > 1 else "",
            "componentes": ' '.join(desired_content[i] for i in posiciones_componentes if i < len(desired_content))
        }

        with connect_to_database() as cnx:
            with cnx.cursor() as cursor:
                add_data = ("INSERT INTO wikipedia2"
                        "(introduccion, historia, componentes) "
                        "VALUES (%(introduccion)s, %(historia)s, %(componentes)s)")
                cursor.execute(add_data, data_to_mysql)
                cnx.commit()

    except mysql.connector.Error as e:
        print(f"Error de MySQL: {str(e)}")

    except Exception as e:
        print(f"Se ha encontrado un error: {str(e)}")

    finally:
        driver.quit()

if __name__ == '__main__':
    main()
