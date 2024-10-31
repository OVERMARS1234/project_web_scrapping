from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import pandas as pd
import time

# Initialisation du driver
driver = webdriver.Chrome()
url_base = "https://www.avito.ma/fr/maroc/appartements-%C3%A0_vendre"
data = {
    "Titre": [], "Localisation": [], "Prix": [], "Chambres": [], 
    "Salles de bain": [], "Surface": [], "Etage": [], "Type": [], 
    "Description": [], "Equipements": [], "Lien": []
}

def get_text(xpath):
    """Fonction pour extraire le texte en utilisant un XPath donné et gérer les erreurs."""
    try:
        return driver.find_element(By.XPATH, xpath).text
    except NoSuchElementException:
        return "N/A"

def scrape_annonce(lien):
    """Scraper une annonce d'appartement à partir de son lien."""
    driver.get(lien)
    time.sleep(2)  # Attente pour charger la page

    # Extraire les données de chaque annonce
    data["Titre"].append(get_text("//h1[@class='sc-1g3sn3w-12 jUtCZM']"))
    data["Localisation"].append(get_text("//span[@class='sc-1x0vz2r-0 iotEHk']"))
    data["Prix"].append(get_text("//p[@class='sc-1x0vz2r-0 lnEFFR sc-1g3sn3w-13 czygWQ']"))
    data["Chambres"].append(get_text("//div[@class='sc-6p5md9-2 bxrxrn'][1]//span[@class='sc-1x0vz2r-0 kQHNss']"))
    data["Salles de bain"].append(get_text("/html/body/div[1]/div/main/div/div[3]/div[1]/div[2]/div[1]/div[1]/div[2]/div[4]/div[1]/div[2]/div/span"))
    data["Surface"].append(get_text("//span[contains(text(), 'Surface')]/following-sibling::span"))
    data["Etage"].append(get_text("//span[contains(text(), 'Étage')]/following-sibling::span"))
    data["Type"].append(get_text("//span[contains(text(), 'Type')]/following-sibling::span"))
    data["Description"].append(get_text("//p[@class='sc-ij98yj-0 fAYGMO']"))
    # Pour les équipements, on utilise une liste pour stocker plusieurs valeurs si elles existent
    equipements = [equipement.text for equipement in driver.find_elements(By.XPATH, "//*[@class='sc-1x0vz2r-0 bXFCIH']")]
    data["Equipements"].append(", ".join(equipements) if equipements else "N/A")
    data["Lien"].append(lien)

def scrape_page(url):
    """Scraper les liens d'annonces d'une page de résultats."""
    driver.get(url)
    time.sleep(2)  # Attendre que la page de résultats se charge
    
    try:
        annonces = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//a[@class='sc-1jge648-0 eTbzNs']"))
        )
        
        # Collecter tous les liens des annonces
        liens_annonces = [annonce.get_attribute('href') for annonce in annonces]

        # Scraper chaque annonce individuellement
        for lien in liens_annonces:
            scrape_annonce(lien)
            time.sleep(2)  # Pause entre chaque annonce pour limiter les risques de blocage

    except TimeoutException:
        print("Timeout: La page de résultats a pris trop de temps à charger.")
    except StaleElementReferenceException:
        print("Erreur de référence obsolète.")

# Exécution principale
for page_num in range(1, 3):  # Scraper les deux premières pages par exemple
    scrape_page(f"{url_base}?o={page_num}")

# Conversion des données en DataFrame et export CSV
df = pd.DataFrame(data)
df.to_csv('avito.csv', encoding='utf-8', index=False)
print("Données sauvegardées dans avito.csv")

driver.quit()



