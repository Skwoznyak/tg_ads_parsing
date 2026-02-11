from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import pickle
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import shutil
import os
import re


def check_browser_availability():
    """Проверяет доступность браузеров в системе"""
    browsers = {
        'chrome': False,
        'firefox': False
    }

    # Проверяем Chrome/Chromium
    chrome_paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "chromium",
        "google-chrome"
    ]

    for path in chrome_paths:
        if shutil.which(path):
            browsers['chrome'] = True
            print(f"✅ Найден Chrome/Chromium: {path}")
            break

    # Проверяем Firefox
    firefox_paths = ["firefox", "/usr/bin/firefox"]
    for path in firefox_paths:
        if shutil.which(path):
            browsers['firefox'] = True
            print(f"✅ Найден Firefox: {path}")
            break

    return browsers


def create_firefox_driver():
    """Создает драйвер с автоматическим выбором браузера (Chrome -> Firefox)"""

    print("🔍 Проверяю доступность браузеров...")
    browsers = check_browser_availability()

    # Сначала пробуем Chrome, если он доступен
    if browsers['chrome']:
        print("🚀 Пробую создать Chrome драйвер...")
        try:
            chrome_options = ChromeOptions()

            # Основные опции для headless режима
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-software-rasterizer")

            # User agent
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            # Для работы в Docker
            chrome_options.add_argument("--disable-setuid-sandbox")
            chrome_options.add_argument("--single-process")

            # Пробуем разные пути к Chrome/Chromium
            chrome_paths = [
                "/usr/bin/chromium",
                "/usr/bin/chromium-browser",
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable"
            ]

            driver = None
            for chrome_path in chrome_paths:
                try:
                    chrome_options.binary_location = chrome_path
                    driver = webdriver.Chrome(options=chrome_options)
                    print(
                        f"✅ Chrome драйвер успешно создан с путем: {chrome_path}")
                    return driver
                except Exception as e:
                    print(
                        f"⚠️ Не удалось создать Chrome с путем {chrome_path}: {e}")
                    continue

            # Если не удалось создать Chrome, пробуем без указания пути
            try:
                chrome_options.binary_location = None
                driver = webdriver.Chrome(options=chrome_options)
                print("✅ Chrome драйвер успешно создан (автоопределение пути)")
                return driver
            except Exception as e:
                print(f"❌ Chrome драйвер недоступен: {e}")

        except Exception as e:
            print(f"❌ Ошибка при настройке Chrome: {e}")
    else:
        print("⚠️ Chrome/Chromium не найден в системе")

    # Fallback на Firefox
    if browsers['firefox']:
        print("🔄 Переключаюсь на Firefox...")
        try:
            firefox_options = Options()
            firefox_options.add_argument("--headless")
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--disable-dev-shm-usage")

            # User agent для Firefox
            firefox_options.set_preference("general.useragent.override",
                                           "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")

            driver = webdriver.Firefox(options=firefox_options)
            print("✅ Firefox драйвер успешно создан")
            return driver

        except Exception as e:
            print(f"❌ Ошибка при создании Firefox драйвера: {e}")
    else:
        print("❌ Firefox не найден в системе")

    print("❌ Не удалось создать ни один драйвер. Убедитесь, что установлен Chrome/Chromium или Firefox")
    return None


def phone_register_send(phone_num):
    driver = create_firefox_driver()
    if not driver:
        print("Не удалось создать Firefox драйвер")
        return

    driver.get("https://ads.telegram.org")

    pole_phone = driver.find_element(By.CSS_SELECTOR, ".btn.pr-btn.login-link")
    pole_phone.click()

    phone = phone_num
    vvod = driver.find_element(
        By.CSS_SELECTOR, '.form-control.pr-form-control.input-lg')
    vvod.send_keys(phone)

    send_sms = driver.find_element(
        By.XPATH, "//button[@type='submit' and contains(@class, 'btn') and contains(text(), 'Next')]")
    send_sms.click()

    time.sleep(30)

    save_cookies(driver)
    try:
        driver.quit()
    except Exception as e:
        print(f"Ошибка при закрытии браузера: {e}")


