#!/usr/bin/env python3
"""Monta index.html a partir de modelo.html, do horário (horario.json) e dos créditos das imagens,
e as páginas do feed (feed/*.html) a partir de posts/*.md e modelo_post.html.

Uso: python3 build.py   (depois de editar horario.json, modelo.html, assets/credits.json ou um post)
"""
import json
import math
import re
import shutil
from html import escape
from pathlib import Path

import markdown

RAIZ = Path(__file__).parent
SLOTS = [("08:20", "09:10"), ("09:20", "10:10"), ("10:10", "11:00"), ("11:00", "11:50"), ("11:50", "12:50"),
         ("13:30", "14:20"), ("14:20", "15:10"), ("15:20", "16:10"), ("16:10", "17:00"), ("17:00", "17:40")]
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]


def tabela():
    """Grade semanal em CSS grid: cada bloco recebe dia (coluna) e faixa de horários (linhas) explícitos."""
    horario = json.loads((RAIZ / "horario.json").read_text(encoding="utf-8"))
    inicios = [a for a, _ in SLOTS]
    fins = [b for _, b in SLOTS]
    partes = ['<div class="semana" role="table" aria-label="Horário semanal 2026/2">']
    partes += [f'<div class="sem-dia" role="columnheader" style="grid-column:{d + 2};grid-row:1">{nome}</div>' for d, nome in enumerate(DIAS)]
    partes += [f'<div class="sem-hora" role="rowheader" style="grid-column:1;grid-row:{r + 2}" title="{a}–{b}">{a}</div>' for r, (a, b) in enumerate(SLOTS)]
    for e in horario:
        ini, fim = inicios.index(e["ini"]) + 2, fins.index(e["fim"]) + 3
        sala = f'<span>{e["sala"]}</span>' if e["sala"] else ""
        rotulo = f'{DIAS[e["dia"] - 1]} {e["ini"]}–{e["fim"]}: {e["nome"]}' + (f', sala {e["sala"]}' if e["sala"] else "")
        partes.append(f'<div class="slot {e["tipo"]}" role="cell" style="grid-column:{e["dia"] + 1};grid-row:{ini}/{fim}" '
                      f'data-dia="{e["dia"]}" data-ini="{e["ini"]}" data-fim="{e["fim"]}" title="{escape(e["nome"])}" aria-label="{escape(rotulo)}">'
                      f'<b>{e["sigla"]}</b>{sala}</div>')
    partes.append("</div>")
    return "\n          ".join(partes)


def traco():
    """Traço da tela de osciloscópio da barra lateral: uma senoide modulada em amplitude,
    periódica em 240 unidades, desenhada duas vezes para a animação rolar sem emenda."""
    pontos = []
    for i in range(0, 481):
        x = i
        envelope = 0.55 + 0.45 * math.cos(2 * math.pi * x / 120)
        y = 36 - 24 * envelope * math.sin(2 * math.pi * x / 20)
        pontos.append(f"{x:.0f} {y:.1f}")
    return "M" + " L".join(pontos)


def figura_pesquisa():
    """Figura da aba Pesquisa: voz -> espectrograma mel -> seleção de descritores -> emoção.
    Valores ilustrativos, gerados de forma determinística."""
    w = 240
    out = [f'<svg class="fig-ml" viewBox="0 0 {w} 404" role="img" aria-labelledby="fig-ml-t">',
           '<title id="fig-ml-t">Da voz à emoção: sinal, espectrograma mel, seleção de descritores e classificação (ilustrativo)</title>']
    rotulo = lambda y, texto: out.append(f'<text class="fig-rot" x="0" y="{y}">{texto}</text>')
    seta = lambda y: out.append(f'<path class="fig-seta" d="M{w/2} {y}v14m-4 -5l4 5 4-5"/>')
    # 1. sinal de voz: rajadas com envelope, como sílabas
    rotulo(10, "voz")
    pts = []
    for i in range(0, 241):
        t = i / 240
        env = max(0.0, math.sin(math.pi * t * 3)) ** 1.5
        y = 38 - 22 * env * math.sin(2 * math.pi * i / 6.5) * (0.7 + 0.3 * math.cos(i / 9))
        pts.append(f"{i} {y:.1f}")
    out.append(f'<path class="fig-onda" d="M{" L".join(pts)}"/>')
    seta(66)
    # 2. espectrograma em escala mel: 30 quadros x 12 bandas
    rotulo(96, "espectrograma mel")
    quadros, bandas, x0, y0, cw, ch = 30, 12, 0, 102, 8, 6
    for q in range(quadros):
        env = max(0.0, math.sin(math.pi * (q + 0.5) / quadros * 3)) ** 1.2
        for b in range(bandas):
            formante = math.exp(-((b - 3 - 1.5 * math.sin(q / 4)) ** 2) / 3) + 0.7 * math.exp(-((b - 8 + math.cos(q / 5)) ** 2) / 4)
            v = min(1.0, 0.08 + env * formante)
            out.append(f'<rect x="{x0 + q * cw}" y="{y0 + (bandas - 1 - b) * ch}" width="{cw - 1}" height="{ch - 1}" fill-opacity="{v:.2f}"/>')
    seta(180)
    # 3. descritores: 20 valores, 6 selecionados
    rotulo(210, "descritores selecionados")
    escolhidos = {1, 4, 7, 11, 14, 18}
    for k in range(20):
        h = 10 + 26 * abs(math.sin(k * 1.7 + 0.4))
        cls = "fig-sel" if k in escolhidos else "fig-desc"
        out.append(f'<rect class="{cls}" x="{k * 12}" y="{254 - h:.1f}" width="9" height="{h:.1f}" rx="1.5"/>')
    seta(262)
    # 4. classificador: probabilidade por emoção
    rotulo(292, "emoção")
    emocoes = [("neutra", 0.14), ("alegria", 0.09), ("raiva", 0.65), ("tristeza", 0.12)]
    for n, (nome, p) in enumerate(emocoes):
        y = 302 + n * 25
        cls = "fig-barra-max" if p == max(v for _, v in emocoes) else "fig-barra"
        out.append(f'<text class="fig-emo" x="0" y="{y + 11}">{nome}</text>')
        out.append(f'<rect class="fig-trilho" x="62" y="{y + 2}" width="150" height="12" rx="3"/>')
        out.append(f'<rect class="{cls}" x="62" y="{y + 2}" width="{150 * p:.0f}" height="12" rx="3"/>')
        out.append(f'<text class="fig-emo" x="{w}" y="{y + 11}" text-anchor="end">{p:.2f}</text>')
    out.append("</svg>")
    return "".join(out)


