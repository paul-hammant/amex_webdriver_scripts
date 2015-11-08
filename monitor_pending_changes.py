from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import sys

# WebDriver has not element.remove() function, so it has to be hacked
# -------------------------------------------------------------------
def kill_element(element):
    driver.execute_script("""
        var element = arguments[0];
        element.parentNode.removeChild(element);
        """, element)

driver = webdriver.Firefox()

# Get to the Pending statements and activity page
# -----------------------------------------------
driver.get("https://www.americanexpress.com")
driver.set_window_size(1400, 3500)

driver.find_element_by_id("Username").send_keys(sys.argv[1])
driver.find_element_by_id("Password").send_keys(sys.argv[2])
driver.find_element_by_id("loginLink").click()
driver.find_element_by_id("MYCA_PC_Statements2").click()
WebDriverWait(driver, 3).until(lambda driver : driver.find_element_by_id("pendingHdr")).click()

# Create a bunch of space so that ElementNotVisibleException doesn't happen quite as much.
# ----------------------------------------------------------------------------------------
try:
    WebDriverWait(driver, 3).until(lambda driver : driver.find_element_by_id("graphContainerClose")).click()
except NoSuchElementException:
    pass
except ElementNotVisibleException:
    pass
elems_to_delete = ["pendinghelp-tbody","tbllinks","proc_total","iNavMainContainer","iNavWrapper","cmSnapshot","footer", ".toolbar-wrapper.AXP_iNSlide"]
for to_delete in elems_to_delete:
    try:
        kill_element(WebDriverWait(driver, 2).until(lambda driver : driver.find_element_by_id(to_delete)))
    except TimeoutException:
        try:
            kill_element(driver.find_element_by_css_selector(to_delete))
        except NoSuchElementException:
            print "Element not removed: " + to_delete + " - not found"
    except ElementNotVisibleException:
        print "Element not removed: " + to_delete + " - not visible"

# Loop though pending payments clicking the "mark for monitoring" widget if it is not already set
# -----------------------------------------------------------------------------------------------
tds = WebDriverWait(driver, 3).until(lambda driver : driver.find_elements_by_xpath("//table[@id='listData']/tbody[contains(@class,'pending-trans')]/tr/td[contains(@class,'colDesc')]"))
for ix, td in enumerate(tds):
    attribute = td.click()
    try:
        WebDriverWait(driver, 3).until(lambda driver : driver.find_element_by_id("unMarked_" + str(ix))).click()
        WebDriverWait(driver, 3).until(lambda driver : driver.find_element_by_id("markCharge_" + str(ix))).click()
        print "Charge " + str(ix) + " marked for monitoring "
    except NoSuchElementException:
        pass
    except ElementNotVisibleException:
        pass
    td.click() # close that flyout again
    kill_element(td.find_element_by_xpath("..")) # create more space towards the top of the viewport

driver.close()