def save_cookies(driver, filename="cookies_user.pkl"):
    cookies = driver.get_cookies()

    with open(filename, 'wb') as f:
        pickle.dump(cookies, f)

    print(f"Куки сохранены: {len(cookies)} штук")


def load_cookies(driver, filename="cookies_user.pkl"):
    try:
        with open(filename, 'rb') as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            driver.add_cookie(cookie)

        print(f"Куки загружены: {len(cookies)} штук")
        return True
    except FileNotFoundError:
        print("Файл с куки не найден")
        return False


def is_authorized(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, ".pr-account-button-content")
        return True
    except:
        return False


def login_with_cookies():
    driver = create_firefox_driver()
    if not driver:
        print("Не удалось создать Firefox драйвер")
        return None

    driver.get("https://ads.telegram.org")

    if load_cookies(driver):
        driver.refresh()

        if is_authorized(driver):
            print("Успешный вход через куки!")
            return driver
        else:
            print("Куки устарели, нужна повторная авторизация")
            driver.quit()
            return None
    else:
        print("Файл с куками не найден")
        driver.quit()
        return None


def find_channel_by_name(driver, channel_name):
    try:
        channel_elem = driver.find_element(
            By.XPATH, f"//div[@class='pr-account-button-title' and contains(text(), '{channel_name}')]")
        print(f'канал {channel_name} нашелся!')
        return channel_elem
    except:
        print(f"Канал '{channel_name}' не найден")
        return None


def _safe_text(elem):
    """Возвращает текст элемента, если он есть, иначе пустую строку."""
    try:
        if elem is None:
            return ""
        return elem.text.strip()
    except Exception:
        return ""


def format_date_added(date_string):
    """
    Форматирует дату в формат месяц/день/год время
    Пример: 2/18/25 15:29
    """
    if not date_string or date_string.strip() == "":
        return ""

    try:
        # Убираем лишние пробелы
        date_string = date_string.strip()
        # print(f"[ФОРМАТИРОВАНИЕ ДАТЫ] 🔍 Обрабатываю дату: '{date_string}'")

        # Пробуем разные форматы даты, которые могут прийти из Telegram Ads
        date_formats = [
            # 2 May 24 17:25 (ПЕРВЫЙ ПРИОРИТЕТ - РЕАЛЬНЫЙ ФОРМАТ)
            "%d %b %y %H:%M",
            "%d %b %Y %H:%M",      # 2 May 2024 17:25
            "%d %B %y %H:%M",      # 2 May 24 17:25
            "%d %B %Y %H:%M",      # 2 May 2024 17:25
            "%d %b %y",            # 27 Feb 25
            "%d %b %Y",            # 27 Feb 2025
            "%d %B %y",            # 27 February 25
            "%d %B %Y",            # 27 February 2025
            "%Y-%m-%d %H:%M",      # 2025-02-18 15:29
            "%d.%m.%Y %H:%M",      # 18.02.2025 15:29
            "%d/%m/%Y %H:%M",      # 18/02/2025 15:29
            "%m/%d/%Y %H:%M",      # 02/18/2025 15:29
            "%Y-%m-%d",            # 2025-02-18
            "%d.%m.%Y",            # 18.02.2025
            "%d/%m/%Y",            # 18/02/2025
            "%m/%d/%Y",            # 02/18/2025
        ]

        parsed_date = None
        for fmt in date_formats:
            try:
                # print(f"[ФОРМАТИРОВАНИЕ ДАТЫ] 🔍 Пробую формат: {fmt}")
                parsed_date = datetime.strptime(date_string, fmt)
                # print(f"[ФОРМАТИРОВАНИЕ ДАТЫ] ✅ Успешно распарсил с форматом: {fmt}")
                break
            except ValueError as e:
                # print(f"[ФОРМАТИРОВАНИЕ ДАТЫ] ❌ Формат {fmt} не подошел: {e}")
                continue

        if parsed_date is None:
            # Если не удалось распарсить, возвращаем исходную строку
            # print(f"[ФОРМАТИРОВАНИЕ ДАТЫ] ⚠️ Не удалось распарсить дату '{date_string}', возвращаю исходную")
            return date_string

        # Форматируем в нужный формат: месяц/день/год время (без ведущих нулей)
        # Используем совместимый с Windows подход
        month = parsed_date.month
        day = parsed_date.day
        year = parsed_date.strftime("%y")
        time = parsed_date.strftime("%H:%M")
        result = f"{month}/{day}/{year} {time}"
        # print(f"[ФОРМАТИРОВАНИЕ ДАТЫ] ✅ Результат: '{date_string}' -> '{result}'")
        return result

    except Exception as e:
        print(
            f"[ФОРМАТИРОВАНИЕ ДАТЫ] ⚠️ Ошибка при форматировании даты '{date_string}': {e}")
        return date_string


