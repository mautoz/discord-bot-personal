#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import random

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

def get_screenshots(links: list) -> None:
    for link in links:
        firefox_options = Options()
        firefox_options.headless = True
        firefox_options.add_argument(f'user-agent={USER_AGENT}')
        driver = webdriver.Firefox(options=firefox_options)
        driver.set_window_size(800, 600)
        driver.get(link)
        name = link.split('/')[-2]
        driver.save_screenshot(f"{name}.png")
        driver.quit()

        sleep_duration = random.uniform(60, 180)
        time.sleep(sleep_duration)