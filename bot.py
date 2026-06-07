import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

TOKEN = "vk1.a.ptzBVqWpVUh7Q30u8FV-Ku8u1Zdhx_RpjZhSut9jViFPdBxH7w48znMt8PCDzp0Ht3jys7iRk-V4bCyn3tDuKF9GqXMaiZJVrS9JD_VjUm_VdmUMHirkRIxYtF3xY7Fr2JMyeituuZ8XuMNMAjQtguuFaqexVqtSnK4COimQO0BaURtaTprHnGSB_gXTqeZpA_lylBwTKE5lTrj3teS7fA"

GROUP_ID = 235623171  # ID группы

# Подключение к VK API
vk_session = vk_api.VkApi(token=TOKEN)
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()


# Функции-обработчики команд
def cmd_hello():
    return "Привет! Я бот!"


def cmd_bye():
    return "До свидания! 👋"


def cmd_help():
    return "Доступные команды: привет, hi, пока, bye, помощь, help"


def cmd_time():
    from datetime import datetime

    now = datetime.now().strftime("%H:%M:%S")
    return f"Сейчас {now}"


# Сами команды
commands = {
    "привет": cmd_hello,
    "hi": cmd_hello,
    "пока": cmd_bye,
    "bye": cmd_bye,
    "хелп": cmd_help,
    "help": cmd_help,
    "время": cmd_time,
    "time": cmd_time,
}

print("Бот запущен! Ожидание сообщений...")

# Основной цикл обработки событий
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object.message
        peer_id = msg[
            "peer_id"
        ]  # чтоб сообщения отправлялись в тот чат, где было написано, а не в личку
        text = msg["text"].lower().strip()

        # Проверяем, есть ли команда в словаре
        if text in commands:
            answer = commands[text]()
            vk.messages.send(
                peer_id=peer_id,  # отправляем в тот же чат
                message=answer,
                random_id=get_random_id(),
            )
            print(
                f"Сообщение от {msg['from_id']} в чате {peer_id}: '{text}' -> ответ отправлен"
            )
