import os
import csv
import io
import time
import json
import hmac
import base64
import hashlib
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

def env(nome, padrao=None):
    """Le variavel de ambiente limpando aspas/espacos (o painel da Vercel e o
    Import .env costumam trazer o valor entre aspas)."""
    v = os.environ.get(nome, padrao)
    if v is None:
        raise RuntimeError(f"Variavel de ambiente {nome} nao definida")
    return str(v).strip().strip('"').strip("'").strip()


PIPEDRIVE_DOMAIN = env("PIPEDRIVE_DOMAIN")
PIPEDRIVE_API_TOKEN = env("PIPEDRIVE_API_TOKEN")
CSV_URL = env("COLABORADORES_CSV_URL")
PIPEDRIVE_BASE_URL = "https://" + PIPEDRIVE_DOMAIN
REFRESH_SECONDS = int(env("REFRESH_SECONDS", 1200))  # 20 min

# ---- autenticacao do acesso privilegiado ----
# USUARIOS_PRIVILEGIADOS = "usuario1:hash_sha256,usuario2:hash_sha256"
#   (hash da senha em sha256 hex; gere com gerar_hash.py)
# AUTH_SECRET = string aleatoria longa para assinar o token
def _carrega_usuarios():
    raw = os.environ.get("USUARIOS_PRIVILEGIADOS", "") or ""
    raw = raw.strip().strip('"').strip("'").strip()
    users = {}
    for par in raw.split(","):
        par = par.strip()
        if not par or ":" not in par:
            continue
        u, h = par.split(":", 1)
        users[u.strip().lower()] = h.strip().lower()
    return users

USUARIOS_PRIV = _carrega_usuarios()
AUTH_SECRET = (os.environ.get("AUTH_SECRET", "") or "troque-este-segredo").encode()
TOKEN_HORAS = 12  # validade do login


def _sha256(txt):
    return hashlib.sha256(txt.encode("utf-8")).hexdigest()


def gera_token(usuario):
    exp = int(time.time()) + TOKEN_HORAS * 3600
    corpo = f"{usuario}|{exp}"
    assinatura = hmac.new(AUTH_SECRET, corpo.encode(), hashlib.sha256).hexdigest()
    bruto = f"{corpo}|{assinatura}"
    return base64.urlsafe_b64encode(bruto.encode()).decode()


