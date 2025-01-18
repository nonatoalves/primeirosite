import random
import matplotlib.pyplot as plt
import csv

def simulate_coin_tosses(num_tosses):
    results = []
    for _ in range(num_tosses):
        results.append(random.choice(["cara", "coroa"]))
    return results

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

def save_to_csv(results):
    filename = "coin_tosses.csv"
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Resultado"])  # Cabeçalho
        for result in results:
            writer.writerow([result])
    print(f"Arquivo CSV gerado: {filename}")

def main():
    num_tosses = 1000000  # Número de lançamentos
    results = simulate_coin_tosses(num_tosses)
    stats = analyze_results(results)

    # Exibindo os resultados para o Excel sem espaços
    print("Resultado\tSequência\tSaldo\tDrawdown")
    for result, seq, saldo, drawdown in zip(results, stats["sequence"], stats["balance"], stats["drawdowns"]):
        print(f"{result}\t\t{seq}\t\t{saldo}\t{drawdown}")

    print("\nResumo Estatístico:")
    print(f"Total de caras: {stats['total_caras']}")
    print(f"Total de coroas: {stats['total_coroas']}")
    print(f"Maior sequência de caras: {stats['max_cara_seq']}")
    print(f"Maior sequência de coroas: {stats['max_coroa_seq']}")
    print(f"Maior drawdown: {stats['max_drawdown']}")
    print(f"Porcentagem de caras: {stats['percentage_caras']:.2f}%")
    print(f"Porcentagem de coroas: {stats['percentage_coroas']:.2f}%")

    # Gerar arquivo CSV com resultados
    save_to_csv(results)

    # Plotando gráfico de Saldo Acumulado e Drawdown
    plt.figure(figsize=(10, 6))

    # Saldo acumulado de caras - coroas
    plt.plot(stats['balance'], label='Saldo Acumulado (Cara - Coroa)', color='blue', alpha=0.7)
    
    # Drawdown
    plt.plot(stats['drawdowns'], label='Drawdown', color='red', linestyle='--')

    # Marcando áreas de "Cara" dominando e "Coroa" dominando
    plt.fill_between(range(len(stats['balance'])), stats['balance'], 0, where=[x >= 0 for x in stats['balance']],
                     color='green', alpha=0.2, label='Cara Dominando')
    plt.fill_between(range(len(stats['balance'])), stats['balance'], 0, where=[x < 0 for x in stats['balance']],
                     color='orange', alpha=0.2, label='Coroa Dominando')

    plt.title('Gráfico de Saldo Acumulado e Drawdown ao longo dos Lançamentos')
    plt.xlabel('Número de Lançamentos')
    plt.ylabel('Saldo Acumulado / Drawdown')
    plt.grid(True)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()