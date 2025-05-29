from flask import Flask, render_template, request, send_file
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import math
import os
import uuid

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nome_pedido = request.form["nome_pedido"]
        largura_rolo = float(request.form["largura_rolo"])
        comprimento_rolo = float(request.form["comprimento_rolo"])
        margem = 0.01

        pecas = []
        for i in range(len(request.form.getlist("nome_peca"))):
            pecas.append({
                "nome": request.form.getlist("nome_peca")[i],
                "largura": float(request.form.getlist("largura")[i]),
                "comprimento": float(request.form.getlist("comprimento")[i]),
                "quantidade": int(request.form.getlist("quantidade")[i]),
                "cor": "lightblue"
            })

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.set_xlim(0, comprimento_rolo)
        ax.set_ylim(0, largura_rolo)
        ax.set_title(f"Plano de Corte - {nome_pedido}")
        ax.set_xlabel("Comprimento (m)")
        ax.set_ylabel("Largura (m)")
        rolo = patches.Rectangle((0, 0), comprimento_rolo, largura_rolo, linewidth=1.5, edgecolor='black', facecolor='none')
        ax.add_patch(rolo)

        pos_x = 0
        total_area = largura_rolo * comprimento_rolo
        area_util = 0
        total_pecas = 0

        for peca in pecas:
            l_total = peca["largura"] + margem
            c_total = peca["comprimento"] + margem
            por_faixa = int(largura_rolo // l_total)
            restante = peca["quantidade"]
            faixas = math.ceil(restante / por_faixa)

            for faixa in range(faixas):
                if pos_x + c_total > comprimento_rolo:
                    break
                for i in range(por_faixa):
                    if restante <= 0: break
                    pos_y = i * l_total
                    ax.add_patch(patches.Rectangle((pos_x, pos_y), c_total - margem, l_total - margem,
                                                   facecolor=peca["cor"], edgecolor='gray'))
                    ax.text(pos_x + 0.02, pos_y + 0.01, peca["nome"], fontsize=6)
                    restante -= 1
                    area_util += peca["largura"] * peca["comprimento"]
                    total_pecas += 1
                pos_x += c_total

        os.makedirs("static", exist_ok=True)
        img_path = f"static/plano_{uuid.uuid4().hex}.png"
        plt.tight_layout()
        plt.savefig(img_path, dpi=300)
        plt.close()

        os.makedirs("relatorios", exist_ok=True)
        pdf_path = f"relatorios/{nome_pedido.replace(' ', '_')}.pdf"
        pdf = canvas.Canvas(pdf_path, pagesize=A4)
        pdf.setTitle(f"Relatório - {nome_pedido}")
        pdf.drawString(50, 800, f"Relatório de Corte - {nome_pedido}")
        pdf.drawString(50, 780, f"Largura do rolo: {largura_rolo:.2f} m")
        pdf.drawString(50, 765, f"Comprimento disponível: {comprimento_rolo:.2f} m")
        pdf.drawString(50, 750, f"Comprimento usado: {pos_x:.2f} m")
        pdf.drawString(50, 735, f"Peças cortadas: {total_pecas}")
        pdf.drawString(50, 720, f"Aproveitamento: {(area_util / total_area * 100):.2f}%")
        pdf.drawImage(img_path, 50, 400, width=500, preserveAspectRatio=True)
        pdf.save()

        return send_file(pdf_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # usa a porta que o Render fornece
    app.run(host="0.0.0.0", port=port)
