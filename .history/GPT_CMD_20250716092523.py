import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.console import Console
from rich.text import Text
import time

console = Console()

def iniciar_navegador():
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options, use_subprocess=True)
    driver.get("https://chatgpt.com")
    return driver

def enviar_pregunta(driver, pregunta):
    try:
        wait = WebDriverWait(driver, 60)
        caja = wait.until(EC.element_to_be_clickable((By.ID, "prompt-textarea")))
        caja.click()
        caja.send_keys(pregunta)
        caja.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.markdown")))
        time.sleep(2)

        respuestas = driver.find_elements(By.CSS_SELECTOR, "div.markdown")
        return respuestas[-1].text.strip() if respuestas else "[Sin respuesta]"
    except Exception as e:
        return f"[ERROR] {e}"

def imprimir_respuesta(texto):
    rich_text = Text(texto)
    console.print(rich_text)

def main():
    driver = iniciar_navegador()
    print("[INFO] Si ves login o captcha, resuélvelo en el navegador.")
    input("[MANUAL] Pulsa ENTER cuando puedas escribir en el prompt...\n")

    while True:
        pregunta = input(">> Pregunta ('salir' para terminar): ").strip()
        if pregunta.lower() == "salir":
            break

        respuesta = enviar_pregunta(driver, pregunta)
        print("\n--- CMD response ---\n")
        imprimir_respuesta(respuesta)
        print("\n----XXXX----\n")

    driver.quit()

if __name__ == "__main__":
    main()
