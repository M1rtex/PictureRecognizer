import easyocr
import pytesseract
import cv2
import telebot
from os import remove
from glob import glob

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_config = r"--oem 3 --psm 6"
TOKEN = ''


def text_recognition(file_path):
    img = cv2.imread(file_path)
    reader = easyocr.Reader(["en"])
    info = reader.readtext(img, detail=1)
    positions = info[0][0]
    start_x, fin_x, start_y, fin_y = positions[0][0], positions[1][0], positions[0][1], positions[2][1]
    img = img[start_y:fin_y, start_x:fin_x]
    # cv2.imshow("res", img) # cropped preview
    # cv2.waitKey(0) # cropped preview
    result = pytesseract.image_to_string(img, config=custom_config).strip()
    return result


def telegram_bot(token):
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, "Привет, я бот по распознаванию цифр с картинок.\nПришли мне картинку и я всё распознаю)")

    @bot.message_handler(content_types=['document', 'photo'])
    def send_message(message):
        try:
            chat_id = message.chat.id
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            src = './img/' + message.document.file_name
            with open(src, 'wb') as new_file:
                new_file.write(downloaded_file)
            bot.reply_to(message, "Принял, понял, передал")
            data = text_recognition(src)
            with open(src, 'rb') as ph:
                # bot.send_document(message.chat.id, ph)
                bot.reply_to(message, f"Всё готово! Вот данные:\n{data}")
            for file in glob('./img/*'):
                remove(file)
        except Exception as e:
            bot.reply_to(message, f'Ой ошибка:\n{e}\nЯ не гугл, я не понимаю ((((((')

    @bot.message_handler(content_types=['text'])
    def reply_to_text(message):
        if message.text.lower() == "привет":
            start_message(message)
        else:
            bot.send_message(message.chat.id,
                             "Я работаю по принципу: картинка ---> результат.\nОтправь мне картинку и начнём работу!")

    bot.polling()


if __name__ == '__main__':
    telegram_bot(TOKEN)