def safe_checkbox_interaction(driver, checkbox_name, should_be_selected):
    """
    Безопасное взаимодействие с чекбоксом с несколькими попытками
    """
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            print(
                f"[НАСТРОЙКА ТАБЛИЦЫ] 🔄 Попытка {attempt + 1}/{max_attempts} для чекбокса: {checkbox_name}")

            # Находим чекбокс
            checkbox = driver.find_element(
                By.CSS_SELECTOR, f"input[name='{checkbox_name}']")

            # Прокручиваем элемент в видимую область
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
            time.sleep(0.5)

            # Проверяем текущее состояние
            is_selected = checkbox.is_selected()

            if should_be_selected and not is_selected:
                print(
                    f"[НАСТРОЙКА ТАБЛИЦЫ] ✅ Включаю чекбокс: {checkbox_name}")
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(0.3)
            elif not should_be_selected and is_selected:
                print(
                    f"[НАСТРОЙКА ТАБЛИЦЫ] 🔄 Отключаю чекбокс: {checkbox_name}")
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(0.3)
            else:
                print(
                    f"[НАСТРОЙКА ТАБЛИЦЫ] ✅ Чекбокс {checkbox_name} уже в нужном состоянии")

            return True

        except Exception as e:
            print(
                f"[НАСТРОЙКА ТАБЛИЦЫ] ⚠️ Попытка {attempt + 1} не удалась для {checkbox_name}: {e}")
            if attempt < max_attempts - 1:
                time.sleep(1)  # Пауза перед следующей попыткой
            else:
                print(
                    f"[НАСТРОЙКА ТАБЛИЦЫ] ❌ Не удалось настроить {checkbox_name} после {max_attempts} попыток")
                return False

    return False


def _load_all_rows_by_scrolling(driver, wait):
    """
    🚀 ОПТИМИЗИРОВАННАЯ прокрутка с адаптивным ожиданием
    Устраняет time.sleep() и использует WebDriverWait
    """
    try:
        # Убедимся, что таблица есть
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".js-ads-table-body")))

        last_height = driver.execute_script(
            "return document.body.scrollHeight")

        scroll_iterations = 0

        while True:
            # Прокручиваем вниз
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # 🚀 ДОБАВЛЕНО: Пауза 1 секунда после каждой прокрутки для загрузки
            print(f"[ПАРСИНГ] ⏳ Пауза 1 сек для загрузки данных...")
            time.sleep(1)

            # 🚀 УВЕЛИЧЕНО ВРЕМЯ: Адаптивное ожидание (теперь до 8 секунд)
            try:
                # Ждем максимум 8 секунд, пока высота страницы не увеличится
                WebDriverWait(driver, 8).until(lambda d: d.execute_script(
                    "return document.body.scrollHeight") > last_height)
                new_height = driver.execute_script(
                    "return document.body.scrollHeight")
                last_height = new_height
                scroll_iterations += 1
                print(
                    f"[ПАРСИНГ] ✅ Итерация скролла {scroll_iterations}, высота: {new_height}")
            except TimeoutException:
                # Если высота не изменилась за 8 секунд, выходим
                print(
                    "[ПАРСИНГ] ✅ Высота страницы не изменилась, прекращаю прокрутку.")
                break

        print(
            f"[ПАРСИНГ] Прокрутка завершена после {scroll_iterations} итераций")

        # 🚀 ДОБАВЛЕНО: Дополнительная задержка для полной загрузки всех элементов
        print("[ПАРСИНГ] ⏳ Ожидаю 5 секунд для полной загрузки всех элементов...")
        time.sleep(5)

    except Exception as e:
        print(f"[ПАРСИНГ] ⚠️ Ошибка при прокрутке: {e}")


