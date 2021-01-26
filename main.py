import json
import os
import re
import shutil
import requests
from datetime import datetime
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# you can set the chromedriver path on the system path and remove this variable
CHROME_DRIVER_PATH = 'utils/chromedriver_87.exe'  # version 87.0.4280.88


def main():
    dir_name = datetime.now().date()
    # bagy_store = input('What bagy store do you want to get the catalog? ')
    bagy_store = 'mytrendy'
    bagy_store_endpoint = 'https://www.bagy.com.br/{}'.format(bagy_store)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
    print('>> Loading page')
    driver.get(bagy_store_endpoint)
    delay = 3  # seconds
    products = []
    try:
        el = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'card')))
        print('>>>> Page ready!')
        sleep(1)
        print('>> Getting products')
        qtt_els = 0
        while True:
            product_cards = driver.find_elements_by_class_name('card')
            if len(product_cards) == qtt_els:
                break
            qtt_els = len(product_cards)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(2)
        print('>> Getting details of {} products'.format(len(product_cards)))
        id = 0
        product_cards_cp = product_cards.copy()
        for product in product_cards_cp:
            # getting general information
            detail = product.find_element_by_class_name('card-body')
            price = product.find_element_by_class_name('price')
            img = product.find_element_by_class_name('img-container')
            temp = {
                'id': format(id, "04"),
                'name': detail.text,
                'price': price.text,
                'url': product.get_attribute('href'),
                'img_url': (re.split('[()]', img.value_of_css_property('background-image'))[1]).replace('"', ''),
            }
            # downloading image
            print('>>>> Getting product {}'.format(temp['id']))
            response = requests.get(temp['img_url'], stream=True)
            if response.status_code == 200:
                save_image_to_file(response, dir_name, temp['id'])
            else:
                print(response.status_code)
                print('error')
                break
            del response
            # going to the product detail page and get description
            # Open a new window
            driver.execute_script("window.open('');")
            # Switch to the new window and open URL B
            driver.switch_to.window(driver.window_handles[1])
            driver.get(temp['url'])
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'product-description')))
            product_description = driver.find_element_by_class_name('product-description')
            description = product_description.find_element_by_tag_name('p')
            temp['description'] = description.text
            driver.close()
            # Switch back to the first tab with URL A
            driver.switch_to.window(driver.window_handles[0])
            # making the product dictionary
            products.append(temp)
            id += 1
        print('>> Saving data')
        filename = 'collected_data/{}/products.json'.format(dir_name)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a', encoding='utf-8') as fp:
            saving_json = json.dumps(products, ensure_ascii=False, indent=2)
            # pickle.dump(products, fp)
            fp.write(saving_json)
            fp.write('\n')
        print('>>>> Done')
    except TimeoutException as te:
        print('>> Loading took too much time!')
        print(str(te))
        print('>>>> Exit')
    driver.close()


def save_image_to_file(image, dirname, suffix):
    img_name = 'collected_data/{dirname}/img_{suffix}.png'.format(dirname=dirname, suffix=suffix)
    os.makedirs(os.path.dirname(img_name), exist_ok=True)
    with open(img_name, 'wb') as out_file:
        image.raw.decode_content = True
        shutil.copyfileobj(image.raw, out_file)


if __name__ == "__main__":
    main()
