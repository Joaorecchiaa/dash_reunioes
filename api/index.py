import os
import csv
import io
import time
import calendar
import unicodedata
import threading
import requests
from datetime import datetime, date, timedelta
from collections import defaultdict
from flask import Flask, jsonify, request, Response

# .env so existe localmente; na Vercel as variaveis vem do painel
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
except Exception:
    pass

try:
    from api.pipedrive_client import PipedriveClient
    from api.front import HTML
except ImportError:
    from pipedrive_client import PipedriveClient
    from front import HTML

app = Flask(__name__, static_folder=None)

PIPEDRIVE_DOMAIN = os.environ["PIPEDRIVE_DOMAIN"]
PIPEDRIVE_API_TOKEN = os.environ["PIPEDRIVE_API_TOKEN"]
CSV_URL = os.environ["COLABORADORES_CSV_URL"]
PIPEDRIVE_BASE_URL = f"https://{PIPEDRIVE_DOMAIN}"
REFRESH_SECONDS = int(os.environ.get("REFRESH_SECONDS", 1200))  # 20 min

client = PipedriveClient(PIPEDRIVE_DOMAIN, PIPEDRIVE_API_TOKEN)

TIMES_VALIDOS = {"SNIPER", "OLYMPUS", "ELITE"}
SUBAREA_ALIAS = {"MGM": "OLYMPUS"}  # so MGM vira OLYMPUS; o resto passa igual

MESES_NOME = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
              "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
MES_TO_NUM = {}
for i, nome in enumerate(MESES_NOME, start=1):
    MES_TO_NUM[nome] = i
    MES_TO_NUM[nome[:3]] = i

TTL = 300
_cache = {"csv": None, "meta": None, "acts": {}, "deals": {}, "current": None}
_lock = threading.Lock()


# ---------- utilidades ----------

