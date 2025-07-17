"""Command line interface to interact with ChatGPT via a browser.

This script starts Chrome in incognito mode so that no browsing data
or credentials are persisted. It prints responses to the terminal only
and stores no conversation history.

Licensed under the Apache License, Version 2.0. See the LICENSE file
for details.
"""

import time
from typing import Optional, List
import os
import tempfile
import requests

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".telegram_token")
import argparse
import os
import time

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rich.console import Console
from rich.text import Text
import pyperclip
from PIL import ImageGrab, Image

console = Console()


def cargar_token() -> Optional[str]:
    """Return the Telegram bot token from env or a local file."""
    token = os.getenv("TELEGRAM_TOKEN")
    if token:
        return token.strip()
    if os.path.isfile(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            console.print(f"[WARN] No se pudo leer {TOKEN_FILE}: {e}")
    return None


def enviar_telegram(token: str, chat_id: str, mensaje: str) -> None:
    """Send a message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": mensaje})
    except Exception as e:
        console.print(f"[WARN] No se pudo enviar a Telegram: {e}")

def get_args():
    """Return parsed command-line arguments."""
    parser = argparse.ArgumentParser(description="Interact with ChatGPT from the terminal")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome in headless mode"
    )
    parser.add_argument(
        "--save-file",
        type=str,
        help="Optional path to save the conversation"
    )
    return parser.parse_args()


def iniciar_navegador(headless: bool = False):
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--no-first-run --no-service-autorun --password-store=basic")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("--disable-notifications")
    if headless:
        options.add_argument("--headless=new")
    driver = uc.Chrome(options=options, use_subprocess=True)
    driver.get("https://chatgpt.com")
    return driver


def configurar() -> tuple[bool, Optional[str], Optional[str], bool, Optional[str], Optional[str]]:
    """Interactively ask the user how to start the session."""
    head = input("¿Ejecutar en modo headless? (s/N): ").strip().lower() == "s"
    save_file: Optional[str] = None
    if input("¿Guardar la conversación en un archivo? (s/N): ").strip().lower() == "s":
        save_file = input("Ruta del archivo: ").strip() or None
    prompts_file: Optional[str] = None
    if input("¿Cargar preguntas desde un archivo? (s/N): ").strip().lower() == "s":
        prompts_file = input("Ruta del archivo de preguntas: ").strip() or None
    notificar = input("¿Enviar respuestas por Telegram? (s/N): ").strip().lower() == "s"
    chat_id: Optional[str] = None
    token: Optional[str] = None
    if notificar:
        chat_id = input("Chat ID de Telegram: ").strip() or None
        token = cargar_token()
        if not token:
            token = input("Token del bot de Telegram: ").strip() or None
    return head, save_file, prompts_file, notificar, chat_id, token

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

def imprimir_respuesta(texto: str) -> None:
    """Pretty print a response using rich."""
    rich_text = Text(texto)
    console.print(rich_text)

def mostrar_historia(history):
    for i, (q, r) in enumerate(history, 1):
        console.print(f"{i}. Q: {q}\n   A: {r}\n")


def cargar_prompts(ruta: str) -> List[str]:
    """Load prompts from a file if provided."""
    try:
        with open(ruta, encoding="utf-8") as f:
            return [l.strip() for l in f if l.strip()]
    except Exception as e:
        console.print(f"[WARN] No se pudieron cargar las preguntas: {e}")
        return []


def exportar_historia(history: List[tuple[str, str]], ruta: str) -> None:
    """Save the conversation to a Markdown file."""
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("# Conversación\n\n")
        for q, r in history:
            f.write(f"## Q: {q}\n{r}\n\n")


def buscar_en_historia(history: List[tuple[str, str]], termino: str) -> List[tuple[str, str]]:
    """Return all entries that match the search term."""
    t = termino.lower()
    return [(q, r) for q, r in history if t in q.lower() or t in r.lower()]


def copiar_historia(history: List[tuple[str, str]]) -> None:
    """Copy the whole history to the clipboard."""
    texto = "\n\n".join(f"Q: {q}\nA: {r}" for q, r in history)
    if texto:
        pyperclip.copy(texto)
        print("[INFO] Historial copiado al portapapeles.")
    else:
        print("[WARN] No hay historial para copiar.")


def obtener_imagen_clipboard() -> Optional[str]:
    """Save an image from the clipboard to a temporary file and return the path."""
    try:
        img = ImageGrab.grabclipboard()
    except Exception as e:
        console.print(f"[WARN] No se pudo acceder al portapapeles: {e}")
        return None
    if not isinstance(img, Image.Image):
        console.print("[WARN] No hay una imagen en el portapapeles.")
        return None
    ruta = os.path.join(tempfile.gettempdir(), "gpt_clipboard.png")
    img.save(ruta, "PNG")
    return ruta


def enviar_imagen_clipboard(driver) -> str:
    """Upload an image from the clipboard to ChatGPT."""
    ruta = obtener_imagen_clipboard()
    if not ruta:
        return "[Sin imagen]"
    try:
        wait = WebDriverWait(driver, 60)
        caja = wait.until(EC.element_to_be_clickable((By.ID, "prompt-textarea")))
        attach = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
        attach.send_keys(ruta)
        caja.send_keys(Keys.RETURN)
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.markdown")))
        time.sleep(2)
        respuestas = driver.find_elements(By.CSS_SELECTOR, "div.markdown")
        return respuestas[-1].text.strip() if respuestas else "[Sin respuesta]"
    except Exception as e:
        return f"[ERROR] {e}"
    finally:
        if os.path.exists(ruta):
            os.remove(ruta)


def main():
    headless, save_file, prompts_path, notif_tel, chat_id, token = configurar()
    driver = iniciar_navegador(headless)
    history: List[tuple[str, str]] = []

    prompts: List[str] = cargar_prompts(prompts_path) if prompts_path else []
    args = get_args()
    driver = iniciar_navegador(args.headless)
    history = []

    print("[INFO] Si ves login o captcha, resuélvelo en el navegador.")
    input("[MANUAL] Pulsa ENTER cuando puedas escribir en el prompt...\n")

    for pregunta in prompts:
        start = time.time()
        respuesta = enviar_pregunta(driver, pregunta)
        dur = time.time() - start
        print("\n--- CMD response ---\n")
        imprimir_respuesta(respuesta)
        print(f"\n[INFO] Tiempo de respuesta: {dur:.1f}s\n----XXXX----\n")
        history.append((pregunta, respuesta))
        if notif_tel and chat_id and token:
            enviar_telegram(token, chat_id, respuesta)
        if save_file:
            with open(save_file, "a", encoding="utf-8") as f:
                f.write(f"Q: {pregunta}\nA: {respuesta}\n\n")

    try:
        while True:
            print(
                "\nMenú:\n"
                "1. Preguntar\n"
                "2. Ver historia\n"
                "3. Borrar historia\n"
                "4. Copiar última respuesta\n"
                "5. Copiar historial\n"
                "6. Buscar en historia\n"
                "7. Exportar historia\n"
                "8. Enviar imagen del portapapeles\n"
                "9. Salir"
            )
            opcion = input("Selecciona opción: ").strip()

            if opcion == "9":
                break
            elif opcion == "2":
                mostrar_historia(history)
                continue
            elif opcion == "3":
                history.clear()
                if save_file:
                    open(save_file, "w").close()
                print("[INFO] Historia borrada.")
                continue
            elif opcion == "4":
                if history:
                    pyperclip.copy(history[-1][1])
                    print("[INFO] Última respuesta copiada al portapapeles.")
                else:
                    print("[WARN] No hay respuestas para copiar.")
                continue
            elif opcion == "5":
                copiar_historia(history)
                continue
            elif opcion == "6":
                termino = input("Término a buscar: ").strip()
                for q, r in buscar_en_historia(history, termino):
                    console.print(f"Q: {q}\nA: {r}\n")
                continue
            elif opcion == "7":
                ruta = input("Archivo destino: ").strip()
                if ruta:
                    exportar_historia(history, ruta)
                    print(f"[INFO] Historial exportado a {ruta}.")
                else:
                    print("[WARN] Ruta no válida.")
                continue
            elif opcion == "8":
                start = time.time()
                respuesta = enviar_imagen_clipboard(driver)
                dur = time.time() - start
                imprimir_respuesta(respuesta)
                history.append(("[Imagen]", respuesta))
                if notif_tel and chat_id and token:
                    enviar_telegram(token, chat_id, respuesta)
                if save_file:
                    with open(save_file, "a", encoding="utf-8") as f:
                        f.write(f"Imagen enviada\nA: {respuesta}\n\n")
                continue
            elif opcion != "1":
                print("[WARN] Opción no reconocida.")
                continue

            pregunta = input("Escribe tu pregunta: ").strip()
            if not pregunta:
    try:
        while True:
            pregunta = input(">> Pregunta ('salir' o 'historia'): ").strip()

            if pregunta.lower() == "salir":
                break

            if pregunta.lower() == "historia":
                for i, (q, r) in enumerate(history, 1):
                    console.print(f"{i}. Q: {q}\n   A: {r}\n")
                continue

            start = time.time()
            respuesta = enviar_pregunta(driver, pregunta)
            dur = time.time() - start

            print("\n--- CMD response ---\n")
            imprimir_respuesta(respuesta)
            print(f"\n[INFO] Tiempo de respuesta: {dur:.1f}s\n----XXXX----\n")

            history.append((pregunta, respuesta))
            if notif_tel and chat_id and token:
                enviar_telegram(token, chat_id, respuesta)

            if save_file:
                with open(save_file, "a", encoding="utf-8") as f:


            if args.save_file:
                with open(args.save_file, "a", encoding="utf-8") as f:
                    f.write(f"Q: {pregunta}\nA: {respuesta}\n\n")
    except KeyboardInterrupt:
        print("\n[INFO] Sesión interrumpida por el usuario.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
