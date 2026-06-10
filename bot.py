import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
import time
from datetime import datetime
import json

# НЕ ЗАБЫТЬ ПОМЕНЯТЬ
TOKEN = "vk1.a.ptzBVqWpVUh7Q30u8FV-Ku8u1Zdhx_RpjZhSut9jViFPdBxH7w48znMt8PCDzp0Ht3jys7iRk-V4bCyn3tDuKF9GqXMaiZJVrS9JD_VjUm_VdmUMHirkRIxYtF3xY7Fr2JMyeituuZ8XuMNMAjQtguuFaqexVqtSnK4COimQO0BaURtaTprHnGSB_gXTqeZpA_lylBwTKE5lTrj3teS7fA"
GROUP_ID = 235623171

# Подключение к VK API
vk_session = vk_api.VkApi(token=TOKEN, api_version="5.199")
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()


# классика
def cmd_hello():
    return "Привет! Я бот!"


def cmd_bye():
    return "До свидания! 👋"


def cmd_help():
    return (
        "Доступные команды: привет, hi, пока, bye, помощь, help, цитата, коллаж, время"
    )


def cmd_time():
    now = datetime.now().strftime("%H:%M:%S")
    return f"Сейчас {now}"


commands = {
    "привет": cmd_hello,
    "hi": cmd_hello,
    "пока": cmd_bye,
    "bye": cmd_bye,
    "помощь": cmd_help,
    "help": cmd_help,
    "время": cmd_time,
    "time": cmd_time,
}
PROFILES_FILE = r"C:\Users\chesn\Desktop\аэа\profiles.json"


def load_profiles():
    # Загружаем пользовательские профили из JSON-файла
    if not os.path.exists(PROFILES_FILE):
        print(f"Файл {PROFILES_FILE} не найден, использую стандартные имена")
        return {}
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"Загружено профилей: {len(data)}")
            return data
    except Exception as e:
        print(f"Ошибка загрузки {PROFILES_FILE}: {e}")
        return {}


def get_user_custom_profile(user_id):
    # Возвращаем кастомный профиль пользователя, если он есть
    profiles = load_profiles()
    user_id_str = str(user_id)
    if user_id_str in profiles:
        return profiles[user_id_str]
    return None


def get_user_display_info(vk, user_id):
    """
    Возвращает (имя_для_отображения, url_аватарки) для пользователя
    Если есть кастомный профиль — используем его.
    Иначе — берём данные из VK.
    """
    # Проверяем кастомный профиль
    custom = get_user_custom_profile(user_id)

    # бля, заебло, типа логи, чтоб понять где ссаная ошибка
    print(f"[DEBUG] user_id={user_id}, custom={custom}")

    if custom and custom.get("name"):
        print(f"[DEBUG] ✓ Использую кастомное имя: {custom['name']}")
        # Если в профиле указан кастомный URL аватарки — используем его
        avatar_url = custom.get("avatar_url") if custom.get("avatar_url") else None

        # Если аватарка не задана в профиле — пробуем взять из VK
        if not avatar_url:
            try:
                user_info = vk.users.get(user_ids=user_id, fields=["photo_100"])[0]
                avatar_url = user_info.get("photo_100", "")
            except Exception as e:
                print(f"[DEBUG] Ошибка получения аватарки из VK: {e}")
                avatar_url = ""

        return custom["name"], avatar_url

    # Нет кастомного профиля — берём из VK
    print(f"[DEBUG] ✗ Кастомного профиля нет для {user_id}, беру из VK")
    try:
        user_info = vk.users.get(user_ids=user_id, fields=["photo_100"])[0]
        name = f"{user_info['first_name']} {user_info['last_name']}"
        avatar_url = user_info.get("photo_100", "")
        return name, avatar_url
    except Exception as e:
        print(f"[DEBUG] Ошибка получения данных из VK: {e}")
        return "Неизвестный пользователь", ""


