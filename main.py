import logging
from telegram.ext import Application, MessageHandler, filters, CommandHandler

from db_connector import DbConnector

BOT_TOKEN = "6254947443:AAFKXLTMdpMY3P7uRczslDOi_StqIbI5nIs"

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

connector = DbConnector("tasks.db")


def get_all_tasks(chat_id):
    """Функция для получения всех задач и преобразования в str"""
    tasks = connector.get_all_tasks(chat_id)
    if not tasks:
        return "Список задач пуст."
    msg = ""
    for num, task in enumerate(tasks, start=1):
        time = None
        try:
            time = task[4].split('_')
            time = f". Затрачено { time[0]} дней {time[1]} часов {time[2]} минут"
        except BaseException:
            pass
        if not 'дней' in time and task[1] != "❌" and task[1] != "✅":
            time = '(задача не завершена)'
        elif task[1] == "❌" :
            time = '(задача отменена)'
        msg += f"{num}) {task[1]} {task[0]} {time}\n"
    return msg

async def start(update, context):
    """Старт."""
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    await update.message.reply_text(
        "Привет! Я бот-напоминалка. Буду рад помочь тебе с делами!\n"
        "Пропиши /help для того, чтобы узнать все актуальные команды!"
    )


async def help_func(update, context):
    """Помощь пользователю - список команд"""
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    await update.message.reply_text(
        "Привет! Я бот для управления задачами.\n\n"
        "/new (название задачи) - создать новую задачу\n"
        "/cancel (название задачи) - изменить статус задачи \
            (завершена -> не завершена; не завершена -> отменена; отменена -> не завершена)\n"
        "/done (название задачи) - изменить статус задачи на завершена\n"
        "/all - прогресс работы по всем todo задачам\n"
        "/clear - очистить список всех задач\n"
        "/del (название задачи) - удаление выбранной задачи"
    )


async def create_new_task(update, context):
    """ Создает новую задачу"""
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("Пожалуйста, укажите задачу.")
        return
    connector.create_new_task(task, update.message.chat_id)
    await update.message.reply_text(f"Задача «{task}» добавлена.")
    await update.message.reply_text(get_all_tasks(update.message.chat_id))


async def change_task_status(update, context):
    """изменяет статус задачи"""
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("Пожалуйста, укажите задачу.")
        return
    if not connector.check_task(task, update.message.chat_id):
        await update.message.reply_text("Задача не существует")
        return
    connector.change_task(task, update.message.chat_id)
    await update.message.reply_text(f"Статус задачи «{task}» изменен")
    await update.message.reply_text(get_all_tasks(update.message.chat_id))

async def clear_tasks(update, context):
    """Очищает список задач по команде /clear"""
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    connector.clear_tasks(update.message.chat_id)
    await update.message.reply_text("Список задач удален")


async def clear_task(update, context):
    """Удаляет одну выбранную задачу"""
    task = " ".join(context.args)
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    connector.clear_task(task, update.message.chat_id)
    await update.message.reply_text("Задача удалена")


async def complete_task(update, context):
    """ завершить todo задачу по команде /complete"""
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("Пожалуйста, укажите задачу")
        return
    if not connector.check_task(task, update.message.chat_id):
        await update.message.reply_text(f"Задача «{task}» не существует")
        return
    connector.complete_task(task, update.message.chat_id)
    await update.message.reply_text(f"Статус задачи '{task}' изменен на «завершена»")
    await update.message.reply_text(get_all_tasks(update.message.chat_id))


async def all_tasks(update, context):
    """Выводит все задачи"""
    await context.bot.delete_message(chat_id=update.effective_chat.id,
                                     message_id=update.message.message_id)
    await update.message.reply_text(get_all_tasks(update.message.chat_id))


async def unknown(update, context):
    """Обработчик неизвестных команд"""
    await update.message.reply_text("Извините, я не понимаю эту команду.")


def main():
    """Просто main"""
    # Создаём объект Application.
    # Вместо слова "TOKEN" надо разместить полученный от @BotFather токен
    application = Application.builder().token(BOT_TOKEN).build()

    # Создаём обработчик сообщений типа filters.TEXT
    # из описанной выше асинхронной функции echo()
    # После регистрации обработчика в приложении
    # эта асинхронная функция будет вызываться при получении сообщения
    # с типом "текст", т. е. текстовых сообщений.
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help_func)
    new_handler = CommandHandler('new', create_new_task)
    clear_all_handler = CommandHandler('clear', clear_tasks)
    clear_one_handler = CommandHandler('del', clear_task)
    done_handler = CommandHandler('done', complete_task)
    all_handler = CommandHandler('all', all_tasks)
    change_task_status_handler = CommandHandler('cancel', change_task_status)
    unknown_command_handler = MessageHandler(filters.TEXT, unknown)


    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(new_handler)
    application.add_handler(clear_all_handler)
    application.add_handler(clear_one_handler)
    application.add_handler(done_handler)
    application.add_handler(change_task_status_handler)
    application.add_handler(all_handler)
    application.add_handler(unknown_command_handler)
    # application.add_handler(message_handler)

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()