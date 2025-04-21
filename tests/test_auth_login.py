# import time
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException

# BASE_URL = "http://localhost:8000/api"  # ✅ Remove `/api` unless your login page is actually under /api

# def test_valid_login(driver):
#     driver.get(f"{BASE_URL}/login/")  # ✅ Confirm this path

#     # Fill in login form
#     driver.find_element(By.NAME, "username").send_keys("test-user1")
#     driver.find_element(By.NAME, "password").send_keys("test-user1")
#     driver.find_element(By.XPATH, "//button[text()='Login']").click()

#     # Optional: wait for page load (better to use WebDriverWait in real scenarios)
#     time.sleep(2)  # Use time.sleep() instead of implicitly_wait for a quick wait after form submission

#     # Debug: check for error message
#     try:
#         error = driver.find_element(By.XPATH, "//p[@style='color:red;']").text
#         print(f"Login failed: {error}")
#     except NoSuchElementException:
#         pass

#     # ✅ Final assertion
#     assert "Dashboard" in driver.page_source or "Welcome" in driver.page_source, \
#         f"Login likely failed — 'Dashboard' not found in page source.\nPage Source:\n{driver.page_source}"
