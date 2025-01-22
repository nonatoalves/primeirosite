from flask import Flask, request, jsonify, send_file
import os
import matplotlib.pyplot as plt
from moeda_simulation import simulate_coin_tosses, analyze_results

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Simulação de Lançamento de Moeda</h1>
    <form action="/simulate" method="get">
        <label for="num_tosses">Número de Lançamentos:</label>
        <input type="number" id="num_tosses" name="num_tosses" min="1" value="100">
        <button type="submit">Simular</button>
    </form>
    """

@app.route('/simulate', methods=['GET'])
def simulate():
    num_tosses = int(request.args.get('num_tosses', 100))
    results = simulate_coin_tosses(num_tosses)
    stats = analyze_results(results)

    # Gerar gráfico
    plt.figure(figsize=(10, 6))
    plt.plot(stats['balance'], label='Saldo Acumulado (Cara - Coroa)', color='blue', alpha=0.7)
    plt.plot(stats['drawdowns'], label='Drawdown', color='red', linestyle='--')
    for flip in stats['flip_points']:
        plt.scatter(flip, stats['balance'][flip], color='red', label='Virada no Saldo' if flip == stats['flip_points'][0] else "", zorder=5)
    plt.fill_between(range(len(stats['balance'])), stats['balance'], 0, where=[x >= 0 for x in stats['balance']],
                     color='green', alpha=0.2, label='Cara Dominando')
    plt.fill_between(range(len(stats['balance'])), stats['balance'], 0, where=[x < 0 for x in stats['balance']],
                     color='orange', alpha=0.2, label='Coroa Dominando')
    plt.title('Gráfico de Saldo Acumulado e Drawdown ao longo dos Lançamentos')
    plt.xlabel('Número de Lançamentos')
    plt.ylabel('Saldo Acumulado / Drawdown')
    plt.grid(True)
    plt.legend()
    graph_path = "static/graph.png"
    plt.savefig(graph_path)
    plt.close()

    return jsonify({
        "total_caras": stats["total_caras"],
        "total_coroas": stats["total_coroas"],
        "max_cara_seq": stats["max_cara_seq"],
        "max_coroa_seq": stats["max_coroa_seq"],
        "max_drawdown": stats["max_drawdown"],
        "percentage_caras": stats["percentage_caras"],
        "percentage_coroas": stats["percentage_coroas"],
        "total_flips": stats["total_flips"],
        "graph_url": f"/{graph_path}"
    })

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_file(os.path.join('static', filename))

if __name__ == "__main__":
    app.run(debug=True)
