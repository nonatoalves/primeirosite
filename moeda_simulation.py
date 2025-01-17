import random
import matplotlib.pyplot as plt
import csv

# Função que simula os lançamentos de moedas
def simulate_coin_tosses(num_tosses):
    results = []
    for _ in range(num_tosses):
        results.append(random.choice(["cara", "coroa"]))
    return results

# Função que analisa os resultados
def analyze_results(results):
    total_caras = results.count("cara")
    total_coroas = results.count("coroa")
    
    # Calcular as porcentagens de "cara" e "coroa"
    percentage_caras = (total_caras / len(results)) * 100
    percentage_coroas = (total_coroas / len(results)) * 100
    
    # Contar a sequência em tempo real
    cara_seq = 0
    coroa_seq = 0
    max_cara_seq = 0
    max_coroa_seq = 0
    sequence = []

    # Calcular o saldo acumulado (cara vs coroa)
    balance = []  # Lista para armazenar o "balance" de caras vs coroas
    cara_count = 0
    coroa_count = 0

    for toss in results:
        if toss == "cara":
            cara_seq += 1
            coroa_seq = 0
            max_cara_seq = max(max_cara_seq, cara_seq)
            cara_count += 1
        else:
            coroa_seq += 1
            cara_seq = 0
            max_coroa_seq = max(max_coroa_seq, coroa_seq)
            coroa_count += 1
        sequence.append(cara_seq if toss == "cara" else coroa_seq)
        balance.append(cara_count - coroa_count)

    # Cálculo do Drawdown
    peak = balance[0]
    drawdowns = [0]
    for value in balance[1:]:
        if value > peak:
            peak = value
        drawdowns.append(peak - value)
    
    max_drawdown = max(drawdowns)
    
    return {
        "total_caras": total_caras,
        "total_coroas": total_coroas,
        "max_cara_seq": max_cara_seq,
        "max_coroa_seq": max_coroa_seq,
        "max_drawdown": max_drawdown,
        "percentage_caras": percentage_caras,
        "percentage_coroas": percentage_coroas,
        "sequence": sequence,
        "balance": balance,
        "drawdowns": drawdowns
    }

# Função que gera o CSV
def save_to_csv(results):
    filename = "coin_tosses.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Resultado"])  # Cabeçalho
        for result in results:
            writer.writerow([result])
    print(f"Arquivo CSV gerado: {filename}")

# Função de simulação principal
def simulate(num_tosses):
    results = simulate_coin_tosses(num_tosses)
    stats = analyze_results(results)

    return stats

# Esta função será chamada para gerar a simulação quando invocada do Flask
def get_simulation_result(num_tosses):
    results = simulate(num_tosses)
    return results
