from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

# Amazon login credentials
AMAZON_EMAIL = "your_email@example.com"
AMAZON_PASSWORD = "your_password"

# Setup WebDriver
service = Service('c:\chromedriver.exe')  
driver = webdriver.Chrome(service=service)

def amazon_login(driver):
    """Logs in to Amazon with user credentials."""
    driver.get("https://www.amazon.com")
    time.sleep(2)
    
    # Click on the sign-in button
    sign_in_button = driver.find_element(By.ID, "nav-link-accountList")
    sign_in_button.click()
    
    # Enter email
    email_field = driver.find_element(By.ID, "ap_email")
    email_field.send_keys(AMAZON_EMAIL)
    email_field.send_keys(Keys.RETURN)
    time.sleep(2)
    
    # Enter password
    password_field = driver.find_element(By.ID, "ap_password")
    password_field.send_keys(AMAZON_PASSWORD)
    password_field.send_keys(Keys.RETURN)
    time.sleep(2)

def scrape_category(driver, category_url):
    """Scrapes products with discounts > 50% from a given category."""
    driver.get(category_url)
    time.sleep(3)
    
    products = []
    for _ in range(30):  
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.zg-grid-general-faceout"))
            )
            
            product_elements = driver.find_elements(By.CSS_SELECTOR, "div.zg-grid-general-faceout")
            for product in product_elements:
                try:
                    title = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncate").text
                    price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                    discount_info = product.find_element(By.CSS_SELECTOR, ".s-savings-percent").text
                    discount_percent = int(discount_info.strip('%').strip())
                    
                    if discount_percent > 50:
                        products.append({
                            'Title': title,
                            'Price': price,
                            'Discount': discount_info
                        })
                except Exception as e:
                    continue
            
            # Go to the next page
            next_button = driver.find_element(By.CSS_SELECTOR, ".a-pagination .a-last a")
            if next_button:
                next_button.click()
                time.sleep(3)
            else:
                break
        except Exception as e:
            print(f"Error on page: {e}")
            break
    
    return products

def save_to_csv(data, filename):
    
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

def main():
    try:
        amazon_login(driver)
        
        # List of category URLs to scrape
        categories = [
            "https://www.amazon.com/Best-Sellers/zgbs/",
            "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
            "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
            "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0"
            
        ]
        
        all_products = []
        for category_url in categories:
            products = scrape_category(driver, category_url)
            all_products.extend(products)
            if len(all_products) > 1500:  # Limit to 1500 products
                break
        
        # Save results to a CSV file
        save_to_csv(all_products, "amazon_best_sellers.csv")
        print("Scraping completed. Data saved to 'amazon_best_sellers.csv'.")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()