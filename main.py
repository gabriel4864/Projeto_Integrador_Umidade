import datetime
from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import json
import paho.mqtt.client as mqtt
app = Flask('Umidade')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Senai%40134@127.0.0.1/db_umidade'

# server_name = 'datascience-gp7.mysql.database.azure.com'
# port = '3606'
# username = 'grupo7'
# password = 'Senai%40134'
# database = 'db_umidade'

# certificado = 'DigiCertGlobalRootG2.crt.pem'

# uri = f"mysql://{username}:{password}@{server_name}:{port}/{database}"
# ssl_certificado = f"?ssl_ca={certificado}"

# app.config['SQLALCHEMY_DATABASE_URI'] = uri + ssl_certificado

mybd = SQLAlchemy(app)


# ********************* CONEXÃO SENSORES *********************************

mqtt_data = {}


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("projeto_integrado/SENAI134/Cienciadedados/grupo1")

def on_message(client, userdata, msg):
    global mqtt_data
 # Decodifica a mensagem recebida de bytes para string
    payload = msg.payload.decode('utf-8')
   
    # Converte a string JSON em um dicionário Python
    mqtt_data = json.loads(payload)
   
    # Imprime a mensagem recebida
    print(f"Received message: {mqtt_data}")

    # Adiciona o contexto da aplicação para a manipulação do banco de dados
    with app.app_context():
        try:
            temperatura = mqtt_data.get('temperature')
            pressao = mqtt_data.get('pressure')
            altitude = mqtt_data.get('altitude')
            umidade = mqtt_data.get('humidity')
            co2 = mqtt_data.get('co2')
            timestamp_unix = mqtt_data.get('timestamp')

            if timestamp_unix is None:
                print("Timestamp não encontrado no payload")
                return

            # Converte timestamp Unix para datetime
            try:
                timestamp = datetime.fromtimestamp(int(timestamp_unix), tz=datetime.timezone.utc)
            except (ValueError, TypeError) as e:
                print(f"Erro ao converter timestamp: {str(e)}")
                return

            # Cria o objeto Registro com os dados
            new_data = Umi(
                temperatura=temperatura,
                pressao=pressao,
                altitude=altitude,
                umidade=umidade,
                co2=co2,
                tempo_registro=timestamp
            )

            # Adiciona o novo registro ao banco de dados
            mybd.session.add(new_data)
            mybd.session.commit()
            print("Dados inseridos no banco de dados com sucesso")

        except Exception as e:
            print(f"Erro ao processar os dados do MQTT: {str(e)}")
            mybd.session.rollback()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect("test.mosquitto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()




# ------------------------------------
# TABELA

class Umi(mybd.Model):
    __tablename__ = 'LEITURA'
    id_leitura = mybd.Column(mybd.Integer, primary_key=True)
    umidade = mybd.Column(mybd.String(255))
    temperatura = mybd.Column(mybd.String(255))
    pressao = mybd.Column(mybd.String(255))
    co2 = mybd.Column(mybd.String(255))

    def to_json(self):
        return {
            "id_leitura": self.id_leitura,
            "umidade": self.umidade,
            "temperatura": self.temperatura,
            "pressao": self.pressao,
            "co2": self.co2,
            "tempo_registro": self.tempo_registro
        }

# GET all umidades
@app.route('/leitura', methods=['GET'])
def seleciona_umidade():
    umidades = Umi.query.all()
    umidades_json = [umidade.to_json() for umidade in umidades]
    return gera_resposta(200, umidades_json, "Lista de umidades")

# GET umidade por ID
@app.route('/leitura/<id_leitura_pam>', methods=['GET'])
def seleciona_leitura_id(id_leitura_pam):
    umidade = Umi.query.filter_by(id_leitura=id_leitura_pam).first()
    if not umidade:
        return gera_resposta(404, {}, "ID não encontrado")
    return gera_resposta(200, umidade.to_json(), "Dado encontrado")

# POST nova umidade
@app.route('/leitura', methods=['POST'])
def criar_leitura():
    requisicao = request.get_json()
    try:
        umidade = Umi(
            id_leitura=requisicao['id_leitura'],
            valor_umidade=requisicao['valor_umidade'],
            temperatura = requisicao['temperatura'],
            pressao = requisicao['temperatura'],
            co2 = requisicao ['co2'],
            tempo_registro =requisicao['tempo_registro']

        )
        mybd.session.add(umidade)
        mybd.session.commit()
        return gera_resposta(201, umidade.to_json(), "Criado com sucesso!")
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, {}, "Erro ao cadastrar!")

# DELETE umidade
@app.route('/leitura/<id_leitura_pam>', methods=['DELETE'])
def deleta_leitura(id_leitura_pam):
    umidade = Umi.query.filter_by(id_leitura=id_leitura_pam).first()
    if not umidade:
        return gera_resposta(404, {}, "Umidade não encontrada")
    try:
        mybd.session.delete(umidade)
        mybd.session.commit()
        return gera_resposta(200, umidade.to_json(), "Deletado com sucesso!")
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, {}, "Erro ao deletar!")

# PUT umidade
@app.route("/leitura/<id_leitura_pam>", methods=['PUT'])
def atualiza_leitura(id_leitura_pam):
    umidade = Umi.query.filter_by(id_leitura=id_leitura_pam).first()
    if not umidade:
        return gera_resposta(404, {}, "Umidade não encontrada")

    requisicao = request.get_json()
    try:
        if 'umidade' in requisicao:
            umidade.umidade = requisicao['umidade']  
        if 'temperatura' in requisicao:
            umidade.temperatura = requisicao['temperatura']  
        if 'pressao' in requisicao:
            umidade.pressao = requisicao['pressao']  
        if 'co2' in requisicao:
            umidade.co2 = requisicao['co2']         
        if 'tempo_registro' in requisicao:
            umidade.tempo_registro = requisicao['tempo_registro']  

        mybd.session.commit()
        return gera_resposta(200, umidade.to_json(), "Umidade atualizada com sucesso!")
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, {}, "Erro ao atualizar!")

# -------------------------------------
# RESPOSTA PADRÃO

def gera_resposta(status, conteudo, mensagem=False):
    body = {}
    body["Lista de umidades"] = conteudo
    if mensagem:
        body['mensagem'] = mensagem

    return Response(json.dumps(body), status=status, mimetype='application/json')

app.run(port=5000, host='localhost', debug=True)