def sem_acento(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    return "".join(c for c in s if not unicodedata.combining(c))


def norm(s):
    return sem_acento(s).strip().lower()


def parse_mes(v):
    v = norm(v)
    if v.isdigit():
        return int(v)
    return MES_TO_NUM.get(v) or MES_TO_NUM.get(v[:3])


def novo_contador():
    return {"planned": 0, "done": 0, "no_show": 0, "reagendada": 0}


def soma_em(counter, tipo, done):
    counter["planned"] += 1
    if tipo == "meeting" and done:
        counter["done"] += 1
    elif tipo == "no_show":
        counter["no_show"] += 1
    elif tipo == "nao_se_aplica":
        counter["reagendada"] += 1


def soma_contadores(dest, src):
    for k in dest:
        dest[k] += src[k]


# ---------- CSV de colaboradores ----------

def carrega_csv():
    with _lock:
        c = _cache["csv"]
        if c and time.time() - c["ts"] < TTL:
            return c["rows"]
    resp = requests.get(CSV_URL, timeout=30, allow_redirects=True,
                        headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        print(f"[CSV] {resp.status_code} ao baixar. URL: {CSV_URL[:120]}...")
        print(f"[CSV] resposta: {resp.text[:200]}")
        resp.raise_for_status()
    resp.encoding = "utf-8"
    reader = csv.DictReader(io.StringIO(resp.text))

    def achar(*nomes):
        for col in nomes:
            alvo = norm(col)
            for h in reader.fieldnames:
                if norm(h) == alvo:
                    return h
        return None

    col_nome = achar("Nome", "NOME")
    col_sub = achar("Subarea", "SUBAREA")
    col_cargo = achar("Cargo", "CARGO")
    col_mes = achar("Mês Referencia", "Mes Referencia", "MÊS REFERIDO")
    col_ano = achar("Ano Referencia", "ANO REFERIDO")
    faltando = [n for n, c in [("Nome", col_nome), ("Subarea", col_sub),
                ("Cargo", col_cargo), ("Mês Referencia", col_mes),
                ("Ano Referencia", col_ano)] if not c]
    if faltando:
        print("[CSV] Colunas nao encontradas:", faltando, "| Cabecalhos:", reader.fieldnames)

    rows = []
    for r in reader:
        subarea = (r.get(col_sub) or "").strip().upper()
        subarea = SUBAREA_ALIAS.get(subarea, subarea)
        cargo = norm(r.get(col_cargo))
        mes = parse_mes(r.get(col_mes))
        ano = norm(r.get(col_ano))
        ano = int(ano) if ano.isdigit() else None
        rows.append({
            "nome": (r.get(col_nome) or "").strip(),
            "time": subarea,
            "cargo": cargo,
            "mes": mes,
            "ano": ano,
        })
    with _lock:
        _cache["csv"] = {"ts": time.time(), "rows": rows}
    return rows


def closers_do_mes(year, month):
    """{nome: time} dos closers ativos naquele mes/ano, so times validos."""
    out = {}
    for r in carrega_csv():
        if not r["cargo"].startswith("closer"):   # "closer 1", "closer 2"...
            continue
        if r["mes"] != month or r["ano"] != year:
            continue
        if r["time"] not in TIMES_VALIDOS:
            continue
        if r["nome"]:
            out[r["nome"]] = r["time"]
    return out


def meses_disponiveis():
    pares = set()
    for r in carrega_csv():
        if r["mes"] and r["ano"]:
            pares.add((r["ano"], r["mes"]))
    hoje = date.today()
    pares.add((hoje.year, hoje.month))
    saida = []
    for ano, mes in sorted(pares, reverse=True):
        saida.append({"value": f"{ano}-{mes:02d}", "label": f"{MESES_NOME[mes-1]}/{ano}"})
    return saida


# ---------- meta Pipedrive ----------

def carrega_meta():
    with _lock:
        m = _cache["meta"]
        if m and time.time() - m["ts"] < TTL:
            return m["users"], m["pipelines"]
    users = client.get_users_map()
    pipelines = client.get_pipelines_map()
    with _lock:
        _cache["meta"] = {"ts": time.time(), "users": users, "pipelines": pipelines}
    return users, pipelines


def acts_do_owner(owner_id, year, month):
    key = (owner_id, year, month)
    with _lock:
        c = _cache["acts"].get(key)
        if c and time.time() - c["ts"] < TTL:
            return c["acts"]
    inicio = (date(year, month, 1) - timedelta(days=31)).strftime("%Y-%m-%dT00:00:00Z")
    acts = client.get_meeting_activities(owner_id, updated_since=inicio)
    with _lock:
        _cache["acts"][key] = {"ts": time.time(), "acts": acts}
    return acts


def info_dos_deals(deal_ids):
    """{deal_id: {"pipeline_id":..., "title":...}} com cache."""
    faltando = []
    with _lock:
        for d in deal_ids:
            if d not in _cache["deals"]:
                faltando.append(d)
    if faltando:
        novos = client.get_deals_info(faltando)
        with _lock:
            _cache["deals"].update(novos)
    with _lock:
        return {d: _cache["deals"].get(d) for d in deal_ids}


# ---------- construcao ----------

def build_dashboard(year, month, time_filtro=None, closer_filtro=None):
    users, pipelines = carrega_meta()
    closers = closers_do_mes(year, month)

    if time_filtro and time_filtro.upper() != "TODOS":
        closers = {n: t for n, t in closers.items() if t == time_filtro.upper()}
    if closer_filtro and closer_filtro.upper() != "TODOS":
        closers = {n: t for n, t in closers.items() if n == closer_filtro}

    last_day = calendar.monthrange(year, month)[1]
    combined_days = {d: novo_contador() for d in range(1, last_day + 1)}
    month_total = novo_contador()
    por_closer = []
    por_time = defaultdict(novo_contador)
    por_time_days = {}          # time -> {dia: contador}
    nao_encontrados = []

    for nome, time_c in sorted(closers.items()):
        if time_c not in por_time_days:
            por_time_days[time_c] = {d: novo_contador() for d in range(1, last_day + 1)}

        owner_id = users.get(nome.strip().lower())
        if not owner_id:
            nao_encontrados.append(nome)
            continue

        acts = acts_do_owner(owner_id, year, month)
        deal_ids = {a["deal_id"] for a in acts if a.get("deal_id")}
        deal_info = info_dos_deals(deal_ids)

        c_total = novo_contador()
        c_days = {d: novo_contador() for d in range(1, last_day + 1)}
        c_pipes = defaultdict(novo_contador)
        c_meetings = []

        for a in acts:
            due = a.get("due_date")
            deal_id = a.get("deal_id")
            tipo = a.get("type")
            done = a.get("done")
            if not due or not deal_id:
                continue
            d = datetime.strptime(due, "%Y-%m-%d").date()
            if d.year != year or d.month != month:
                continue

            soma_em(combined_days[d.day], tipo, done)
            soma_em(month_total, tipo, done)
            soma_em(c_total, tipo, done)
            soma_em(c_days[d.day], tipo, done)
            soma_em(por_time[time_c], tipo, done)
            soma_em(por_time_days[time_c][d.day], tipo, done)

            info = deal_info.get(deal_id) or {}
            pid = info.get("pipeline_id")
            pnome = pipelines.get(pid, f"Funil {pid}") if pid else "Sem funil"
            soma_em(c_pipes[pnome], tipo, done)

            if tipo == "meeting" and done:
                status = "feita"
            elif tipo == "no_show":
                status = "no_show"
            elif tipo == "nao_se_aplica":
                status = "reagendada"
            else:
                status = "pendente"

            c_meetings.append({
                "deal_id": deal_id,
                "title": info.get("title") or f"Negocio {deal_id}",
                "date": due,
                "dia": d.day,
                "hora": a.get("due_time") or "",
                "subject": a.get("subject") or "",
                "status": status,
                "pipeline": pnome,
                "url": f"{PIPEDRIVE_BASE_URL}/deal/{deal_id}",
            })

        c_meetings.sort(key=lambda m: (m["date"], m["hora"]))

        por_closer.append({
            "name": nome, "time": time_c,
            "total": c_total,
            "days": [{"dia": d, "counter": c_days[d]} for d in range(1, last_day + 1)],
            "by_pipeline": dict(c_pipes),
            "meetings": c_meetings,
        })

    dias = [{"dia": d, "counter": combined_days[d]} for d in range(1, last_day + 1)]
    por_closer.sort(key=lambda x: (-x["total"]["planned"], x["name"]))

    por_time_days_out = {
        t: [{"dia": d, "counter": dd[d]} for d in range(1, last_day + 1)]
        for t, dd in por_time_days.items()
    }

    return {
        "generated_at": datetime.now().isoformat(),
        "year": year, "month": month,
        "month_label": f"{MESES_NOME[month-1]}/{year}",
        "days": dias,
        "month_total": month_total,
        "por_time": dict(por_time),
        "por_time_days": por_time_days_out,
        "por_closer": por_closer,
        "nao_encontrados": nao_encontrados,
    }


def eh_default(year, month, team, closer):
    hoje = date.today()
    return (year == hoje.year and month == hoje.month
            and (not team or team.upper() == "TODOS")
            and (not closer or closer.upper() == "TODOS"))


def refresh_current_loop():
    """Reconstroi o mes atual a cada REFRESH_SECONDS. So roda LOCAL --
    na Vercel (serverless) nao existe processo de fundo; o refresh vem do navegador."""
    while True:
        try:
            hoje = date.today()
            data = build_dashboard(hoje.year, hoje.month)
            with _lock:
                _cache["current"] = {"ts": time.time(), "key": (hoje.year, hoje.month), "data": data}
            print(f"[auto] mes atual atualizado {datetime.now():%H:%M:%S}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Erro no refresh automatico:", e)
        time.sleep(REFRESH_SECONDS)


# ---------- rotas ----------

@app.route("/api/init")
def api_init():
    hoje = date.today()
    return jsonify({
        "months": meses_disponiveis(),
        "current": f"{hoje.year}-{hoje.month:02d}",
        "teams": ["Todos"] + sorted(TIMES_VALIDOS),
        "refresh_seconds": REFRESH_SECONDS,
    })


@app.route("/api/closers")
def api_closers():
    mes = request.args.get("month", "")
    try:
        year, month = map(int, mes.split("-"))
    except Exception:
        hoje = date.today()
        year, month = hoje.year, hoje.month
    closers = closers_do_mes(year, month)
    return jsonify({"closers": ["Todos"] + sorted(closers.keys())})


@app.route("/api/dashboard")
def api_dashboard():
    mes = request.args.get("month", "")
    try:
        year, month = map(int, mes.split("-"))
    except Exception:
        hoje = date.today()
        year, month = hoje.year, hoje.month
    team = request.args.get("team")
    closer = request.args.get("closer")

    if eh_default(year, month, team, closer):
        with _lock:
            c = _cache["current"]
            if c and c["key"] == (year, month):
                return jsonify(c["data"])

    try:
        return jsonify(build_dashboard(year, month, team, closer))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# servir o front (HTML vem embutido em front.py -- garante que vai no bundle)
@app.route("/")
def index():
    return Response(HTML, mimetype="text/html")


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "rota nao encontrada", "path": request.path}), 404
    return Response(HTML, mimetype="text/html")


if __name__ == "__main__":
    threading.Thread(target=refresh_current_loop, daemon=True).start()
    app.run(debug=True, port=5000, use_reloader=False)