# цитаты
def create_quote_image(quote_text, author_name, avatar_url):

    # НАСТРОЙКИ
    width = 800  # ширина картинки
    avatar_size = 60  # размер аватарки (ширина и высота)
    avatar_x = 30  # отступ аватарки слева
    avatar_y = 30  # отступ аватарки сверху

    name_x = 100  # отступ имени слева
    name_y = 45  # отступ имени сверху
    name_font_size = 24  # размер шрифта имени
    name_color = "#cba6f7"  # цвет имени

    text_x = 40  # отступ текста цитаты слева
    text_font_size = 16  # размер шрифта цитаты
    text_color = "#cdd6f4"  # цвет текста цитаты
    line_spacing = 25  # расстояние между строками

    padding_top = 100  # отступ сверху (аватарка + имя + воздух)
    padding_bottom = 40  # отступ снизу (пустое пространство после текста)

    # шрифты
    # СКАЧАЙ ПОТОМ ЧЕ-НИТЬ ПРИКОЛЬНОЕ, А ТО ХУЛИ. Пока ссылки просто для заполнения
    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", name_font_size)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", text_font_size)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Создаём временное изображение, чтобы измерить текст
    temp_img = Image.new("RGB", (width, 100))
    temp_draw = ImageDraw.Draw(temp_img)

    # Разбиваем текст на строки с учётом ширины
    lines = []
    words = quote_text.split()
    if not words:
        words = [""]

    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        bbox = temp_draw.textbbox((0, 0), test_line, font=font_small)
        if bbox[2] - bbox[0] < width - text_x * 2:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    # Убираем возможные пустые строки
    lines = [line for line in lines if line.strip()]

    # Высота картинки
    text_height = len(lines) * line_spacing
    total_height = padding_top + text_height + padding_bottom

    # Создаём финальное изображение с рассчитанной высотой
    img = Image.new("RGB", (width, total_height), color="#1e1e2e")
    draw = ImageDraw.Draw(img)

    # ава
    try:
        resp = requests.get(avatar_url, timeout=5)
        avatar = Image.open(BytesIO(resp.content)).resize((avatar_size, avatar_size))
        img.paste(avatar, (avatar_x, avatar_y))
    except:
        pass

    # ник
    draw.text((name_x, name_y), author_name, fill=name_color, font=font_big)

    # сама цитата построчно
    y = padding_top
    for line in lines:
        draw.text((text_x, y), line, fill=text_color, font=font_small)
        y += line_spacing

    # Сохраняем картинку
    output_path = "quote.png"
    img.save(output_path)
    return output_path


def create_quote_image_multi(quotes_list, width=800):
    """Создаёт картинку-коллаж из нескольких цитат (высота подстраивается под количество)"""

    avatar_size = 40  # размер аватарки
    avatar_x = 30  # отступ аватарки слева

    name_x = 100  # отступ имени слева
    name_font_size = 20  # размер шрифта имени
    name_color = "#cba6f7"  # цвет имени

    text_x = 80  # отступ текста цитаты слева
    text_font_size = 14  # размер шрифта цитаты
    text_color = "#cdd6f4"  # цвет текста цитаты
    text_max_length = 150  # максимальная длина текста (символов)

    line_height = 100  # высота одной цитаты (аватарка + имя + текст)
    padding_top = 30  # отступ сверху (перед первой цитатой)
    padding_bottom = 7  # отступ снизу (пустое пространство после последней цитаты)

    divider_color = "#45475a"  # цвет разделительной линии
    divider_width = 1  # толщина разделительной линии

    # Загружаем шрифты. ТУТ ТАК ЖЕ КАК И В ПРОШЛОЙ НЕ ЗАБЫТЬ
    try:
        font_big = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", name_font_size)
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", text_font_size)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    total_height = padding_top + (len(quotes_list) * line_height) + padding_bottom

    # Создаём изображение с рассчитанной высотой
    img = Image.new("RGB", (width, total_height), color="#1e1e2e")
    draw = ImageDraw.Draw(img)

    # цитатка
    y_offset = padding_top

    for quote in quotes_list:
        # Ава
        try:
            resp = requests.get(quote["avatar_url"], timeout=5)
            avatar = Image.open(BytesIO(resp.content)).resize(
                (avatar_size, avatar_size)
            )
            img.paste(avatar, (avatar_x, y_offset + 5))
        except:
            pass

        # Имя автора
        draw.text(
            (name_x, y_offset + 5), quote["author"], fill=name_color, font=font_big
        )

        # Текст цитаты (обрезаем, если слишком длинный)
        text = quote["text"]
        if len(text) > text_max_length:
            text = text[:text_max_length] + "..."

        draw.text((text_x, y_offset + 35), text, fill=text_color, font=font_small)

        # Разделительная линия (кроме последней цитаты)
        if quote != quotes_list[-1]:
            line_y = y_offset + line_height - 10
            draw.line(
                (30, line_y, width - 30, line_y),
                fill=divider_color,
                width=divider_width,
            )

        y_offset += line_height

    # Сохраняем картинку
    output_path = "quotes_collage.png"
    img.save(output_path)
    return output_path


def upload_doc(vk_session, file_path, peer_id):
    """Загружает документ в VK и возвращает attachment"""
    vk = vk_session.get_api()
    upload_server = vk.docs.getMessagesUploadServer(type="doc", peer_id=peer_id)[
        "upload_url"
    ]
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(upload_server, files=files).json()
    doc = vk.docs.save(file=response["file"])["doc"]
    return f"doc{doc['owner_id']}_{doc['id']}"


