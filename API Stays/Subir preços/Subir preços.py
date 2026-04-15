import pandas as pd
import requests

arquivo = "API Stays\\Subir preços\\precos.xlsx"
aba = "Sheet1"

df = pd.read_excel(arquivo, sheet_name=aba)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": "Basic NzFhYTQ4N2U6MjYyNmVkOTc="
}

def validar_preco(valor):
    try:
        valor = float(valor)
        return valor > 0
    except:
        return False

for _, row in df.iterrows():
    listing_id = row["id"]
    data_iso = pd.to_datetime(row["data"], dayfirst=True).strftime("%Y-%m-%d")

    prices = []

    for col in df.columns:
        if isinstance(col, str) and col.startswith("minStay"):
            valor = row.get(col)

            if pd.notna(valor) and validar_preco(valor):
                try:
                    min_stay = int(col.replace("minStay", ""))
                    prices.append({
                        "minStay": min_stay,
                        "_f_val": float(valor)
                    })
                except ValueError:
                    print(f"SKIP | coluna inválida: {col}")

    if not prices:
        print(f"SKIP | {listing_id} | {data_iso} | sem preços")
        continue

    prices = sorted(prices, key=lambda x: x["minStay"])

    url = f"https://housi.stays.com.br/external/v1/calendar/listing/{listing_id}/prices"

    payload = {
        "from": data_iso,
        "to": data_iso,
        "prices": prices
    }

    try:
        response = requests.patch(url, headers=headers, json=payload)
        response.raise_for_status()

        print(f"OK | {listing_id} | {data_iso} | {prices}")
        print("Resposta:", response.json())

    except requests.exceptions.RequestException as e:
        print(f"ERRO | {listing_id} | {data_iso} | {e}")