import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
import pandas as pd
from groq import Groq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

app = Flask(__name__)
client = Groq(api_key=api_key)

tabela_global = pd.DataFrame()

@app.route("/", methods=["GET", "POST"])
def index():
    global tabela_global
    resposta = ""
    pergunta = ""
    tabela_html = ""

    if request.method == "POST":
        if "file" in request.files:
            arquivo = request.files["file"]
            if arquivo.filename.endswith(".csv"):
                tabela_global = pd.read_csv(arquivo)
        elif "pergunta" in request.form:
            pergunta = request.form["pergunta"]
            if not tabela_global.empty:
                prompt = f"""
                Abaixo estão alguns dados da tabela:

                {tabela_global.head(10).to_string(index=False)}

                Pergunta: {pergunta}
                """
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": "Você é um assistente de IA que responde perguntas em forma de texto. Sempre que alguém te pedir informações sobre uma sala, organize um texto com os dados. Não dê opinião sobre materiais. voce deve responder desta forma: A sala tem a parede de alvenaria, teto de gesso e piso de ceramica. nada alem disso",
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama-3.3-70b-versatile",
                )
                resposta = chat_completion.choices[0].message.content

    if not tabela_global.empty:
        tabela_html = tabela_global.to_html(classes="tabela", index=False)

    return render_template("index.html", resposta=resposta, pergunta=pergunta, tabela_html=tabela_html)

if __name__ == "__main__":
    app.run(debug=True)
