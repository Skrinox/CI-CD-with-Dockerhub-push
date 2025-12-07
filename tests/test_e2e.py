import os
import threading
import time

import pytest
import requests
from app import create_app, db
from selenium import webdriver
from selenium.webdriver.common.by import By


def wait_for_server(url, timeout=10):
    start  = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url)
            return True
        except Exception:
            time.sleep(0.1)
    raise TimeoutError(f"Server at {url} did not start in time.")


@pytest.fixture
def start_app():
    
    db_path = os.path.abspath("e2e_test.db")
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["SECRET_KEY"] = "e2e-test-secret"
    
    app = create_app()
    
    with app.app_context():
        db.drop_all()
        db.create_all()
    
    def run():
        app.run(port=5000, host="127.0.0.1", debug=False, use_reloader=False)
        
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()
    
    wait_for_server("http://127.0.0.1:5000")
    
    yield


@pytest.fixture
def driver(start_app):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

    
def register(driver, username="testuser", password="supersecurepwd"):
    
    driver.get("http://127.0.0.1:5000/register")
    
    driver.find_element("name", "username").send_keys(username)
    driver.find_element("name", "password").send_keys(password)
    driver.find_element("name", "confirm").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(0.3)

def login(driver, username="testuser", password="supersecurepwd"):
    register(driver, username, password)
    
    driver.get("http://127.0.0.1:5000/login")
    driver.find_element("name", "username").send_keys(username)
    driver.find_element("name", "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(0.3)

def test_register(driver):
    register(driver, "testuser", "supersecurepwd")
    assert "/login" in driver.current_url or "registration successful" in driver.page_source.lower()
 
    
def test_login(driver, username="testuser", password="supersecurepwd"):
    login(driver, username, password)
    assert "logged in successfully" in driver.page_source.lower()
    
    
def test_create_task(driver):

    login(driver, "testuser", "supersecurepwd")
    
    driver.get("http://127.0.0.1:5000/tasks/new")
    driver.find_element("name", "title").send_keys("e2e task")
    driver.find_element("name", "description").send_keys("end-to-end test task")
    
    date_input = driver.find_element("name", "due_date")
    driver.execute_script("arguments[0].value = '2025-12-07';", date_input)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(0.3)
    
    assert "e2e task" in driver.page_source
   
    
def test_toggle_task(driver):
    
    login(driver, "testuser", "supersecurepwd")
    
    driver.get("http://127.0.0.1:5000/tasks/new")
    driver.find_element("name", "title").send_keys("Task to Toggle")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(0.3)
    
    driver.get("http://127.0.0.1:5000/")
    toggle_buttons = driver.find_elements(By.CSS_SELECTOR, "form[action*='toggle'] button")
    assert len(toggle_buttons) > 0, "toggle buttons not found"
    toggle_buttons[0].click()
    time.sleep(0.3)
    
    assert "status updated" in driver.page_source.lower() or "updated" in driver.page_source.lower()
    
    