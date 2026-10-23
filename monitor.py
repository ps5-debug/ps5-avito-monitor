import os, re, json, time, hashlib
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
SEARCH_URL = os.environ.get(
    "SEARCH_URL",
    "https://www.avito.ru/moskva/igry_pristavki_i_programmy/igry_pristavki_i_programmy/igrovye_pristavki/sony/sony_playstation_5-ASgBAgICBESSAsoJsvoN4o6TAbb6DY6OkwH0zRSayo8D"
)
STATE_PATH = "seen.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; PS5Monitor/1.0)",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}

def send_telegram(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": False},
        timeout=20,
    )
    r.raise_for_status()
    data = r.json()
    if not data.get("ok"):
        raise RuntimeError("Telegram API не принял сообщение")

def load_seen():
    try:
        with open(STATE_PATH, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def parse_listings(html):
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    # Avito's markup can change. Only use links that look like listing URLs.
    for a in soup.select("a[href]"):
        href = a.get("href", "")
        title = " ".join(a.get_text(" ", strip=True).split())
        if not title or not href:
            continue
        if "/items/" not in href and not re.search(r"_\d{8,}(?:\?|$)", href):
            continue
        low = title.lower()
        if not (("playstation" in low and "5" in low) or "ps5" in low or ("плейстейшн" in low and "5" in low)):
            continue
        full_url = urljoin("https://www.avito.ru", href.split("?")[0])
        m = re.search(r"_(\d{8,})$", full_url)
        key = m.group(1) if m else hashlib.sha1(full_url.encode()).hexdigest()[:16]
        # Try to find price in nearby card text.
        parent = a
        for _ in range(4):
            if parent.parent:
                parent = parent.parent
        card_text = " ".join(parent.get_text(" ", strip=True).split())[:800]
        pm = re.search(r"([\d\s\u00a0]+)\s*₽", card_text)
        price = re.sub(r"\s+", " ", pm.group(0)).strip() if pm else "Цена не распознана"
        results[key] = {"title": title[:250], "url": full_url, "price": price}
    return results

def main():
    r = requests.get(SEARCH_URL, headers=HEADERS, timeout=25)
    if r.status_code in (403, 429):
        raise RuntimeError(f"Авито ответил HTTP {r.status_code}; возможно, запросы ограничены.")
    r.raise_for_status()
    items = parse_listings(r.text)
    if not items:
        raise RuntimeError("Не удалось извлечь объявления из страницы. Возможно, изменилась разметка или показана антибот-защита.")
    seen = load_seen()
    new = [(k, v) for k, v in items.items() if k not in seen]
    if not os.path.exists(STATE_PATH):
        # First run only records current listings, avoiding a flood of old ads.
        with open(STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(sorted(items.keys()), f)
        print(f"Первый запуск: сохранено {len(items)} существующих объявлений; уведомления не отправлялись.")
        return
    for key, item in new:
        send_telegram("🆕 Возможное новое объявление PS5\n"
                      f"{item['title']}\nЦена: {item['price']}\n{item['url']}")
        seen.add(key)
        time.sleep(1)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(sorted(seen), f)
    print(f"Объявлений на странице: {len(items)}; новых: {len(new)}")

if __name__ == "__main__":
    main()
