import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from openpyxl import Workbook
from datetime import datetime
from tqdm import tqdm  # Importando tqdm

# Configuração do WebDriver para suprimir logs
options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("log-level=3")  # Define o nível de log como "warning" (3)
driver = webdriver.Chrome(options=options)

# Lista de links dos prédios
urls_predios = [
    "https://www.quintoandar.com.br/condominio/be-urban-metro-brooklin-jardim-das-acacias-sao-paulo-ed5zsjog6d"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# Criar uma nova pasta de trabalho do Excel
wb = Workbook()

# Ativar a planilha ativa
ws = wb.active

# Adicionar cabeçalhos
ws.append(['Empreendimento', 'Metragem', 'Aluguel', 'Condomínio', 'IPTU', 'Seguro Incêndio',
           'Taxa de Serviço', 'Valor Total', 'Data de Publicação', 'Link', 'URL do prédio'])

# Barra de progresso para URLs de prédios
for url_prédio in tqdm(urls_predios, desc="Processando prédios"):
    requisicao = requests.get(url_prédio, headers=headers)
    driver.get(url_prédio)
    html = driver.page_source
    site = BeautifulSoup(html, "html.parser")
    url_apartamentos = site.find_all("a", href=True)

    elemento = site.find(
        'h3', class_='CozyTypography xih2fc wIyEP2 _8JKqPG r4Q8xM')

    # Lista para armazenar os links filtrados
    links_filtrados = []

    padrao = r"/imovel/[^/]+/alugar"
    url_apartamentos_filtrados = [url_prédio["href"]
                                  for url_prédio in url_apartamentos if re.search(padrao, url_prédio["href"])]

    url_apartamentos_formatados = [
        "https://www.quintoandar.com.br" + url_prédio for url_prédio in url_apartamentos_filtrados]

    # Adicionando os links filtrados à lista com barra de progresso
    for link in tqdm(url_apartamentos_formatados, desc="Processando apartamentos", leave=False):
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            if elemento.get_text()[39:] in soup.get_text():
                links_filtrados.append(link)

    # Adicionar dados coletados
    for link in links_filtrados:
        response = requests.get(link)
        if response.status_code == 200:
            soup_apartamento = BeautifulSoup(response.content, "html.parser")

            # Coletar informações específicas
            metro_quadrado = soup_apartamento.find(
                "p", class_="CozyTypography xih2fc EKXjIf Ci-jp3")
            metragem = metro_quadrado.get_text()[0:2].replace(
                '\xa0', '').strip() if metro_quadrado else "Metragem não encontrada"

            empreendimento = elemento.get_text(
            )[39:].replace('\xa0', '').strip()

            aluguel = soup_apartamento.find(
                "p", class_="CozyTypography xih2fc _72Hu5c wIyEP2 _8JKqPG r4Q8xM")
            aluguel_formatado = aluguel.get_text()[8:].replace(
                '\xa0', '').strip() if aluguel else "Aluguel não encontrado"

            valor_total = soup_apartamento.find(
                "p", class_="CozyTypography xih2fc wIyEP2 _8JKqPG r4Q8xM")
            valor_total_formatado = valor_total.get_text()[6:].replace(
                '\xa0', '').strip() if valor_total else "Valor total não encontrado"

            publicado = re.compile(r"Publicado há \d+")
            data_publicacao = soup_apartamento.find("span", string=publicado)
            data = data_publicacao.text.strip()[13:].replace(
                '\xa0', '') if data_publicacao else "Data de publicação não encontrada"

            # Condomínio,IPTU, Seguro Incêndio e Taxa de Serviço
            condominio_formatado = "Condomínio não encontrado"
            iptu_formatado = "IPTU não encontrado"
            seguro_formatado = "Seguro não encontrado"
            taxa_formatada = "Taxa de Serviço não encontrada"

            # Procurar todos os itens de lista que contêm as informações
            itens = soup_apartamento.find_all(
                "li", class_="PriceTable_listItem__ZmeJY")
            for item in itens:
                descricao = item.find(
                    "span", class_="PriceItem_buttonWrapper__j5wyB")  # Nome da taxa
                # Captura os elementos de valor
                valor_container = item.find_all(
                    "p", class_="CozyTypography xih2fc _72Hu5c Ci-jp3")

                # Certificar-se de que temos ao menos dois <p> para o valor desejado
                if descricao and len(valor_container) > 1:
                    descricao_texto = descricao.get_text(
                        strip=True).replace('\xa0', '')
                    valor_texto = valor_container[1].get_text(strip=True).replace(
                        '\xa0', '')  # Extrai o segundo <p>, que contém o valor

                    # Associar os valores aos campos apropriados
                    if "IPTU" in descricao_texto:
                        iptu_formatado = valor_texto
                    elif "Seguro incêndio" in descricao_texto:
                        seguro_formatado = valor_texto
                    elif "Condomínio" in descricao_texto:
                        condominio_formatado = valor_texto
                    elif "Taxa de serviço" in descricao_texto:
                        taxa_formatada = valor_texto
                    elif "Aluguel" in descricao_texto:
                        aluguel_formatado = valor_texto

            # Adicionar os dados à planilha
            ws.append([empreendimento, metragem, aluguel_formatado, condominio_formatado, iptu_formatado,
                       seguro_formatado, taxa_formatada, valor_total_formatado, data, link, url_prédio])

# Fechar o navegador
driver.quit()

# Salvar o arquivo Excel
agora = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
nome_arquivo = rf"Scripts\WebScrapping - Quinto Andar\Arquivos\ScrappyQA_{
    agora}.xlsx"
wb.save(nome_arquivo)
print(f"Arquivo salvo como '{nome_arquivo}'")