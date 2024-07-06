import datetime
import json
import http.client
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Přihlašovací údaje
username = "josef.rajmon@as4u.cz"
password = "{@7BF41e54@}"

# ID příjemce
recipient_id = "7946839892062226"
while True:
    conn = http.client.HTTPSConnection("epic-free-games1.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "2f174ac7femsh0e6b8bf1083c77ep16ca63jsn8194061d3ac3",
        'x-rapidapi-host': "epic-free-games1.p.rapidapi.com"
    }

    conn.request("GET", "/currentGames", headers=headers)

    res = conn.getresponse()
    data = res.read()

    # Převedení dat na datetime objekty a nalezení nejnižšího data ukončení
    end_dates = [datetime.datetime.fromisoformat(item['offerEndDate'].replace('Z', '+00:00')) for item in json.loads(data.decode("utf-8"))]
    min_end_date = min(end_dates)

    # Kontrola, zda již bylo nejnižší datum ukončení při spuštění skriptu
    try:
        with open('min_end_date.txt', 'r') as file:
            saved_min_end_date = datetime.datetime.fromisoformat(file.read().strip()).replace(tzinfo=datetime.timezone.utc)
    except FileNotFoundError:
        saved_min_end_date = datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)

    if datetime.datetime.now(datetime.timezone.utc) > saved_min_end_date and min_end_date != saved_min_end_date:
        # Uložení nejnižšího data ukončení do souboru
        with open('min_end_date.txt', 'w') as file:
            file.write(str(min_end_date))

        titles = [item['title'] for item in json.loads(data.decode("utf-8"))]
        titles_string = '/n <br> '.join(titles)

        # Inicializuj webový prohlížeč
        driver = webdriver.Chrome()
        driver.get("https://www.facebook.com/")

        # Zadej přihlašovací údaje a přihlas se
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "pass")
        email_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)

        # Přejdi na stránku chatu
        time.sleep(5)
        driver.get(f"https://www.facebook.com/messages/t/{recipient_id}")
        time.sleep(10) # Počkej 10 sekund, aby se stránka načetla

        # Odešli zprávu
        chat_input = driver.find_element(By.CSS_SELECTOR, "div[aria-label='Zpráva'][contenteditable='true']")
        chat_input.send_keys(titles_string)
        chat_input.send_keys(Keys.RETURN)
        time.sleep(50)

        # Zavři webový prohlížeč
        driver.quit()

        time.sleep(60)
