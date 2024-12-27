import pandas as pd
import numpy as np

# Função para carregar os dados e tratar a coluna datetime
def carregar_dados(caminho):
    # Carregar os dados do arquivo
    df = pd.read_excel(caminho)
    
    # Exibir as colunas para diagnóstico
    print("Colunas encontradas:", df.columns)
    
    # Garantir que o nome das colunas está correto (ajustando para o formato esperado)
    if 'mês' in df.columns:  # Se "mês" estiver com acento
        df['datetime'] = pd.to_datetime(df[['ano', 'dia', 'mês', 'hora']].astype(str).agg('-'.join, axis=1))
    else:  # Se o nome da coluna for "mes" sem acento
        df['datetime'] = pd.to_datetime(df[['ano', 'dia', 'mes', 'hora']].astype(str).agg('-'.join, axis=1))
    
    # Definir datetime como índice
    df.set_index('datetime', inplace=True)
    
    return df

# Função para executar o teste de compra e venda com base nas velas
def testar_operacoes(df):
    # Inicializando variáveis para controle de trades
    resultados = []
    saldo = 0.0
    
    for dia, dia_data in df.groupby(df.index.date):
        print(f"Analisando o dia {dia}")
        
        # Filtrando apenas os dados entre 10:00 e 17:00
        periodo = dia_data.between_time('10:00', '17:00')
        
        if len(periodo) < 2:
            continue
        
        # Começar o trade na vela das 10:00
        entrada = None
        sentido_trade = None
        
        for i in range(1, len(periodo)):
            vela_atual = periodo.iloc[i]
            vela_anterior = periodo.iloc[i-1]
            
            if entrada is None:
                # Se a vela das 10:00 for de baixa, entra em venda; se for de alta, entra em compra
                if vela_anterior['close'] > vela_anterior['open']:
                    entrada = vela_anterior['close']  # Preço de fechamento da vela anterior
                    sentido_trade = 'compra'
                else:
                    entrada = vela_anterior['close']
                    sentido_trade = 'venda'
            
            # Verificar se o trade precisa ser encerrado
            if sentido_trade == 'compra' and vela_atual['close'] < vela_atual['open']:
                # Vela de baixa cancela a compra e realiza o lucro ou prejuízo
                resultado = vela_atual['close'] - entrada
                resultados.append(resultado)
                saldo += resultado
                entrada = None
                sentido_trade = None
            elif sentido_trade == 'venda' and vela_atual['close'] > vela_atual['open']:
                # Vela de alta cancela a venda e realiza o lucro ou prejuízo
                resultado = entrada - vela_atual['close']
                resultados.append(resultado)
                saldo += resultado
                entrada = None
                sentido_trade = None

        # Finaliza o dia com o saldo atual
        print(f"Resultado do dia {dia}: {saldo:.2f}")
    
    # Relatório final
    print(f"Lucro/perda total: {saldo:.2f}")
    print(f"Resultados por operação: {resultados}")

# Função principal para carregar dados e testar as operações
def main():
    caminho_arquivo = 'C:/Users/maver/Downloads/site2/winhist.xlsx'
    
    # Carregar os dados
    df = carregar_dados(caminho_arquivo)
    
    # Realizar o teste de compra e venda
    testar_operacoes(df)

# Chamar a função principal
if __name__ == "__main__":
    main()
