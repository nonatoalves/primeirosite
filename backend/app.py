from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from bs4 import BeautifulSoup
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['https://nonatoalves.com.br', 'https://www.nonatoalves.com.br', 'https://nonatoalves.netlify.app'])


class TJPEAuditoria:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://www.tjpe.jus.br/consultasalario"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.tjpe.jus.br',
            'Referer': 'https://www.tjpe.jus.br/consultasalario/xhtml/manterConsultaSalario/consultaSalario.xhtml'
        }
        self.viewstate = None
        self.meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        
    def _get_viewstate(self):
        try:
            url = f"{self.base_url}/xhtml/manterConsultaSalario/consultaSalario.xhtml"
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            v = soup.find('input', {'name': 'javax.faces.ViewState'})
            if v:
                self.viewstate = v.get('value')
                return True
            return False
        except:
            return False
    
    def consultar_mes(self, mes, ano='2026', nome=''):
        if not self._get_viewstate():
            return []
        try:
            url = f"{self.base_url}/xhtml/manterConsultaSalario/consultaSalario.xhtml"
            payload = {
                'j_id22': 'j_id22',
                'j_id22:j_id32comboboxField': mes,
                'j_id22:j_id32': mes,
                'j_id22:j_id46comboboxField': ano,
                'j_id22:j_id46': ano,
                'j_id22:nome': nome,
                'j_id22:j_id51': 'Pesquisar',
                'javax.faces.ViewState': self.viewstate
            }
            response = self.session.post(url, data=payload, headers=self.headers, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extrair_dados(soup, mes, ano)
        except Exception as e:
            return []
    
    def _extrair_dados(self, soup, mes, ano):
        dados = []
        tabela = soup.find('table', {'id': 'j_id22:j_id49'})
        if not tabela:
            tabela = soup.find('table', class_='rich-table')
        if not tabela:
            return dados
        
        colunas = ['Nome', 'Cargo', 'Lotação', 'Remuneracao_Paradigma', 'Vantagens_Pessoais', 
                   'Subsidio_Funcao', 'Indenizacoes', 'Vantagens_Eventuais', 'Gratificacoes',
                   'Previdencia', 'Imposto_Renda', 'Descontos_Diversos', 'Retencao_Teto',
                   'Rendimento_Liquido', 'Remuneracao_Origem', 'Diarias']
        
        for linha in tabela.find_all('tr'):
            if 'rich-table-header' in linha.get('class', []):
                continue
            celulas = linha.find_all('td')
            if not celulas:
                continue
            
            linha_dados = {}
            for i, celula in enumerate(celulas):
                if i == 9 or i == 14:
                    continue
                if i < 9:
                    col_idx = i
                elif i > 9 and i < 14:
                    col_idx = i - 1
                elif i > 14:
                    col_idx = i - 2
                else:
                    continue
                if col_idx >= len(colunas):
                    continue
                
                link = celula.find('a')
                texto = link.get_text(strip=True) if link else celula.get_text(strip=True)
                
                if 'R$' in texto:
                    try:
                        valor = texto.replace('R$', '').replace('.', '').replace(',', '.').strip()
                        linha_dados[colunas[col_idx]] = float(valor) if valor else 0.0
                    except:
                        linha_dados[colunas[col_idx]] = texto
                else:
                    linha_dados[colunas[col_idx]] = texto
            
            if linha_dados.get('Nome'):
                linha_dados['Mês'] = mes
                linha_dados['Ano'] = ano
                dados.append(linha_dados)
        return dados
    
    def consultar_todos_servidores(self, ano='2026'):
        todos = []
        for mes in self.meses:
            dados = self.consultar_mes(mes, ano, nome='')
            if dados:
                todos.extend(dados)
        return todos
    
    def consultar_por_nome(self, nome, ano='2026'):
        todos = []
        for mes in self.meses:
            dados = self.consultar_mes(mes, ano, nome)
            if dados:
                todos.extend(dados)
        return todos
    
    def processar_pivot(self, dados):
        """Transforma dados em formato Pivot (um servidor por linha)"""
        servidores = {}
        for d in dados:
            chave = d['Nome'] + '|' + d['Cargo'] + '|' + d['Lotação']
            if chave not in servidores:
                servidores[chave] = {
                    'Nome': d['Nome'],
                    'Cargo': d['Cargo'],
                    'Lotação': d['Lotação'],
                    'meses': {}
                }
            servidores[chave]['meses'][d['Mês']] = d['Rendimento_Liquido'] / 100
        
        resultado = []
        for chave, s in servidores.items():
            linha = {
                'Nome': s['Nome'],
                'Cargo': s['Cargo'],
                'Lotação': s['Lotação']
            }
            total = 0
            for mes in self.meses:
                valor = s['meses'].get(mes, 0)
                linha[mes] = round(valor, 2)
                total += valor
            linha['Total'] = round(total, 2)
            resultado.append(linha)
        
        return resultado


@app.route('/')
def index():
    return jsonify({
        'status': 'online',
        'mensagem': 'API do TJPE - Auditoria de Rendimentos',
        'endpoints': {
            '/buscar': 'POST - Enviar nome, ano e mes',
            '/health': 'GET - Verificar status'
        }
    })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

@app.route('/buscar', methods=['POST'])
def buscar():
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        ano = data.get('ano', '2026')
        mes_filtro = data.get('mes', 'todos')
        
        auditoria = TJPEAuditoria()
        
        if nome:
            dados = auditoria.consultar_por_nome(nome, ano)
        else:
            dados = auditoria.consultar_todos_servidores(ano)
        
        pivot = auditoria.processar_pivot(dados)
        
        if mes_filtro != 'todos':
            pivot = [s for s in pivot if s.get(mes_filtro, 0) > 0]
        
        return jsonify({
            'success': True,
            'dados': pivot,
            'total': len(pivot)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)