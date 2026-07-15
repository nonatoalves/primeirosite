from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from bs4 import BeautifulSoup
import json
from datetime import datetime
import concurrent.futures

app = Flask(__name__)
CORS(app, origins=['https://nonatoalves.com.br', 'https://www.nonatoalves.com.br', 'https://nonatoalves.netlify.app'])

class TJPEAuditoria:
    def __init__(self):
        self.session = requests.Session()
        # REDUZIR TIMEOUT PARA RESPOSTA MAIS RÁPIDA
        self.session.timeout = 15
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
        self._cache_viewstate = None
        self._cache_timestamp = None
        
    def _get_viewstate(self):
        """Obtém ViewState com cache para evitar múltiplas requisições"""
        # Cache por 5 minutos
        if self._cache_viewstate and self._cache_timestamp:
            if (datetime.now() - self._cache_timestamp).seconds < 300:
                self.viewstate = self._cache_viewstate
                return True
        
        try:
            url = f"{self.base_url}/xhtml/manterConsultaSalario/consultaSalario.xhtml"
            response = self.session.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            v = soup.find('input', {'name': 'javax.faces.ViewState'})
            if v:
                self.viewstate = v.get('value')
                self._cache_viewstate = self.viewstate
                self._cache_timestamp = datetime.now()
                return True
            return False
        except:
            return False
    
    def consultar_mes(self, mes, ano='2026', nome=''):
        """Consulta um mês específico com timeout reduzido"""
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
            # TIMEOUT REDUZIDO PARA 15 SEGUNDOS
            response = self.session.post(url, data=payload, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extrair_dados(soup, mes, ano)
        except requests.Timeout:
            print(f"⏱️ Timeout ao consultar {mes}")
            return []
        except Exception as e:
            print(f"❌ Erro ao consultar {mes}: {e}")
            return []
    
    def _extrair_dados(self, soup, mes, ano):
        """Extrai dados da tabela de forma otimizada"""
        dados = []
        tabela = soup.find('table', {'id': 'j_id22:j_id49'})
        if not tabela:
            tabela = soup.find('table', class_='rich-table')
        if not tabela:
            return dados
        
        # Extrair todas as linhas da tabela
        for linha in tabela.find_all('tr'):
            if 'rich-table-header' in linha.get('class', []):
                continue
            
            celulas = linha.find_all('td')
            if len(celulas) < 3:
                continue
            
            # Pegar os valores diretamente pelas posições
            nome_servidor = self._limpar_texto(celulas[0].get_text(strip=True))
            
            if not nome_servidor:
                continue
            
            cargo = self._limpar_texto(celulas[1].get_text(strip=True)) if len(celulas) > 1 else ''
            lotacao = self._limpar_texto(celulas[2].get_text(strip=True)) if len(celulas) > 2 else ''
            
            # Otimizar: tentar apenas coluna 15 primeiro (mais comum)
            rendimento = 0
            if len(celulas) > 15:
                rendimento = self._converter_valor(celulas[15].get_text(strip=True))
            
            # Fallback rápido
            if rendimento == 0 and len(celulas) > 14:
                rendimento = self._converter_valor(celulas[14].get_text(strip=True))
            
            dados.append({
                'Nome': nome_servidor,
                'Cargo': cargo,
                'Lotação': lotacao,
                'Rendimento_Liquido': rendimento,
                'Mês': mes,
                'Ano': ano
            })
        
        return dados
    
    def _limpar_texto(self, texto):
        """Remove tags HTML e caracteres especiais de forma otimizada"""
        # Otimizado: usar replace em vez de regex para melhor performance
        texto = texto.replace('&ordf;', 'º').replace('&ordm;', 'º')
        texto = texto.replace('&ccedil;', 'ç').replace('&atilde;', 'ã')
        texto = texto.replace('&otilde;', 'õ').replace('&aacute;', 'á')
        texto = texto.replace('&eacute;', 'é').replace('&iacute;', 'í')
        texto = texto.replace('&oacute;', 'ó').replace('&uacute;', 'ú')
        texto = texto.replace('&acirc;', 'â').replace('&ecirc;', 'ê')
        texto = texto.replace('&ocirc;', 'ô').replace('&ucirc;', 'û')
        texto = texto.replace('&nbsp;', ' ').replace('&amp;', '&')
        texto = texto.replace('&lt;', '<').replace('&gt;', '>')
        return texto.strip()
    
    def _converter_valor(self, texto):
        """Converte R$ 10.201,54 para float de forma otimizada"""
        try:
            # Otimizado: remove apenas o necessário
            if 'R$' in texto:
                texto = texto.replace('R$', '').replace('r$', '').strip()
                texto = texto.replace('.', '').replace(',', '.')
                if texto and texto != '0.00' and texto != '0':
                    return float(texto)
            return 0
        except:
            return 0
    
    def consultar_todos_servidores(self, ano='2026'):
        """Consulta todos os meses em paralelo para maior velocidade"""
        todos = []
        
        # Usar ThreadPoolExecutor para consultar meses em paralelo
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Criar lista de tarefas
            futures = []
            for mes in self.meses:
                future = executor.submit(self.consultar_mes, mes, ano, '')
                futures.append((mes, future))
            
            # Coletar resultados
            for mes, future in futures:
                try:
                    dados = future.result(timeout=20)
                    if dados:
                        todos.extend(dados)
                        print(f"✅ {mes}: {len(dados)} registros")
                except concurrent.futures.TimeoutError:
                    print(f"⏱️ Timeout em {mes}")
                except Exception as e:
                    print(f"❌ Erro em {mes}: {e}")
        
        return todos
    
    def consultar_por_nome(self, nome, ano='2026'):
        """Consulta meses em paralelo para busca por nome"""
        todos = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for mes in self.meses:
                future = executor.submit(self.consultar_mes, mes, ano, nome)
                futures.append((mes, future))
            
            for mes, future in futures:
                try:
                    dados = future.result(timeout=20)
                    if dados:
                        todos.extend(dados)
                        print(f"✅ {mes}: {len(dados)} registros para '{nome}'")
                except concurrent.futures.TimeoutError:
                    print(f"⏱️ Timeout em {mes}")
                except Exception as e:
                    print(f"❌ Erro em {mes}: {e}")
        
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
                    'Lotacao': d['Lotação'],
                    'meses': {}
                }
            servidores[chave]['meses'][d['Mês']] = d['Rendimento_Liquido']
        
        resultado = []
        for chave, s in servidores.items():
            linha = {
                'Nome': s['Nome'],
                'Cargo': s['Cargo'],
                'Lotacao': s['Lotacao']
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