def parse_table_data_optimized(driver):
    """
    🚀🚀 КРИТИЧЕСКИ ОПТИМИЗИРОВАННЫЙ парсинг с локальным HTML парсингом
    """
    try:
        # Ждем загрузки таблицы (увеличено до 20 секунд)
        wait = WebDriverWait(driver, 20)

        # Пробуем разные селекторы для таблицы
        table_selectors = [
            ".js-ads-table-body",
            ".ads-table",
            ".table-body",
            "[class*='table']",
            "[class*='ads']"
        ]

        table_found = False
        for selector in table_selectors:
            try:
                print(f"[ПАРСИНГ] Пробую селектор: {selector}")
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, selector)))
                print(f"[ПАРСИНГ] ✅ Таблица найдена с селектором: {selector}")
                table_found = True
                break
            except Exception as e:
                print(f"[ПАРСИНГ] ❌ Селектор {selector} не найден: {e}")
                continue

        if not table_found:
            print(f"[ПАРСИНГ] ❌ Таблица объявлений не найдена ни с одним селектором")
            return []

        # Перед парсингом загружаем все строки через оптимизированную прокрутку
        try:
            _load_all_rows_by_scrolling(driver, wait)
        except Exception as e:
            print(
                f"[ПАРСИНГ] ⚠️ Не удалось догрузить все строки прокруткой: {e}")

        # 🚀🚀 КРИТИЧЕСКАЯ ОПТИМИЗАЦИЯ: Локальный парсинг HTML
        print("[ПАРСИНГ] 🚀 Переходим к локальному парсингу HTML...")

        # Получаем весь HTML таблицы одной командой
        table_element = driver.find_element(
            By.CSS_SELECTOR, ".js-ads-table-body")
        table_html = table_element.get_attribute('outerHTML')

        # Парсим HTML локально с BeautifulSoup (МНОГОКРАТНО быстрее)
        soup = BeautifulSoup(table_html, 'lxml')
        rows = soup.find_all('tr')

        print(f"[ПАРСИНГ] 📊 Найдено строк в HTML: {len(rows)}")

        # Отладка: выводим структуру первой строки
        if len(rows) > 0:
            first_row = rows[0]
            first_cells = first_row.find_all('td')
            print(
                f"[ПАРСИНГ] 🔍 Первая строка содержит {len(first_cells)} ячеек")
            if len(first_cells) > 0:
                print(
                    f"[ПАРСИНГ] 🔍 Пример первой ячейки: {first_cells[0].get_text(strip=True)[:50]}...")

        parsed_data = []
        skipped_rows = 0

        for i, row in enumerate(rows):
            try:
                cells = row.find_all('td')
                if not cells:
                    skipped_rows += 1
                    continue

                # Пропускаем строки с менее чем 5 ячейками (неполные данные)
                if len(cells) < 5:
                    print(
                        f"[ПАРСИНГ] ⚠️ Строка {i} пропущена: только {len(cells)} ячеек")
                    skipped_rows += 1
                    continue

                # 1) Первая ячейка: заголовок и URL
                title_cell = cells[0]
                title_link = title_cell.find('a', class_='pr-link')

                # 🚀 ИСПРАВЛЕНИЕ: Ищем ссылку с target="_blank" и извлекаем href
                url_link = title_cell.find('a', {'target': '_blank'})

                ad_title = title_link.get_text(
                    strip=True) if title_link else ""

                # 🚀 ИСПРАВЛЕНИЕ: Извлекаем полный URL из атрибута href
                if url_link and url_link.get('href'):
                    ad_url = url_link.get('href')
                else:
                    ad_url = ""

                # 🚀 НОВОЕ: Объединяем Title и URL через перенос строки
                if ad_url:
                    ad_title_with_url = f"{ad_title}\n{ad_url}"
                else:
                    ad_title_with_url = ad_title

                # Далее ячейки идут по порядку как в шапке
                def cell_text(idx):
                    try:
                        if idx >= len(cells):
                            return ""
                        cell = cells[idx]
                        link = cell.find('a', class_='pr-link')
                        if link:
                            return link.get_text(strip=True).replace("\n", " ")
                        else:
                            return cell.get_text(strip=True).replace("\n", " ")
                    except Exception:
                        return ""

                # 🚀 ОБНОВЛЕНО: Индексация согласно реальной структуре HTML
                # Порядок колонок: Ad Title(0), Views(1), Opens(2), Clicks(3), Actions(4), CTR(5), CVR(6), CPM(7), CPC(8), CPA(9), Spent(10), Budget(11), Target(12), Status(13), Date(14)
                views = cell_text(1)
                opens = cell_text(2)  # Эта колонка будет скрыта настройками
                clicks = cell_text(3)
                actions = cell_text(4)
                ctr = cell_text(5)
                cvr = cell_text(6)
                cpm = cell_text(7)
                cpc = cell_text(8)
                cpa = cell_text(9)
                spent = cell_text(10)
                budget = cell_text(11)
                target = cell_text(12)  # Эта колонка будет скрыта настройками
                status = cell_text(13)
                date_added = cell_text(14)

                # 🚀 ОПТИМИЗАЦИЯ: Правильная обработка числовых данных
                def clean_currency_value(value):
                    """Очищает валютные значения: убирает знаки валют и заменяет точки на запятые"""
                    if not value or value == '–':
                        return ""

                    # Убираем знаки валют
                    cleaned = value.replace('€', '').replace(
                        '$', '').replace('₽', '').strip()

                    # Заменяем точки на запятые
                    cleaned = cleaned.replace('.', ',')

                    return cleaned

                try:
                    cpm_clean = cpm.replace('€', '').replace(',', '.')
                    cpm_num = float(
                        cpm_clean) if cpm_clean and cpm_clean != '–' else 0.0
                except ValueError:
                    cpm_num = cpm

                try:
                    budget_clean = budget.replace('€', '').replace(',', '.')
                    budget_num = float(
                        budget_clean) if budget_clean and budget_clean != '–' else 0.0
                except ValueError:
                    budget_num = budget

                # 🚀 НОВОЕ: Обработка колонок CPC, CPA, Spent
                cpc_cleaned = clean_currency_value(cpc)
                cpa_cleaned = clean_currency_value(cpa)
                spent_cleaned = clean_currency_value(spent)

                row_data = {
                    'Ad Title': ad_title_with_url,  # 🚀 ИЗМЕНЕНО: Title + URL через перенос строки
                    'Views': views,
                    'Clicks': clicks,
                    'Actions': actions,
                    'CTR': ctr,
                    'CVR': cvr,
                    'CPM': cpm_num,
                    'CPC': cpc_cleaned,  # 🚀 ОБНОВЛЕНО: Очищенные данные
                    'CPA': cpa_cleaned,  # 🚀 ОБНОВЛЕНО: Очищенные данные
                    'Spent': spent_cleaned,  # 🚀 ОБНОВЛЕНО: Очищенные данные
                    'Budget': budget_num,
                    'Status': status,
                    'Date Added': date_added
                }
                parsed_data.append(row_data)

                # 🔍 ОТЛАДКА: Выводим первую спарсенную строку
                if len(parsed_data) == 1:
                    print(f"[ПАРСИНГ] 🔍 Пример спарсенной строки:")
                    print(f"  - Title with URL: {ad_title_with_url[:100]}...")
                    print(
                        f"  - Views: {views}, Clicks: {clicks}, Actions: {actions}")
                    print(f"  - CTR: {ctr}, CVR: {cvr}")
                    print(
                        f"  - CPM: {cpm_num}, CPC: {cpc_cleaned}, CPA: {cpa_cleaned}")
                    print(f"  - Spent: {spent_cleaned}, Budget: {budget_num}")
                    print(f"  - Status: {status}")

            except Exception as e:
                print(f"[ПАРСИНГ] ❌ Ошибка при парсинге строки {i}: {e}")
                skipped_rows += 1
                continue

        print(f"🚀 Спарсено {len(parsed_data)} строк из таблицы")
        print(f"📊 Всего строк найдено: {len(rows)}")
        print(f"✅ Успешно спарсено: {len(parsed_data)}")
        print(f"⚠️ Пропущено строк: {skipped_rows}")

        return parsed_data

    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {e}")
        return []


