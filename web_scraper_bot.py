import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from automated_alerts import send_message


URL = "https://stocktrack.ca"
POST_CODE = "V3A 0A5"
USER_EMAIL = "marlonrfajardo@gmail.com"

PRODUCTS = ['PS5 Disc', 'PS5 Digital']
STORE_INVENTORIES = {
    'wm': {
        'frame_xpath': '/html/body/div[1]/div[2]/div/div[2]/div/iframe',
        'btn_xpath': '/html/body/div[2]/div/div[1]/div[2]/div/div/div[1]/div[2]/div/div/div[8]/div/div[2]',
        'stock_num_position': 'td:nth-last-child(2)',
        'name': 'Walmart',
        'stores_num': '20',
        'codes': {
            'PS5 Disc': '71171954856',
            'PS5 Digital': '71171954857'
        }
    },
    'st': {
        'frame_xpath': '/html/body/div[1]/div[2]/div/div[4]/div/iframe',
        'btn_xpath': '/html/body/div[1]/div/div[1]/div[2]/div/div/div[1]/div[2]/div/div/div[7]/div/div[2]',
        'stock_num_position': 'td:last-child',
        'name': 'Staples',
        'stores_num': '22',
        'codes': {
            'PS5 Disc': '2993213',
            'PS5 Digital': '2993214'
        }
    },
    'bb': {
        'frame_xpath': '/html/body/div[1]/div[2]/div/div[5]/div/iframe',
        'btn_xpath': '/html/body/div[1]/div/div[1]/div[2]/div/div/div[1]/div[2]/div/div/div[7]/div/div[2]',
        'stock_num_position': 'td:last-child',
        'name': 'Best Buy',
        'stores_num': '50',
        'codes': {
            'PS5 Disc': '15689336',
            'PS5 Digital': '15689335'
        }
    },
    'src': {
        'frame_xpath': '/html/body/div[1]/div[2]/div/div[6]/div/iframe',
        'btn_xpath': '/html/body/div[1]/div/div[1]/div[2]/div/div/div[1]/div[2]/div/div/div[8]/div/div[2]',
        'stock_num_position': 'td:last-child',
        'name': 'The Source',
        'stores_num': '11',
        'codes': {
            'PS5 Disc': '108090499',
            'PS5 Digital': '108090498'
        }
    }
}


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    driver = webdriver.Chrome(options=options)
    return driver


def input_send_keys(driver, css_selector, keys_to_send):
    input_elm = driver.find_element(By.CSS_SELECTOR, css_selector)
    input_elm.clear()
    input_elm.send_keys(keys_to_send)


def format_stock_results(stock, product, stock_position, store_code):
    store_name = STORE_INVENTORIES[store_code]['name']
    inventory = []

    for i in range(len(stock)):
        stock_entry = {}
        status = stock[i].find_element(
            By.CSS_SELECTOR, stock_position).get_attribute('innerText')
        loc = stock[i].find_element(
            By.CSS_SELECTOR, "td:nth-child(2)").get_attribute('innerText')

        if status.isnumeric() and int(status) > 0:
            stock_entry["product"] = product
            stock_entry["store"] = store_name
            stock_entry["location"] = loc
            stock_entry["stock"] = status

            inventory.append(stock_entry)
    return inventory


def progress_loader_wait(driver):
    wait = WebDriverWait(driver, 30)
    try:
        wait.until_not(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, 'dhx_cell_progress_img')))
    except TimeoutException:
        pass


def scrape(driver, post_code, store_code, product, product_code, stores_limit, frame_path, btn_path, stock_position):
    driver.get(f"{URL}?s={store_code}")
    driver.implicitly_wait(5)
    time.sleep(3)
    try:
        driver.find_element(By.CSS_SELECTOR, "input[name=q]")
    except Exception:
        driver.switch_to.frame(driver.find_element(By.XPATH, frame_path))

    WebDriverWait(driver, 500).until(EC.invisibility_of_element_located(
        (By.CLASS_NAME, 'cf-browser-verification')))

    input_send_keys(driver, "input[name = q]", product_code)
    input_send_keys(driver, "input[name = loc]", post_code)
    store_limit_css = 'input[name = num]' if store_code != 'bb' else 'input[name = km]'
    input_send_keys(driver, store_limit_css, stores_limit)
    driver.find_element(By.XPATH, btn_path).click()

    progress_loader_wait(driver)

    driver.implicitly_wait(3)
    stock = driver.find_elements(
        By.CSS_SELECTOR, '.objbox > table > tbody > .ev_dhx_web, .odd_dhx_web')

    return format_stock_results(stock, product, stock_position, store_code)


def generate_message(results):
    message = ""
    for result in results:
        if int(result['stock']) > 1:
            message += f"{result['stock']} {result['product']}s available at {result['location']} ({result['store']})\n"
        else:
            message += f"{result['stock']} {result['product']} available at {result['location']} ({result['store']})\n"
    return message


def scrape_loop():
    stores = list(STORE_INVENTORIES.keys())
    driver = setup_driver()
    available_stock = []
    for store in stores:
        for product in PRODUCTS:
            result = scrape(
                driver,
                POST_CODE,
                store,
                product,
                STORE_INVENTORIES[store]['codes'][product],
                STORE_INVENTORIES[store]['stores_num'],
                STORE_INVENTORIES[store]['frame_xpath'],
                STORE_INVENTORIES[store]['btn_xpath'],
                STORE_INVENTORIES[store]['stock_num_position']
            )
            available_stock.extend(result)
    print(str(available_stock))
    if available_stock:
        message = generate_message(available_stock)
        # send_sms("PS5 Stock Update", message,
        #          "7782313497@txt.freedommobile.ca")
        send_message("PS5 Stock Update", message, USER_EMAIL)
