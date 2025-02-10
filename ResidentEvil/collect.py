# %%

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd

headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'referer': 'https://www.residentevildatabase.com/personagens/ada-wong/',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        # 'cookie': '_gid=GA1.2.288801614.1738892407; _ga_DJLCSW50SC=GS1.1.1738892405.1.1.1738892460.5.0.0; _ga_D6NF5QC4QT=GS1.1.1738892406.1.1.1738892460.6.0.0; _ga=GA1.2.60111581.1738892406; FCNEC=%5B%5B%22AKsRol8Qm4mX9-iUvZoOJoGnFrGEVTMvfpY3GtruKs3qGv0As1myIw2OWVUeKQFPEXBwkFnM9saEJuJ7aQHgkXhW8IUny7s_8IciwnensLHNs7aEDX5L7o4iROtVaC8DFCeSDNewjyB-UNsNLO3dd6bzpjiaAQOghA%3D%3D%22%5D%5D',
    }

def  get_content(url):
    cookies = {
        '_gid': 'GA1.2.288801614.1738892407',
        '_ga_DJLCSW50SC': 'GS1.1.1738892405.1.1.1738892460.5.0.0',
        '_ga_D6NF5QC4QT': 'GS1.1.1738892406.1.1.1738892460.6.0.0',
        '_ga': 'GA1.2.60111581.1738892406',
        'FCNEC': '%5B%5B%22AKsRol8Qm4mX9-iUvZoOJoGnFrGEVTMvfpY3GtruKs3qGv0As1myIw2OWVUeKQFPEXBwkFnM9saEJuJ7aQHgkXhW8IUny7s_8IciwnensLHNs7aEDX5L7o4iROtVaC8DFCeSDNewjyB-UNsNLO3dd6bzpjiaAQOghA%3D%3D%22%5D%5D',
    }

    resp = requests.get((url), cookies=cookies, headers=headers)
    return resp

def get_basic_infos(soup):
    div_page = soup.find("div", class_="td-page-content")
    p = div_page.find_all("p")[1]
    ems = p.find_all("em")
    data = {}
    for i in ems:
        chave, valor, *_ = i.text.split(":")
        chave = chave.strip(" ")
        data[chave] = valor.strip(" ")


    return data

def get_aparicoes(soup):
    lis = (soup.find("div", class_="td-page-content")
        .find("h4")
        .find_next()
        .find_all("li"))

    aparicoes = [i.text for i in lis]
    return aparicoes

def get_personagem_info(url):
    resp = get_content(url)
    if resp.status_code != 200:
        print("Não foi possivel obter os dados")
        return {}
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    try:
        data = get_basic_infos(soup) or {}  # Garante que data nunca seja None
        data["aparicoes"] = get_aparicoes(soup) or []  # Garante que aparicoes nunca seja None
        return data
    except Exception as e:
        print(f"Erro ao processar os dados para {url}: {e}")
        return {}
    
def get_links():
    url = "https://www.residentevildatabase.com/personagens/"
    resp = requests.get(url, headers=headers)
    soup_personagens = BeautifulSoup(resp.text)
    ancoras = (soup_personagens.find("div", class_="td-page-content").find_all("a"))

    links = [i["href"] for i in ancoras]
    return links

links = get_links()
data = []
for i in tqdm(links):
    d = get_personagem_info(i)
    
    if d is None: 
        print("nenhum dado retornado")
    else:
        d["link"] = i
        nome = i.strip("/").split("/")[-1].replace("-", " ").title()
        d["Nome"] = nome
        data.append(d)

df = pd.DataFrame(data)
df
#%%

df.to_csv("dados_re.csv", index=False, sep=";")
df.to_parquet("dados_re.parquet", index=False)
df.to_pickle("dados_re.pkl")
#%%
