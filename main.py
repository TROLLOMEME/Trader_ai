import os
import json
import openai
from dotenv import load_dotenv
from solders.keypair import Keypair
from solders.rpc.api import Client

# Load env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load keypair
with open("keypair.json", "r") as f:
    secret = json.load(f)
keypair = Keypair.from_bytes(bytes(secret))

# اتصال به سولانا
client = Client("https://api.mainnet-beta.solana.com")
balance = client.get_balance(keypair.pubkey())
print("Balance:", balance)

# گرفتن سیگنال از ChatGPT
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{
        "role": "system",
        "content": "You're a crypto trading bot. Analyze trending tokens on Solana and suggest 1 good buy signal with reason."
    }]
)
signal = response["choices"][0]["message"]["content"]
print("AI signal:", signal)