def creditos():
    itens = json.loads((RAIZ / "assets" / "credits.json").read_text(encoding="utf-8"))
    partes = []
    for c in itens:
        autor = f' por {escape(c["creator"])}' if c.get("creator") else ""
        partes.append(f'foto <a href="{escape(c["page"])}">{escape(c["title"])}</a>{autor}, '
                      f'<a href="{escape(c["licenseUrl"])}">{escape(c["license"])}</a>')
    return " · ".join(["© 2026 Rafael Kingeski", *partes])


def ler_posts():
    """Posts publicados de posts/AAAA-MM-DD-nome.md, do mais novo ao mais antigo.
    O cabeçalho entre --- traz titulo, resumo e rascunho (sim/nao)."""
    posts = []
    for arq in sorted((RAIZ / "posts").glob("*.md"), reverse=True):
        nome = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})-(.+)\.md", arq.name)
        if not nome:
            continue
        texto = arq.read_text(encoding="utf-8")
        cab = re.match(r"---\n(.*?)\n---\n", texto, re.S)
        if not cab:
            raise SystemExit(f"{arq.name}: falta o cabeçalho entre ---")
        meta = dict(linha.split(":", 1) for linha in cab.group(1).splitlines() if ":" in linha)
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        if meta.get("rascunho", "nao").lower() in ("sim", "s", "true"):
            continue
        ano, mes, dia, slug = nome.groups()
        posts.append({
            "slug": slug,
            "titulo": meta.get("titulo", slug),
            "resumo": meta.get("resumo", ""),
            "data_iso": f"{ano}-{mes}-{dia}",
            "data": f"{int(dia)} de {MESES[int(mes) - 1]} de {ano}",
            "html": markdown.markdown(texto[cab.end():], extensions=["fenced_code", "tables", "sane_lists"]),
        })
    return posts


def gerar_feed(posts):
    """Gera feed/<slug>.html para cada post e devolve a lista da aba Feed."""
    pasta = RAIZ / "feed"
    pasta.mkdir(exist_ok=True)
    for velho in pasta.glob("*.html"):  # a pasta é toda gerada: posts apagados somem
        velho.unlink()
    if (RAIZ / "posts" / "imagens").is_dir():
        shutil.copytree(RAIZ / "posts" / "imagens", pasta / "imagens", dirs_exist_ok=True)
    modelo_post = (RAIZ / "modelo_post.html").read_text(encoding="utf-8")
    for p in posts:
        pagina = (modelo_post.replace("{{TITULO}}", escape(p["titulo"])).replace("{{RESUMO}}", escape(p["resumo"]))
                  .replace("{{DATA_ISO}}", p["data_iso"]).replace("{{DATA}}", p["data"]).replace("{{CONTEUDO}}", p["html"]))
        (pasta / f'{p["slug"]}.html').write_text(pagina, encoding="utf-8")
    if not posts:
        return '<p class="nota">Nenhum post ainda.</p>'
    itens = [f'<li><time class="ano" datetime="{p["data_iso"]}">{p["data"]}</time>'
             f'<div><a href="feed/{p["slug"]}.html">{escape(p["titulo"])}</a><p>{escape(p["resumo"])}</p></div></li>'
             for p in posts]
    return '<ol class="posts">\n          ' + "\n          ".join(itens) + "\n        </ol>"


modelo = (RAIZ / "modelo.html").read_text(encoding="utf-8")
saida = modelo.replace("{{TABELA}}", tabela()).replace("{{TRACO}}", traco()).replace("{{FIGURA}}", figura_pesquisa()).replace("{{CREDITOS}}", creditos())
saida = saida.replace("{{FEED}}", gerar_feed(ler_posts()))
(RAIZ / "index.html").write_text(saida, encoding="utf-8")
print("index.html e feed/ gerados")