def save_to_excel_optimized(data, channel_name, filename=None):
    """
    🚀 ОПТИМИЗИРОВАННОЕ сохранение в Excel с правильными типами данных
    """
    if not filename:
        # Очищаем имя канала от недопустимых символов для имени файла
        import re
        safe_channel_name = re.sub(r'[^\w\s\-_\.]', '', channel_name)
        safe_channel_name = safe_channel_name.replace(' ', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_channel_name}_{timestamp}.xlsx"

    try:
        # Создаем DataFrame из данных
        df = pd.DataFrame(data)

        # 🚀 ОБНОВЛЕНО: Ad Title теперь содержит Title + URL через перенос строки
        columns_order = ['Ad Title', 'Views', 'Clicks', 'Actions', 'CTR', 'CVR',
                         'CPM', 'CPC', 'CPA', 'Spent', 'Budget', 'Status', 'Date Added']
        df = df.reindex(columns=columns_order)

        # 🚀 ОПТИМИЗАЦИЯ: Правильные типы данных для числовых колонок
        numeric_columns = ['CPM', 'Budget']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 🚀 НОВОЕ: Очищаем только колонку Views от запятых
        if 'Views' in df.columns:
            print(f"[СОХРАНЕНИЕ] 🔧 Очищаю колонку Views от запятых...")
            df['Views'] = df['Views'].astype(str).str.replace(',', '')
            print(f"[СОХРАНЕНИЕ] ✅ Колонка Views очищена")

        # 🚀 НОВОЕ: Форматируем дату в нужном формате для колонки Date Added
        print(f"[СОХРАНЕНИЕ] 🔍 Доступные колонки: {list(df.columns)}")

        if 'Date Added' in df.columns:
            print(
                f"[СОХРАНЕНИЕ] 🔍 Найдена колонка Date Added, начинаю форматирование...")
            print(
                f"[СОХРАНЕНИЕ] 🔍 Пример исходной даты: {df['Date Added'].iloc[0] if len(df) > 0 else 'Нет данных'}")

            # Применяем форматирование к каждой дате
            df['Date Added'] = df['Date Added'].apply(format_date_added)

            print(
                f"[СОХРАНЕНИЕ] 🔍 Пример отформатированной даты: {df['Date Added'].iloc[0] if len(df) > 0 else 'Нет данных'}")
            print(
                f"[СОХРАНЕНИЕ] ✅ Даты отформатированы в формат месяц/день/год время")
        else:
            print(f"[СОХРАНЕНИЕ] ⚠️ Колонка Date Added не найдена в DataFrame")

        # Сохраняем в Excel
        df.to_excel(filename, index=False, engine='openpyxl')

        print(f"🚀 Данные канала '{channel_name}' сохранены в файл: {filename}")
        return filename

    except Exception as e:
        print(f"Ошибка при сохранении в Excel: {e}")
        return None


