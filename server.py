from flask import Flask, request, jsonify
import random
import string
import time

app = Flask(__name__)

salas = {}

# ---------------- PERGUNTAS ----------------
PERGUNTAS = [
    {
        "pergunta": q,
        "opcoes": op,
        "resposta": r
    }
    for (q, op, r) in [
        ("Quem foi considerada a primeira programadora da história?",
         ["Ada Lovelace", "Marie Curie", "Rosalind Franklin", "Jane Goodall"],
         "Ada Lovelace"),

        ("Quem criou o Teorema de Noether?", ["Ada Lovelace", "Emmy Noether", "Katherine Johnson", "Marie Curie"],
         'Emmy Noether'),
        ("Quem trabalhou na NASA calculando trajetórias espaciais?",
         ["Ada Lovelace", "Emmy Noether", "Katherine Johnson", "Grace Hopper"], "Katherine Johnson"),
        ("Qual cientista ajudou a missão Apollo 11?",
         ["Ada Lovelace", "Katherine Johnson", "Curie", "Noether"], "Katherine Johnson"),
        ("Quem trabalhou com Charles Babbage?",
         ["Ada Lovelace", "Curie", "Noether", "Franklin"], "Ada Lovelace"),
        ("Quem revolucionou a matemática moderna?",
         ["Noether", "Lovelace", "Johnson", "Curie"], "Noether"),
        ("Quem ajudou nos cálculos de foguetes?",
         ["Johnson", "Curie", "Lovelace", "Goodall"], "Johnson"),
        ("Quem criou o primeiro algoritmo?",
         ["Ada Lovelace", "Curie", "Johnson", "Noether"], "Ada Lovelace"),
        ("Quem foi matemática alemã famosa?",
         ["Noether", "Curie", "Lovelace", "Johnson"], "Noether"),
        ("Quem participou da corrida espacial?",
         ["Johnson", "Curie", "Noether", "Lovelace"], "Johnson"),

    ]
]
# ---------------- CRIAR SALA ----------------
@app.route("/criar_sala", methods=["POST"])
def criar_sala():
    dados = request.json

    def gerar_pin():
        return ''.join(random.choices(string.digits, k=4))

    pin = gerar_pin()

    while pin in salas:
        pin = gerar_pin()

    if not pin:
        return jsonify({"erro": "PIN não informado"})

    if pin in salas:
        return jsonify({"erro": "Sala já existe"})

    salas[pin] = {
        "jogadores": {},
        "iniciado": False,
        "pergunta_atual": 0,
        "inicio_pergunta": None,
        "tempo_pergunta": 10,
        "perguntas": random.sample(PERGUNTAS, len(PERGUNTAS))
    }

    return jsonify({"pin": pin})


# ---------------- ENTRAR ----------------
@app.route("/entrar", methods=["POST"])
def entrar():
    dados = request.json
    nome = dados["nome"]
    pin = dados["pin"]

    if pin not in salas:
        return jsonify({"erro": "Sala não existe"})

    if nome not in salas[pin]["jogadores"]:
        salas[pin]["jogadores"][nome] = 0

    return jsonify({"ok": True})


# ---------------- JOGADORES ----------------
@app.route("/jogadores/<pin>")
def jogadores(pin):
    if pin not in salas:
        return jsonify([])

    return jsonify(list(salas[pin]["jogadores"].keys()))


# ---------------- INICIAR ----------------
@app.route("/iniciar/<pin>")
def iniciar(pin):
    sala = salas.get(pin)

    if not sala:
        return {"erro": "Sala não existe"}

    if len(sala["jogadores"]) < 1:
        return {"erro": "Precisa de pelo menos 1 jogador"}

    sala["iniciado"] = True
    sala["pergunta_atual"] = 0
    sala["inicio_pergunta"] = time.time()

    return {"status": "ok"}


# ---------------- STATUS ----------------
@app.route("/status/<pin>")
def status(pin):
    sala = salas.get(pin)

    if not sala:
        return {"erro": "Sala não existe"}

    tempo_restante = 0

    if sala.get("inicio_pergunta"):
        tempo_passado = time.time() - sala["inicio_pergunta"]
        tempo_restante = max(0, sala["tempo_pergunta"] - tempo_passado)

        if tempo_restante <= 0:
            sala["pergunta_atual"] += 1
            sala["inicio_pergunta"] = time.time()

    pergunta = None

    if sala["pergunta_atual"] < len(sala["perguntas"]):
        pergunta = sala["perguntas"][sala["pergunta_atual"]]

    return {
        "iniciado": sala["iniciado"],
        "pergunta_index": sala["pergunta_atual"],
        "tempo": int(tempo_restante),
        "pergunta": pergunta,
        "ranking": sorted(
            sala["jogadores"].items(),
            key=lambda x: x[1],
            reverse=True
        )
    }


# ---------------- RESPONDER ----------------
@app.route("/responder", methods=["POST"])
def responder():
    data = request.json
    nome = data["nome"]
    pin = data["pin"]
    resposta = data["resposta"]

    sala = salas.get(pin)

    if not sala:
        return {"erro": "Sala não existe"}

    pergunta_atual = sala["pergunta_atual"]

    if pergunta_atual >= len(sala["perguntas"]):
        return {"erro": "Jogo acabou"}

    correta = sala["perguntas"][pergunta_atual]["resposta"]

    tempo_passado = time.time() - sala["inicio_pergunta"] if sala.get("inicio_pergunta") else 0
    tempo_restante = max(0, sala["tempo_pergunta"] - tempo_passado)

    if resposta == correta:
        pontos = int(tempo_restante * 10)
        sala["jogadores"][nome] += pontos
        return {
            "correta": True,
            "pontos": pontos,
            "resposta_correta": correta
        }

    else:
        return {
            "correta": False,
            "pontos": 0,
            "resposta_correta": correta
        }


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

