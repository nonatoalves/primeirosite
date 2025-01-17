import random
import matplotlib.pyplot as plt
import streamlit as st

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

# Função para gerar o gráfico
def generate_plot(results):
    caras = results.count("cara")
    coroas = results.count("coroa")
    labels = ["Cara", "Coroa"]
    sizes = [caras, coroas]
    
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    st.pyplot(fig)

# Configuração da interface Streamlit
st.title("Simulação de Lançamentos de Moeda")

# Formulário de entrada para o número de lançamentos
num_tosses = st.number_input("Número de lançamentos", min_value=1, value=100)

# Botão para rodar a simulação
if st.button("Simular"):
    results = simulate_coin_tosses(num_tosses)
    stats = analyze_results(results)

    # Exibir os resultados da simulação
    st.write(f"Total de Caras: {stats['total_caras']}")
    st.write(f"Total de Coroas: {stats['total_coroas']}")
    st.write(f"Porcentagem de Caras: {stats['percentage_caras']:.2f}%")
    st.write(f"Porcentagem de Coroas: {stats['percentage_coroas']:.2f}%")
    st.write(f"Maior sequência de Caras: {stats['max_cara_seq']}")
    st.write(f"Maior sequência de Coroas: {stats['max_coroa_seq']}")
    st.write(f"Maior Drawdown: {stats['max_drawdown']}")
    
    # Gerar gráfico da simulação
    generate_plot(results)
