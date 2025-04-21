import os
import django

# Set environment variable to your settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task_tracker_pro.settings')

# Setup Django before importing models
django.setup()

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from django.contrib.auth.models import User
from tracker.models import Category, Task

@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()

@pytest.fixture
def create_users(db):
    # print(f"1 Live server running at: {live_server.url}")
    admin = User.objects.create_superuser(username='admin', email='admin@test.com', password='adminpass')
    user1 = User.objects.create_user(username='user1', password='userpass1')
    user2 = User.objects.create_user(username='user2', password='userpass2')
    return admin, user1, user2

@pytest.fixture
def create_category(db):
    return Category.objects.create(name="Bug")

@pytest.fixture
def login(driver, live_server):
    def _login(username, password):
        # print(f"2 Live server running at: {live_server.url}")
        driver.get(f"{live_server.url}/api/login/")
        driver.find_element("name", "username").send_keys(username)
        driver.find_element("name", "password").send_keys(password)
        driver.find_element("xpath", "//button[text()='Login']").click()
    return _login
