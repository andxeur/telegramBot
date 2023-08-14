# © Copyright (c) 2023 ANDXEUR
#
# Permission is granted, free of charge, to any person who obtains a copy
# of this software and associated documentation files (the "Software"), to be processed
# in the Software without restriction, including without limitation the rights
# use, copy, modify, merge, publish, distribute, sublicense and/or sell
# copies of the Software, and to allow persons to whom the Software is
# provided for this purpose, subject to the following conditions:
#
# **************************************************************************************
# The copyright notice above and this permission notice must be included in all
# copies or substantial parts of the Software.
# **************************************************************************************
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT ANY WARRANTY, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NOT INFRINGEMENT. UNDER NO CIRCUMSTANCES THE
# AUTHORS OR COPYRIGHT HOLDERS ARE RESPONSIBLE FOR ANY CLAIMS, DAMAGES OR OTHER
# LIABILITY, CONTRACTUAL, TORT OR OTHERWISE, ARISING FROM:
# IN CONNECTION WITH THE SOFTWARE, USE OR OTHER TRANSACTIONS IN THE SOFTWARE.
#
# UNDER NO CIRCUMSTANCES THE AUTHORS OR HOLDERS OF THESE PROGRAMS ARE RESPONSIBLE FOR ANY DAMAGE
# OR OTHER LIABILITY, CAUSED BY THIS PROGRAM
#
# YOUR SOLE OBLIGATION IS TO STIPULATE (INCLUDED) THE NAMES OF THE AUTHORS OF THE PROGRAM WITH THE COPYRIGHT NOTICE IN
# ALL SUBSTANTIAL PARTS OF THE SOFTWARE.
#
# ----------------------------------------------**********ANDXEUR***********----------------------------------------
# We developers develop software that you use on a daily basis, doesn’t that mean we code a part of your life?     #
# ----------------------------------------------**********************----------------------------------------------

import datetime
import json
import os
import pathlib

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, ContextTypes

except ModuleNotFoundError:
    os.system("pip install python-telegram-bot")
    os.system("pip install python-telegram-bot[job-queue]")

# enable log
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

if not os.path.exists('configBot.json'):
    with open('configBot.json', 'w') as json_file_config:
        data_json = {
            "postStatus": False,
        }
        json.dump(data_json, json_file_config, sort_keys=True, indent=2)

# pass it your bots token.
API_KEY_TOKEN_BOT = "......"
ID_BOT_TELEGRAM = None  # exp : 10000500

# cannal id or posts will be send don’t forget to add your bot to this channel means admin
# replace ...... by your id  / exp: "-100'+"11991000118"
id_of_your_channel = "-100" + "......"

files_path = "...."  # exp: ".img/imgJoke"
list_file_names = os.listdir(files_path)
nbr = -1
status_post: bool = False
state: bool = False

hours_post = 16
minute_post = 00
second_post = 00

post_time = datetime.time(hours_post, minute_post, second_post, 000000)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f"""
        Hey! {update.effective_user.first_name} I am the help bot to take action using the following commands: 

        /help or /command  
        -> list all available options  

        /post <option> exp: /post all
        -> to send daily post at the scheduled time 

        /post all
        -> send all images contained in the image directory 

        /stop 
        -> stop the publication of current items

        /count
        -> counts the number of images available 

        /countImg
        -> see the number of images posted  

        /status
        -> see if publication is enabled
    """)


async def image(context: ContextTypes.DEFAULT_TYPE) -> None:
    global nbr, state
    nbr += 1

    job = context.job

    if nbr < len(list_file_names):
        obtained_file = pathlib.Path(list_file_names[nbr])
        full_path_img = os.path.join(files_path, list_file_names[nbr])

        with open('configBot.json', 'r') as f:
            data = json.load(f)

        if obtained_file.suffix != ".mp4":
            await context.bot.send_photo(photo=full_path_img, chat_id=id_of_your_channel)
            os.remove(full_path_img)
            state = True
            data['postStatus'] = True
            with open('configBot.json', 'w') as f:
                json.dump(data, f, sort_keys=True, indent=2)

        else:
            await context.bot.send_video(video=full_path_img, chat_id=id_of_your_channel)
            os.remove(full_path_img)
            state = True
            data['postStatus'] = True
            with open('configBot.json', 'w') as f:
                json.dump(data, f, sort_keys=True, indent=2)

    else:
        # account reset
        nbr = -1
        # if we reach the last file to be posted, stop the planning of the posts
        # supp_planification_si_presente(str(job.chat_id), context)
        await context.bot.sendMessage(
            chat_id=ID_BOT_TELEGRAM,
            text=
            """
            end of daily post please add new image and restart command:

            /help or/command 
            -> list all available titles

            /post <option> 
            -> to send daily post at the scheduled time 

            /post all 
            -> send all images contained in the image directory 
        """)


