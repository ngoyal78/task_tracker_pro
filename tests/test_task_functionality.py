import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_task_creation(driver, live_server, create_users, create_category, login):
    print(f"3 Live server running at: {live_server.url}")
    admin, user1, _ = create_users
    login("admin", "adminpass")
    driver.get(f"{live_server.url}/api/task/create/")

    # Wait until the title input is present in the DOM and visible
    wait = WebDriverWait(driver, 10)
    title_input = wait.until(EC.presence_of_element_located((By.NAME, "title")))
    title_input.send_keys("Fix Login Bug")
    # driver.find_element(By.NAME, "title").send_keys("Fix Login Bug")
    driver.find_element(By.NAME, "description").send_keys("User unable to log in with correct creds.")
    driver.find_element(By.NAME, "priority").send_keys("High")
    driver.find_element(By.NAME, "due_date").send_keys("2025-05-01")
    driver.find_element(By.NAME, "status").send_keys("Not Started")
    driver.find_element(By.NAME, "category").send_keys("Bug")

    # Wait until the multi-select is visible and interactable
    wait = WebDriverWait(driver, 10)
    assigned_select_element = wait.until(EC.presence_of_element_located((By.NAME, "assigned_to")))

    # Scroll into view just in case
    driver.execute_script("arguments[0].scrollIntoView(true);", assigned_select_element)
    # Use Select to interact with multi-select field
    assigned_select = Select(assigned_select_element)
    assigned_select.select_by_visible_text("user1")  # Select user1
    assigned_select.select_by_visible_text("user2")  # You can select multiple like this

    try:
        submit_button = driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]')
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        submit_button.click()
    except Exception:
        driver.execute_script("arguments[0].click();", submit_button)
    # submit_button = driver.find_element(By.CSS_SELECTOR, 'form button[type="submit"]')
    # driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
    # submit_button.click()
    # driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]").click()
    assert "Fix Login Bug" in driver.page_source


def test_task_assignment_and_view(driver, live_server, create_users, create_category, login):
    admin, user1, _ = create_users
    login("user1", "userpass1")

    driver.get(f"{live_server.url}/api/dashboard/")
    # assert "Fix Login Bug" in driver.page_source

    # driver.find_element(By.LINK_TEXT, "Fix Login Bug").click()
    # assert "User unable to log in" in driver.page_source
    # Wait for the table to render and check the task is listed
    WebDriverWait(driver, 10).until(
        EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Fix Login Bug")
    )
    assert "Fix Login Bug" in driver.page_source

    # Click the 'View' button (not link text — it's a button inside <a>)
    view_buttons = driver.find_elements(By.LINK_TEXT, "View")
    assert view_buttons, "No 'View' button found for assigned task"
    view_buttons[0].click()

    # Wait and verify the task detail view is loaded
    # WebDriverWait(driver, 10).until(
    #     EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Your Assigned Tasks")
    # )
    assert "Your Assigned Tasks" in driver.page_source


# def test_task_editing(driver, live_server, create_users, create_category, login):
#     admin, user1, _ = create_users
#     login("admin", "adminpass")

#     driver.get(f"{live_server.url}/tasks/")
#     driver.find_element(By.LINK_TEXT, "Fix Login Bug").click()

#     driver.find_element(By.LINK_TEXT, "Edit Task").click()
#     desc = driver.find_element(By.NAME, "description")
#     desc.clear()
#     desc.send_keys("Issue occurs after password reset.")
#     driver.find_element(By.XPATH, "//button[text()='Save']").click()

#     assert "Issue occurs after password reset." in driver.page_source

# def test_role_based_control(driver, live_server, create_users, create_category, login):
#     admin, user1, user2 = create_users
#     login("user2", "userpass2")

#     driver.get(f"{live_server.url}/task/2")
#     assert "Fix Login Bug" not in driver.page_source  # Task not assigned to user2