def valida_token(token):
    """Retorna o usuario se o token for valido e nao expirado; senao None."""
    if not token:
        return None
    try:
        bruto = base64.urlsafe_b64decode(token.encode()).decode()
        usuario, exp, assinatura = bruto.rsplit("|", 2)
        corpo = f"{usuario}|{exp}"
        esperado = hmac.new(AUTH_SECRET, corpo.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(esperado, assinatura):
            return None
        if int(exp) < int(time.time()):
            return None
        return usuario
    except Exception:
        return None


def eh_privilegiado(req):
    """Le o token do header Authorization: Bearer <token>."""
    auth = req.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return valida_token(auth[7:]) is not None
    return False

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
_cache = {"csv": None, "meta": None, "acts": {}, "deals": {}, "current": {}}
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
    elif tipo == "reagendamento":
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
    """{deal_id: {"pipeline_id":..., "title":...}} com cache local."""
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

def build_dashboard(year, month, time_filtro=None, closer_filtro=None, privilegiado=False):
    users, pipelines = carrega_meta()
    closers = closers_do_mes(year, month)

    if time_filtro and time_filtro.upper() != "TODOS":
        closers = {n: t for n, t in closers.items() if t == time_filtro.upper()}
    if closer_filtro and closer_filtro.upper() != "TODOS":
        closers = {n: t for n, t in closers.items() if n == closer_filtro}

    last_day = calendar.monthrange(year, month)[1]
    combined_days = {d: novo_contador() for d in range(1, last_day + 1)}
    geral_dia = {d: [] for d in range(1, last_day + 1)}  # dia -> reunioes de todos os closers (so priv)
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
        c_criadas = {"proprio": 0, "outro": 0}
        c_criadas_days = {d: {"proprio": 0, "outro": 0} for d in range(1, last_day + 1)}
        c_negocios_mes = {}   # deal_id -> {id,title,url}  (dedupe do mes)
        c_negocios_dia = {d: [] for d in range(1, last_day + 1)}  # dia -> lista de reunioes com negocio

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

            chave = "proprio" if a.get("creator_user_id") == owner_id else "outro"
            c_criadas[chave] += 1
            c_criadas_days[d.day][chave] += 1

            if privilegiado:
                titulo = info.get("title") or ("Negocio " + str(deal_id))
                url = PIPEDRIVE_BASE_URL + "/deal/" + str(deal_id)
                hora = (a.get("due_time") or "")[:5]  # HH:MM
                # dedupe do mes (por negocio)
                if deal_id not in c_negocios_mes:
                    c_negocios_mes[deal_id] = {"id": deal_id, "title": titulo, "url": url}
                # lista do dia (uma linha por reuniao, com hora)
                item_dia = {
                    "id": deal_id, "title": titulo, "url": url,
                    "hora": hora, "tipo": tipo, "done": bool(done),
                }
                c_negocios_dia[d.day].append(item_dia)
                # lista geral (todos os closers) para a secao "dia a dia"
                geral_dia[d.day].append({**item_dia, "closer": nome, "time": time_c})

        por_closer.append({
            "name": nome, "time": time_c,
            "total": c_total,
            "days": [{"dia": d, "counter": c_days[d]} for d in range(1, last_day + 1)],
            "by_pipeline": dict(c_pipes),
            "criadas": c_criadas,
            "criadas_days": [{"dia": d, "c": c_criadas_days[d]} for d in range(1, last_day + 1)],
            "negocios": sorted(c_negocios_mes.values(), key=lambda x: x["id"]) if privilegiado else [],
            "negocios_dia": ([{"dia": d, "itens": sorted(c_negocios_dia[d], key=lambda x: x["hora"])}
                              for d in range(1, last_day + 1)] if privilegiado else []),
        })

    dias = [{"dia": d, "counter": combined_days[d]} for d in range(1, last_day + 1)]
    geral_dia_out = ([{"dia": d, "itens": sorted(geral_dia[d], key=lambda x: (x["hora"], x["closer"]))}
                      for d in range(1, last_day + 1)] if privilegiado else [])
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
        "geral_dia": geral_dia_out,
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
            data_comum = build_dashboard(hoje.year, hoje.month, privilegiado=False)
            data_priv = build_dashboard(hoje.year, hoje.month, privilegiado=True)
            with _lock:
                _cache["current"] = {
                    "ts": time.time(), "key": (hoje.year, hoje.month),
                    "data": {False: data_comum, True: data_priv},
                }
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
    priv = eh_privilegiado(request)

    if eh_default(year, month, team, closer):
        with _lock:
            c = _cache["current"]
            if c and c.get("key") == (year, month) and priv in c["data"]:
                return jsonify(c["data"][priv])

    try:
        return jsonify(build_dashboard(year, month, team, closer, privilegiado=priv))
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def api_login():
    dados = request.get_json(silent=True) or {}
    usuario = str(dados.get("usuario", "")).strip().lower()
    senha = str(dados.get("senha", ""))
    hash_ok = USUARIOS_PRIV.get(usuario)
    if hash_ok and hmac.compare_digest(hash_ok, _sha256(senha)):
        return jsonify({"token": gera_token(usuario), "usuario": usuario})
    return jsonify({"error": "usuario ou senha invalidos"}), 401


@app.route("/api/me")
def api_me():
    auth = request.headers.get("Authorization", "")
    tok = auth[7:] if auth.startswith("Bearer ") else ""
    u = valida_token(tok)
    return jsonify({"privilegiado": bool(u), "usuario": u})


# servir o front (HTML vem embutido em front.py -- garante que vai no bundle)
# "/" = local; "/api/index" = destino do rewrite da Vercel (vercel.json)
@app.route("/")
@app.route("/api/index")
def index():
    return Response(HTML, mimetype="text/html")


# rotas de API "de verdade" que existem
_API_ROTAS = ("/api/init", "/api/closers", "/api/dashboard", "/api/login", "/api/me")


@app.errorhandler(404)
def not_found(e):
    # so devolve erro JSON quando bate numa rota de API conhecida com metodo/params errados;
    # qualquer outro path desconhecido cai no front (SPA-like)
    if request.path in _API_ROTAS:
        return jsonify({"error": "rota nao encontrada", "path": request.path}), 404
    return Response(HTML, mimetype="text/html")


# entrypoint explicito para o runtime Python da Vercel (@vercel/python)
# procura por um objeto WSGI chamado "app", "application" ou "handler"
application = app
handler = app

if __name__ == "__main__":
    threading.Thread(target=refresh_current_loop, daemon=True).start()
    app.run(debug=True, port=5000, use_reloader=False)
