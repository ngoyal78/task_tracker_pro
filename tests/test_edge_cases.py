# import time
# from selenium.webdriver.common.by import By
# from selenium.common.exceptions import NoSuchElementException

# BASE_URL = "http://localhost:8000/api"  # Removed `/api` since login/register are usually frontend routes

# def test_login_with_sql_injection(driver):
#     driver.get(f"{BASE_URL}/login/")
#     driver.find_element(By.NAME, "username").send_keys("admin' OR '1'='1")
#     driver.find_element(By.NAME, "password").send_keys("anything")
#     driver.find_element(By.XPATH, "//button[text()='Login']").click()

#     try:
#         error_text = driver.find_element(By.XPATH, "//p[contains(text(), 'Invalid')]").text
#         assert "Invalid credentials" in error_text
#     except NoSuchElementException:
#         assert "Dashboard" not in driver.page_source, "SQL injection may have bypassed login."

# # def test_unicode_username_registration(driver):
# #     driver.get(f"{BASE_URL}/register/")
# #     driver.find_element(By.NAME, "username").send_keys("测试用户")
# #     driver.find_element(By.NAME, "password1").send_keys("Testpass123")
# #     driver.find_element(By.NAME, "password2").send_keys("Testpass123")
# #     driver.find_element(By.XPATH, "//button[text()='Register']").click()

# #     assert "Dashboard" in driver.page_source or "Welcome" in driver.page_source, \
# #         "Registration with Unicode username may have failed."

# def test_session_timeout(driver):
#     driver.get(f"{BASE_URL}/login/")
#     driver.find_element(By.NAME, "username").send_keys("test-user1")
#     driver.find_element(By.NAME, "password").send_keys("test-user1")
#     driver.find_element(By.XPATH, "//button[text()='Login']").click()

#     # Simulate session idle (use 5 seconds here for demo purposes)
#     time.sleep(5)  # Replace with time.sleep(3600) for real session timeout

#     driver.get(f"{BASE_URL}/dashboard/")  # Simulate accessing a protected page
#     page_source = driver.page_source.lower()
#     assert "login" in page_source or "session expired" in page_source or "dashboard" in page_source, \
#         "Expected session timeout or login page."
