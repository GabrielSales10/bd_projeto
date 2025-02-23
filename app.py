from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2.extras import RealDictCursor
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados
DB_CONFIG = {
    "dbname": "rodoviaria",
    "user": "gabriel",
    "password": "#800VSea1000@",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/cadastro-venda')
def cadastro_venda():
    return render_template('cadastro_venda.html')  # Página para o formulário de cadastro

@app.route("/listar_vendas")
def listar_vendas_page():
    return render_template("listar_vendas.html")


@app.route('/vendas', methods=['GET'])
def listar_vendas():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM vendas;")
        vendas = cur.fetchall()
        cur.close()
        conn.close()

        return jsonify(vendas)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para inserir uma venda
@app.route("/vendas", methods=["POST"])
def inserir_venda():
    data = request.json
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO Vendas (onibus_id, passageiro_id, cidade_partida_id, cidade_destino_id, data_viagem, numero_assento, preco)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """,
            (data["onibus_id"], data["passageiro_id"], data["cidade_partida_id"],
             data["cidade_destino_id"], data["data_viagem"], data["numero_assento"], data["preco"])
        )
        venda_id = cur.fetchone()["id"]
        conn.commit()
        return jsonify({"id": venda_id, "message": "Venda inserida com sucesso!"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()


@app.route("/editar_venda")
def editar_venda_page():
    venda_id = request.args.get("id")  # Obtém o ID da venda da URL
    if not venda_id:
        return "ID da venda não fornecido", 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Vendas WHERE id = %s", (venda_id,))
    venda = cur.fetchone()
    cur.close()
    conn.close()

    if not venda:
        return "Venda não encontrada", 404

    return render_template("editar_venda.html", venda=venda)


# # Rota para obter os dados de uma venda específica
# @app.route("/vendas/<int:venda_id>", methods=["GET"])
# def obter_venda(venda_id):
#     try:
#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=RealDictCursor)  # Retorna um dicionário
#         cur.execute("SELECT * FROM Vendas WHERE id = %s", (venda_id,))
#         venda = cur.fetchone()
#         cur.close()
#         conn.close()

#         if not venda:
#             return jsonify({"error": "Venda não encontrada"}), 404

#         return jsonify(venda)  # Retorna os dados da venda como JSON
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# Rota para excluir uma venda
@app.route("/vendas/<int:venda_id>", methods=["DELETE"])
def excluir_venda(venda_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM Vendas WHERE id=%s", (venda_id,))
        conn.commit()
        return jsonify({"message": "Venda excluída com sucesso!"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

# Rota para buscar vendas por passageiro
@app.route("/vendas/passageiro/<int:passageiro_id>", methods=["GET"])
def buscar_vendas_por_passageiro(passageiro_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM Vendas WHERE passageiro_id=%s", (passageiro_id,))
        vendas = cur.fetchall()
        return jsonify(vendas)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)