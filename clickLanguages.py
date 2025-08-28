from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome()

driver.get("https://translate.google.com/?hl=es&sl=auto&tl=es&op=images")

# Click "Detectar idioma"
driver.find_element(By.ID, "i58").click()

sleep(2)

# Click "Inglés"
driver.find_element(By.ID, "i59").click()

sleep(2)
# Click "Español"
driver.find_element(By.ID, "i60").click()

sleep(2)
# Click "Francés"
driver.find_element(By.ID, "i61").click()

