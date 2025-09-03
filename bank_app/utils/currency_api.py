
import requests
from datetime import datetime, timedelta

def get_cambio(moeda_origem: str, moeda_destino: str = 'BRL') -> float | None:
    """
    Busca a taxa de câmbio em tempo real de uma API pública.
    Retorna a taxa (float) ou None em caso de erro.
    """
    # Esta API retorna o valor de 1 unidade da moeda_origem em moeda_destino.
    # Ex: get_cambio('USD', 'BRL') retorna quantos Reais valem 1 Dólar.
    url = f"https://economia.awesomeapi.com.br/json/last/{moeda_origem}-{moeda_destino}"
    
    try:
        # Faz a requisição com um timeout para não travar o programa indefinidamente
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Lança um erro para respostas como 404 (Not Found) ou 500 (Server Error)
        
        data = response.json()
        
        # A chave da cotação na resposta é a junção das moedas (ex: 'USDBRL')
        chave_cotacao = f"{moeda_origem}{moeda_destino}"
        
        # 'bid' é o preço de "compra" da moeda, que é o que usamos para a conversão
        taxa = float(data[chave_cotacao]['bid'])
        return taxa
        
    except requests.exceptions.RequestException as e:
        # Erro de rede (sem internet, DNS, etc.)
        print(f"\n[ERRO DE REDE] Não foi possível conectar à API de cotação: {e}")
        return None
    except (KeyError, ValueError):
        # Erro de parsing (a resposta da API não veio como esperado ou a moeda não existe)
        print(f"\n[ERRO DE API] Não foi possível encontrar a cotação para a moeda '{moeda_origem}'.")
        return None