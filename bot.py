import tweepy
import requests
import random
import time
import os
from dotenv import load_dotenv

load_dotenv()

# ====== CHAVES (vindas do Railway depois) ======
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_SECRET = os.getenv("X_ACCESS_SECRET")
HF_API_KEY = os.getenv("HF_API_KEY")

# ====== AUTENTICAÇÃO X ======
auth = tweepy.OAuth1UserHandler(
    X_API_KEY,
    X_API_SECRET,
    X_ACCESS_TOKEN,
    X_ACCESS_SECRET
)
api = tweepy.API(auth)

print("🤖 Bot iniciado com personalidade caótica...")

# ====== CONFIGURAÇÕES ======
PALAVRAS_CHAVE = [
    "segunda-feira", "odeio", "cansado", "trabalho", "vida adulta",
    "relacionamento", "ex", "academia", "estudar", "prova"
]

MAX_RESPOSTAS_POR_HORA = 6

HF_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

HEADERS = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# ====== FUNÇÃO IA ======
def gerar_resposta(tweet):
    prompt = f"""
Você é um bot do Twitter sarcástico, debochado e engraçado.
Responda com uma frase curta e criativa ao tweet:

Tweet: "{tweet}"
Resposta:
"""
    data = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 60,
            "temperature": 0.9
        }
    }

    try:
        resp = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=HEADERS,
            json=data,
            timeout=30
        )

        if resp.status_code == 200:
            return resp.json()[0]["generated_text"].split("Resposta:")[-1].strip()
    except:
        return None


# ====== LOOP PRINCIPAL ======
respostas_enviadas = 0
inicio = time.time()

while True:
    try:
        # reset limite por hora
        if time.time() - inicio > 3600:
            respostas_enviadas = 0
            inicio = time.time()

        if respostas_enviadas >= MAX_RESPOSTAS_POR_HORA:
            print("⏳ Limite por hora atingido")
            time.sleep(300)
            continue

        palavra = random.choice(PALAVRAS_CHAVE)
        tweets = api.search_tweets(q=palavra + " -filter:retweets", lang="pt", count=5)

        if not tweets:
            time.sleep(60)
            continue

        tweet = random.choice(tweets)
        texto = tweet.text
        user = tweet.user.screen_name

        resposta = gerar_resposta(texto)

        if resposta:
            api.update_status(
                status=f"@{user} {resposta}",
                in_reply_to_status_id=tweet.id
            )
            print(f"✔ Respondeu @{user}: {resposta}")
            respostas_enviadas += 1

        time.sleep(random.randint(120, 300))

    except Exception as e:
        print("Erro:", e)
        time.sleep(60)