def cmd_quote(event, vk_session, vk):
    """Обработчик команды 'цитата' — отдельные картинки"""
    msg = event.object.message

    if not msg.get("fwd_messages"):
        return "❌ Перешлите одно или несколько сообщений, чтобы я сделал цитаты!"

    fwd_messages = msg["fwd_messages"]
    attachments = []
    max_quotes = 5

    if len(fwd_messages) > max_quotes:
        return f"⚠️ Слишком много сообщений! Обработаю только первые {max_quotes}."

    vk_api_instance = vk_session.get_api()

    for fwd in fwd_messages[:max_quotes]:
        text = fwd.get("text", "")
        author_id = fwd.get("from_id")

        if not text:
            continue

        # для получения имени и аватарки
        author_name, avatar_url = get_user_display_info(vk, author_id)

        img_path = create_quote_image(text, author_name, avatar_url)
        attachment = upload_doc(vk_session, img_path, msg["peer_id"])
        attachments.append(attachment)
        os.remove(img_path)
        time.sleep(0.3)

    if not attachments:
        return "❌ Не удалось обработать ни одного сообщения (возможно, нет текста)"

    vk_api_instance.messages.send(
        peer_id=msg["peer_id"],
        message=f"📌 {len(attachments)} цитат:",
        random_id=get_random_id(),
        attachment=",".join(attachments),
    )
    return None


def cmd_quote_collage(event, vk_session, vk):
    """Обработчик команды 'коллаж' — одна картинка со всеми цитатами"""
    msg = event.object.message

    if not msg.get("fwd_messages"):
        return "❌ Перешлите сообщения для создания коллажа цитат!"

    quotes_data = []
    vk_api_instance = vk_session.get_api()

    for fwd in msg["fwd_messages"][:5]:
        text = fwd.get("text", "")
        author_id = fwd.get("from_id")

        if not text:
            continue

        # для получения имени и аватарки
        author_name, avatar_url = get_user_display_info(vk, author_id)

        quotes_data.append(
            {"text": text, "author": author_name, "avatar_url": avatar_url}
        )

    if not quotes_data:
        return "❌ Нет текста в пересланных сообщениях"

    img_path = create_quote_image_multi(quotes_data)
    attachment = upload_doc(vk_session, img_path, msg["peer_id"])

    vk_api_instance.messages.send(
        peer_id=msg["peer_id"],
        message=f"📌 Коллаж из {len(quotes_data)} цитат:",
        random_id=get_random_id(),
        attachment=attachment,
    )

    os.remove(img_path)
    return None


# тут все запускается
print("Бот запущен! Ожидание сообщений...")

# Импортируем типы ошибок для обработки
from requests.exceptions import ReadTimeout, ConnectionError

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.object.message
                peer_id = msg["peer_id"]
                text = msg["text"].lower().strip()

                # Команда "цитата"
                if text == "цитата":
                    result = cmd_quote(event, vk_session, vk)
                    if result:
                        vk.messages.send(
                            peer_id=peer_id, message=result, random_id=get_random_id()
                        )

                # Команда "коллаж"
                elif text == "коллаж":
                    result = cmd_quote_collage(event, vk_session, vk)
                    if result:
                        vk.messages.send(
                            peer_id=peer_id, message=result, random_id=get_random_id()
                        )

                # Обычные команды из словаря
                elif text in commands:
                    answer = commands[text]()
                    vk.messages.send(
                        peer_id=peer_id, message=answer, random_id=get_random_id()
                    )
                    print(
                        f"Сообщение от {msg['from_id']} в чате {peer_id}: '{text}' -> ответ отправлен"
                    )

    # ошибочки
    except ReadTimeout:
        print("⏰ Таймаут соединения с VK (сервер не ответил вовремя)")
        print("🔄 Переподключаюсь через 3 секунды...")
        time.sleep(3)
        try:
            longpoll = VkBotLongPoll(vk_session, GROUP_ID)
            print("✅ Переподключено!")
        except Exception as e:
            print(f"❌ Ошибка переподключения: {e}")
            print("🔄 Повторная попытка через 10 секунд...")
            time.sleep(10)
            longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    except ConnectionError:
        print("🌐 Ошибка соединения (проблема с интернетом или сервером VK)")
        print("🔄 Переподключаюсь через 5 секунд...")
        time.sleep(5)
        try:
            longpoll = VkBotLongPoll(vk_session, GROUP_ID)
            print("✅ Переподключено!")
        except Exception as e:
            print(f"❌ Ошибка переподключения: {e}")
            print("🔄 Повторная попытка через 15 секунд...")
            time.sleep(15)
            longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    except Exception as e:
        print(f"❌ Неожиданная ошибка: {type(e).__name__}: {e}")
        print("🔄 Переподключаюсь через 5 секунд...")
        time.sleep(5)
        try:
            longpoll = VkBotLongPoll(vk_session, GROUP_ID)
            print("✅ Переподключено!")
        except:
            print("⚠️ Не удалось переподключиться, пробую снова через 10 секунд...")
            time.sleep(10)
            longpoll = VkBotLongPoll(vk_session, GROUP_ID)
