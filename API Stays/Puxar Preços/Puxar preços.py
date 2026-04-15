from datetime import datetime
import requests

# Lista de listings
listing_ids = ["IF06J"]

# Parâmetros de data
date_from = "2026-04-14"
date_to = "2026-04-18"

headers = {
    "Accept": "application/json",
    "Authorization": "Basic NzFhYTQ4N2U6MjYyNmVkOTc="
}

for listing_id in listing_ids:
    url = f"https://housi.stays.com.br/external/v1/calendar/listing/{listing_id}?from={date_from}&to={date_to}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        for day in data:
            # 🔹 Conversão da data
            data_iso = day["date"]  # 2026-04-14
            data_br = datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")

            print(f"\nListing: {listing_id}")
            print(f"Data: {data_br}")
            print(f"Disponibilidade: {day['avail']}")
            print("Preços:")

            for price in day.get("prices", []):
                currencies = price.get("_mcval", {})
                print(
                    f"  - minStay = {price.get('minStay')} | "
                    f"Preço = {currencies.get('BRL')}"
                )

            print("-" * 40)

    except requests.exceptions.RequestException as e:
        print(f"\nErro no listing {listing_id}: {e}")