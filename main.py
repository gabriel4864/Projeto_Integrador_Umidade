from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask('Umidade')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Senai%40134@127.0.0.1/db_umidade'

mybd = SQLAlchemy(app)

# ------------------------------------
# CRIAÇÃO DA TABELA

class Umi(mybd.Model):
    __tablename__ = 'LEITURA_UMIDADE'
    id_leitura = mybd.Column(mybd.Integer, primary_key=True)
    valor_umidade = mybd.Column(mybd.String(255))
    data_hora_leitura = mybd.Column(mybd.String(255))
    id_cidade = mybd.Column(mybd.String(255))
    id_periodo = mybd.Column(mybd.String(255))

    def to_json(self):
        return {
            "id_leitura": self.id_leitura,
            "valor_umidade": self.valor_umidade,
            "data_hora_leitura": self.data_hora_leitura,
            "id_cidade": self.id_cidade,
            "id_periodo": self.id_periodo
        }

# GET all umidades
@app.route('/umidade', methods=['GET'])
def seleciona_umidade():
    umidades = Umi.query.all()
    umidades_json = [umidade.to_json() for umidade in umidades]
    return gera_resposta(200, umidades_json, "Lista de umidades")

# GET umidade por ID
@app.route('/umidade/<id_umidade_pam>', methods=['GET'])
def seleciona_umidade_id(id_umidade_pam):
    umidade = Umi.query.filter_by(id_leitura=id_umidade_pam).first()
    if not umidade:
        return gera_resposta(404, {}, "ID não encontrado")
    return gera_resposta(200, umidade.to_json(), "Dado encontrado")

# POST nova umidade
@app.route('/umidade', methods=['POST'])
def criar_umidade():
    requisicao = request.get_json()
    try:
        umidade = Umi(
            id_leitura=requisicao['id_leitura'],
            valor_umidade=requisicao['valor_umidade'],
            data_hora_leitura=requisicao['data_hora_leitura'],
            id_cidade=requisicao['id_cidade'],  
            id_periodo=requisicao['id_periodo']  
        )
        mybd.session.add(umidade)
        mybd.session.commit()
        return gera_resposta(201, umidade.to_json(), "Criado com sucesso!")
    except Exception as e:
        print('Erro:', e)
        return gera_resposta(400, {}, "Erro ao cadastrar!")

# DELETE umidade
@app.route('/umidade/<id_umidade_pam>', methods=['DELETE'])
def deleta_leitura(id_umidade_pam):
    umidade = Umi.query.filter_by(id_leitura=id_umidade_pam).first()
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
@app.route("/umidade/<id_umidade_pam>", methods=['PUT'])
def atualiza_leitura(id_umidade_pam):
    umidade = Umi.query.filter_by(id_leitura=id_umidade_pam).first()
    if not umidade:
        return gera_resposta(404, {}, "Umidade não encontrada")

    requisicao = request.get_json()
    try:
        if 'valor_umidade' in requisicao:
            umidade.valor_umidade = requisicao['valor_umidade']  
        if 'data_hora_leitura' in requisicao:
            umidade.data_hora_leitura = requisicao['data_hora_leitura']  

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
