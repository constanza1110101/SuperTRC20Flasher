import json
import requests
from tronpy import Tron
from tronpy.keys import PrivateKey

# 📡 Cliente TRON
client = Tron()

# 🔐 Clave privada y API Key directamente en el script
PRIVATE_KEY_HEX = "bbdf1f03f1a253cd29e5bb593934bb6fe821233ac643b35986c4c356597c8ab7"  # Inserta tu clave privada aquí
API_KEY = "f0c685b1-749c-4d01-963f-dab13e927657"  # Inserta tu API key de ChainGateway aquí

# 🧾 Crear la clave privada y la dirección
private_key = PrivateKey(bytes.fromhex(PRIVATE_KEY_HEX))
direccion_origen = private_key.public_key.to_base58check_address()

# 💼 Datos de la transacción (modificar según sea necesario)
direccion_destino = input("Enter the receiving address: ")  # Dirección de destino
monto = int(input("Enter the amount to send: "))  # Cantidad de USDT a enviar
fee_limite = int(input("Enter the transaction fee (in TRX): "))  # Límite de fee (TRX)

# Verificar formato de la dirección de contrato TRC20
contract_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # Dirección del contrato TRC20
try:
    # Verificar si la dirección del contrato es válida
    client.get_contract(contract_address)
    print(f"✅ La dirección del contrato {contract_address} es válida.")
except Exception as e:
    print(f"❌ Error: La dirección del contrato no es válida. {e}")
    exit()

# 🧾 Crear y firmar la transacción
contract = client.get_contract(contract_address)
txn = (
    contract.functions.transfer(direccion_destino, monto)
    .with_owner(direccion_origen)
    .fee_limit(fee_limite)
    .build()
    .sign(private_key)
)

# 🧩 Crear el payload para la solicitud a ChainGateway
payload = {
    "contractAddress": contract_address,
    "privatekey": PRIVATE_KEY_HEX,  # No es recomendable enviar la clave privada en el payload
    "from": direccion_origen,
    "to": direccion_destino,
    "amount": monto,
    "fee_limit": fee_limite
}

# 🛠️ Headers de la solicitud a ChainGateway
headers = {
    "Accept": "application/json",
    "x-api-key": API_KEY
}

# 🧾 Mostrar detalles de la transacción
print(f"\n✅ Transacción firmada. TXID: {txn.txid}")
print("📦 Payload para ChainGateway:")
print(json.dumps(payload, indent=2))

# ❓ ¿Enviar la transacción a ChainGateway?
enviar = input("\n🚀 ¿Deseas enviar esta transacción ahora a través de ChainGateway? (s/n): ").lower()

if enviar == "s":
    print("\n📡 Enviando transacción a través de ChainGateway...")
    url = "https://api.chaingateway.io/v2/tron/transactions/trc20"  # Endpoint de ChainGateway
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Mostrar la respuesta del servidor
    if response.status_code == 200:
        print("✅ Transacción enviada con éxito.")
        print(response.json())  # Mostrar respuesta detallada del servidor
    else:
        print(f"❌ Error al enviar la transacción: {response.text}")
else:
    # 💾 Guardar el payload como un archivo JSON localmente
    from datetime import datetime
    nombre_archivo = f"trx_payload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(nombre_archivo, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"\n💾 Transacción no enviada. Payload guardado en archivo: {nombre_archivo}")
