import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import telebot

# Telegram bot token
TOKEN = '6693574970:AAHPcGJQUWLZC0_2Oid9ve8ONDKnIzCxrSY'

# Inizializza il bot
bot = telebot.TeleBot(TOKEN)

# Funzione per ottenere gli ultimi 50 moltiplicatori dal sito e aggiornare il file CSV
def aggiorna_moltiplicatori_da_sito(file_csv):
    url = "https://roobet.party/crash"
    
    # Effettua la richiesta HTTP al sito
    response = requests.get(url)
    
    if response.status_code == 200:
        # Analizza l'HTML con BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Trova gli elementi contenenti i moltiplicatori
        moltiplicatori_elements = soup.find_all("div", class_="crash-history-item")

        # Estrai gli ultimi 50 moltiplicatori
        ultimi_moltiplicatori = [float(elem.text) for elem in moltiplicatori_elements[:50]]

        # Aggiorna o crea il file CSV
        if os.path.exists(file_csv):
            df = pd.read_csv(file_csv)
            df = pd.concat([pd.DataFrame({'moltiplicatore': ultimi_moltiplicatori}), df], ignore_index=True)
            df = df.drop_duplicates(subset=['moltiplicatore']).head(50)  # Rimuovi duplicati e mantieni gli ultimi 50
        else:
            df = pd.DataFrame({'moltiplicatore': ultimi_moltiplicatori})

        df.to_csv(file_csv, index=False)

        return ultimi_moltiplicatori
    else:
        print(f"Errore nella richiesta al sito. Codice di stato: {response.status_code}")
        return []

# /predict command
@bot.message_handler(commands=['predict'])
def predict(message):
    chat_id = message.chat.id
    try:
        # Read multipliers from CSV
        file_csv = 'moltiplicatori.csv'
        ultimi_moltiplicatori = leggi_moltiplicatori_da_csv(file_csv)

        # Prediction next multiplier
        prossimo_moltiplicatore = previsione_prossimo_moltiplicatore(ultimi_moltiplicatori)

        # Send prediction to bot
        bot.send_message(chat_id, f"Next multiplier will be {prossimo_moltiplicatore}")

    except Exception as e:
        bot.send_message(chat_id, "Error.")

# Funzione per leggere i moltiplicatori da un file CSV
def leggi_moltiplicatori_da_csv(file_path):
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df['moltiplicatore'].tolist()
    else:
        return []

# Aggiungi la funzione per aggiornare gli ultimi moltiplicatori dal sito quando si avvia il bot
file_csv = 'moltiplicatori.csv'
ultimi_moltiplicatori_da_sito = aggiorna_moltiplicatori_da_sito(file_csv)

# Avvia il bot
bot.polling()
