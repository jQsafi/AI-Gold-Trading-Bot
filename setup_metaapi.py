import os
import asyncio
from metaapi_cloud_sdk import MetaApi
from dotenv import load_dotenv

load_dotenv()

async def setup_account():
    token = os.getenv("META_API_TOKEN")
    if not token or token == "your_metaapi_token_here":
        print("Error: Please set META_API_TOKEN in your .env file first.")
        return

    api = MetaApi(token)
    
    login = os.getenv("MT5_LOGIN")
    password = os.getenv("MT5_PASSWORD")
    server = os.getenv("MT5_SERVER") # e.g. Exness-MT5Trial6

    print(f"Attempting to register {login} on {server} with MetaAPI...")

    try:
        account = await api.metatrader_account_api.create_account({
            'name': 'Exness Demo Gold Bot',
            'type': 'cloud',
            'login': login,
            'password': password,
            'server': server,
            'platform': 'mt5',
            'application': 'MetaApi',
            'magic': 123456
        })
        
        print("\n" + "="*30)
        print("SUCCESS! Account Registered.")
        print(f"MetaAPI Account ID: {account['id']}")
        print("="*30)
        print("\nPlease copy this Account ID into your .env file as META_API_ACCOUNT_ID")
        
    except Exception as e:
        print(f"\nError registering account: {e}")
        print("Tip: Make sure the Server Name (e.g. Exness-MT5Trial10) is exactly correct.")

if __name__ == "__main__":
    asyncio.run(setup_account())
