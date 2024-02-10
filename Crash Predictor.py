import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Telegram bot token
TOKEN = '6693574970:AAHPcGJQUWLZC0_2Oid9ve8ONDKnIzCxrSY'

# Last 50 multiplier
def aggiorna_moltiplicatori_da_sito(file_csv):
    url = "https://roobet.party/crash"
    
    # Http Request
    response = requests.get(url)
    
    if response.status_code == 200:
        # analys of Html with beautifulsoup 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find multiplier
        moltiplicatori_elements = soup.find_all("div", class_="crash-history-item")

        # Take last 50 
        ultimi_moltiplicatori = [float(elem.text) for elem in moltiplicatori_elements[:50]]

        # Update or Create file CSV
        if os.path.exists(file_csv):
            df = pd.read_csv(file_csv)
            df = pd.concat([pd.DataFrame({'moltiplicatore': ultimi_moltiplicatori}), df], ignore_index=True)
            df = df.drop_duplicates(subset=['moltiplicatore']).head(50) 
        else:
            df = pd.DataFrame({'moltiplicatore': ultimi_moltiplicatori})

        df.to_csv(file_csv, index=False)

        return ultimi_moltiplicatori
    else:
        print(f"Error on site request. Status code: {response.status_code}")
        return []

# /predict command
def predict(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    try:
        # Read multipliers from CSV
        file_csv = 'moltiplicatori.csv'
        ultimi_moltiplicatori = leggi_moltiplicatori_da_csv(file_csv)

        # Prediction next multiplier
        prossimo_moltiplicatore = previsione_prossimo_moltiplicatore(ultimi_moltiplicatori)

        # Send prediction to bot
        context.bot.send_message(chat_id=chat_id, text=f"Next multiplier will be {prossimo_moltiplicatore}")

    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text="Error.")

# Read csv file
def leggi_moltiplicatori_da_csv(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df['moltiplicatore'].tolist()
    else:
        return []

# Updater and Handler
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Add Handler for /predict
dispatcher.add_handler(CommandHandler("predict", predict))

# Auto update last multiplier
file_csv = 'moltiplicatori.csv'
ultimi_moltiplicatori_da_sito = aggiorna_moltiplicatori_da_sito(file_csv)

# Avvia il bot
updater.start_polling()
updater.idle()