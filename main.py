import json
import os
import re
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# you can set the chromedriver path on the system path and remove this variable
CHROME_DRIVER_PATH = 'utils/chromedriver_87.exe'  # version 87.0.4280.88


def main():
    bagy_store = input('What bagy store do you want to get the catalog?')
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
        for product in product_cards:
            detail = product.find_element_by_class_name('card-body')
            price = product.find_element_by_class_name('price')
            img = product.find_element_by_class_name('img-container')
            temp = {
                'name': detail.text,
                'price': price.text,
                'url': product.get_attribute('href'),
                'img': (re.split('[()]', img.value_of_css_property('background-image'))[1]).replace('"', '')
            }
            products.append(temp)
        print('>> Saving data')
        filename = 'collected_data/products.json'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a', encoding='utf-8') as fp:
            saving_json = json.dumps(products, ensure_ascii=False, indent=2)
            # pickle.dump(products, fp)
            fp.write(saving_json)
            fp.write('\n')
        print('>>>> Done')
    except TimeoutException:
        print('>> Loading took too much time!')
        print('>>>> Exit')


if __name__ == "__main__":
    main()