def supp_planification_si_presente(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    names_of_job = context.job_queue.get_jobs_by_name(name)
    if not names_of_job:
        return False
    for job in names_of_job:
        job.schedule_removal()
    return True


async def publish_img_manually(update: Update, context: ContextTypes.DEFAULT_TYPE, optionComande: str = "all") -> None:
    # recupere l'id du bot lui meme
    chat_id = update.effective_message.chat_id

    global status_post
    status_post = True

    job_removed = supp_planification_si_presente(str(chat_id), context)

    context.job_queue.run_daily(image,
                                time=post_time,
                                days=(0, 1, 2, 3, 4, 5, 6),
                                name=str(id_of_your_channel),
                                data=optionComande)

    text = "Daily post activate with success !"

    if job_removed:
        text += "The old task planning has been removed."

    await update.effective_message.reply_text(text)
    await update.effective_message.reply_text(
        "publish activate successfully")


async def start_publication(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        optionComande = str(context.args[0])

        if optionComande == "all":
            await publish_img_manually(update, context)
        else:
            raise ValueError("the option entered is non-existent check your entry")

    except (IndexError, ValueError):
        await update.effective_message.reply_text(
            """
            it seems that no option has been entered or you have entered a wrong option Use: 

            /help or /command  
            -> list all available options  

            /post <option> exp: /post all
            -> to send daily post at the scheduled time 

            /post all
            -> send all images contained in the image directory 

            /stop 
            -> stop the publication of current items
""")


async def publish_img_auto(application: Application) -> None:
    chat_id = ID_BOT_TELEGRAM

    global status_post
    status_post = True

    job_removed = supp_planification_si_presente(str(chat_id), application)

    application.job_queue.run_daily(image, time=post_time, days=(0, 1, 2, 3, 4, 5, 6), name=str(id_of_your_channel))

    text = "Daily post activate with success !"

    if job_removed:
        text += "The old task planning has been removed."

    await application.bot.sendMessage(chat_id=ID_BOT_TELEGRAM, text=f"""{text} publish activate successfully !""")


async def stop_publication(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global status_post
    status_post = False

    job_removed = supp_planification_si_presente(str(id_of_your_channel), context)
    text = """         
    publication desactivate with success! 
    To restart it Please enter the command:

    /post all 
    -> send all images contained in the image directory 
    """ if job_removed else "No active publication to stop."

    await update.message.reply_text(text)


async def count_all_available_images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nbr_files = len(list_file_names)
    await update.message.reply_text(f"{nbr_files} files available")


async def count_images_posted(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    nbr_files_get = len(list_file_names)
    files_posted = nbr + 1

    if files_posted == nbr_files_get:
        await update.message.reply_text(
            f"{files_posted}/{nbr_files_get} end of the publication all the files were posted !"
        )
    else:
        await update.message.reply_text(
            f"{files_posted}/{nbr_files_get} files posted")


async def status_publication(update: Update,
                             context: ContextTypes.DEFAULT_TYPE) -> None:
    if status_post:
        await update.message.reply_text(
            "the publication is still active")
    else:
        await update.message.reply_text("the publication is disabled")


async def post_init(application: Application) -> None:
    await publish_img_auto(application)

    current_time = datetime.datetime.now().time()

    with open('configBot.json', 'r') as f:
        data = json.load(f)

    if current_time > post_time and not data['postStatus']:

        newHeure = datetime.time(current_time.hour, current_time.minute + 1, 00,
                                 000000)
        application.job_queue.run_once(image, newHeure, name=str(id_of_your_channel))

    elif current_time < post_time:

        data['postStatus'] = False
        with open('configBot.json', 'w') as f:
            json.dump(data, f, sort_keys=True, indent=2)


def main() -> None:
    """Run bot."""
    application = Application.builder().token(API_KEY_TOKEN_BOT).post_init(post_init).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler(["help", "command"], help))
    application.add_handler(CommandHandler("post", start_publication))
    application.add_handler(CommandHandler("stop", stop_publication))
    application.add_handler(CommandHandler("count", count_all_available_images))
    application.add_handler(CommandHandler("countImg", count_images_posted))
    application.add_handler(CommandHandler("status", status_publication))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