def configure_table_settings(driver):
    """
    Настраивает таблицу - нажимает кнопку настроек и выбирает нужные колонки
    """
    try:
        wait = WebDriverWait(driver, 10)

        # 🚀 ДОБАВЛЕНО: Увеличиваем размер окна для лучшей видимости элементов
        driver.maximize_window()
        time.sleep(1)

        # Находим и нажимаем кнопку настроек таблицы
        settings_button = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, ".pr-table-settings")))
        print("[НАСТРОЙКА ТАБЛИЦЫ] ✅ Найдена кнопка настроек, нажимаю...")
        settings_button.click()

        # Ждем появления попапа настроек
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".pr-layer-popup.popup-no-close")))
        print("[НАСТРОЙКА ТАБЛИЦЫ] ✅ Попап настроек открыт")

        # Список нужных чекбоксов для включения (согласно реальной структуре)
        required_checkboxes = [
            "views", "clicks", "actions", "ctr", "cvr", "cpm", "cpc",
            "cpa", "spent", "budget", "status", "date"
        ]

        # Список чекбоксов для отключения (оставляем только нужные)
        all_checkboxes = [
            "opens", "target", "url", "action"
        ]

        # 🚀 ОБНОВЛЕНО: Используем безопасную функцию для отключения ненужных чекбоксов
        for checkbox_name in all_checkboxes:
            safe_checkbox_interaction(
                driver, checkbox_name, should_be_selected=False)

        # 🚀 ОБНОВЛЕНО: Используем безопасную функцию для включения нужных чекбоксов
        for checkbox_name in required_checkboxes:
            safe_checkbox_interaction(
                driver, checkbox_name, should_be_selected=True)

        # Закрываем попап настроек
        close_button = driver.find_element(
            By.CSS_SELECTOR, ".popup-cancel-btn")
        close_button.click()
        print("[НАСТРОЙКА ТАБЛИЦЫ] ✅ Настройки применены, попап закрыт")

        # Ждем обновления таблицы
        time.sleep(2)

        return True

    except Exception as e:
        print(f"[НАСТРОЙКА ТАБЛИЦЫ] ❌ Ошибка при настройке таблицы: {e}")
        return False


