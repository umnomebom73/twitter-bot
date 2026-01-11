import tweepy
import requests
import random
import time
import os
from dotenv import load_dotenv

# ====== CARREGAR VARIÁVEIS DO .env ======
load_dotenv()

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
    "Segunda-feira de novo… alguém mais? 😅",
    "Café forte e coração fraco ☕💔",
    "Procrastinação é meu superpoder 🦸‍♂️",
    "Vida adulta: Wi-Fi > oxigênio 😎",
    "Estudando ou dormindo? Pergunta difícil… 😴",
    "Relacionamento sério com minha cama 🛌❤️",
    "Trabalho ou sono? O dilema eterno 😭",
    "Alguém me lembra porque eu aceitei crescer? 🤔",
    "Hoje acordei, sobrevivi… já tá ótimo.",
    "Meu corpo pede férias, mas meu chefe não. 😬",
    "Café: 70% sobrevivência, 30% ilusão de produtividade.",
    "A vida é uma maratona… mas eu tô correndo só pro sofá.",
    "Estudando pra quê se o sono é inevitável? 😴",
    "Tentar ser adulto é tipo atualizar um software antigo: trava o tempo todo.",
    "Eu queria ter dinheiro ou coragem… mas só tenho Wi-Fi.",
    "O mundo tá girando, eu tô parado… no TikTok.",
    "Segunda-feira: a vingança do universo.",
    "Meu corpo pediu feriado, mas minha agenda disse não.",
    "Já é terça e eu ainda tô em modo zumbi 🧟‍♂️",
    "Alguém me explica como adultos fazem tudo sem chorar?",
    "Procrastinar é a arte de deixar o impossível pra depois.",
    "Vida adulta é pagar boletos e fingir que gosta.",
    "Trabalho duro ou só duro no trabalho? 🤨",
    "Meu café e eu: melhores amigos até o próximo boletim.",
    "Hoje vou ser produtivo… amanhã é que é dia certo.",
    "Estudando sério… no máximo por 5 minutos.",
    "Se o sono é ouro, tô milionário."
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
        else:
            print("Erro HF:", resp.status_code, resp.text)
    except Exception as e:
        print("Erro HF:", e)
    return None

# ====== LOOP PRINCIPAL ======
respostas_enviadas = 0
inicio = time.time()

while True:
    try:
        # Reset limite por hora
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

        # Delay aleatório entre 2 e 5 minutos
        time.sleep(random.randint(120, 300))

    except Exception as e:
        print("Erro:", e)
        time.sleep(60)