def parse_channel_data_optimized(driver, channel_name, save_excel=True):
    """
    🚀 ОПТИМИЗИРОВАННЫЙ поиск канала и парсинг данных
    """
    try:
        # Находим канал
        channel_element = find_channel_by_name(driver, channel_name)

        if not channel_element:
            return {'error': f'Канал "{channel_name}" не найден'}

        # Кликаем по каналу
        channel_element.click()

        # 🚀 ОПТИМИЗАЦИЯ: Ждем загрузки специфического элемента вместо time.sleep()
        wait = WebDriverWait(driver, 15)  # Увеличено до 15 секунд
        try:
            # Ждем появления таблицы или заголовка страницы канала
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".js-ads-table-body")))
            print("[ПАРСИНГ] ✅ Таблица найдена, ожидаю дополнительно 2 сек...")
            time.sleep(2)  # Дополнительная пауза после появления таблицы
        except TimeoutException:
            print("⚠️ Таблица не загрузилась за 15 секунд, продолжаем...")

        # 🚀 НОВОЕ: Настраиваем таблицу перед парсингом
        print("[ПАРСИНГ] 🔧 Настраиваю таблицу...")
        if not configure_table_settings(driver):
            print(
                "[ПАРСИНГ] ⚠️ Не удалось настроить таблицу, продолжаем с текущими настройками")

        # Парсим данные таблицы с критическими оптимизациями
        table_data = parse_table_data_optimized(driver)

        result = {
            'channel_name': channel_name,
            'table_data': table_data,
            'status': 'success'
        }

        # Сохраняем в Excel если нужно
        if save_excel and table_data:
            excel_file = save_to_excel_optimized(table_data, channel_name)
            if excel_file:
                result['excel_file'] = excel_file

        return result

    except Exception as e:
        return {'error': f'Ошибка при парсинге канала: {e}'}
