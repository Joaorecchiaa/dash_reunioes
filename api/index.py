"""Dashboard de Reunioes -- Board Academy.

Regras de reuniao, no-show, ligacao, escala, lead e prazo vem da biblioteca CRN
(github.com/negocios87-sketch/CRN). Este arquivo so monta a tela e as rotas.
"""
import io
import os

# ── CRN: baixada do GitHub quando o painel liga ───────────────
# A Vercel não repassa o token para o instalador do build, então a CRN não entra pelo
# requirements.txt. O painel baixa a versão atual da main (com o token, que em tempo de
# execução funciona) e carrega. Cada vez que o painel liga, pega as regras mais recentes.
# No computador, se a crn já estiver instalada (instalar.bat), usa a instalada.
def _carregar_crn():
    import importlib.util
    import shutil
    import sys
    import tarfile
    import tempfile
    if importlib.util.find_spec("crn") is not None:
        return None
    import requests
    token = (os.environ.get("CRN_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()
    if not token:
        raise RuntimeError("CRN_GITHUB_TOKEN não está nas Environment Variables da Vercel.")
    r = requests.get("https://api.github.com/repos/negocios87-sketch/CRN/tarball/main",
                     headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
                     timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Não consegui baixar a CRN do GitHub (HTTP {r.status_code}). Confira o CRN_GITHUB_TOKEN.")
    base = tempfile.mkdtemp(prefix="crn_")
    with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as tar:
        tar.extractall(base, filter="data")
    raiz = os.path.join(base, os.listdir(base)[0])          # negocios87-sketch-CRN-<commit>
    destino = os.path.join(base, "pacote", "crn")
    shutil.copytree(os.path.join(raiz, "lib"), destino)     # mesmo mapa do pyproject da CRN
    shutil.copytree(os.path.join(raiz, "config"), os.path.join(destino, "config"))
    sys.path.insert(0, os.path.join(base, "pacote"))
    return os.path.basename(raiz).rsplit("-", 1)[-1][:7]   # commit que entrou

_COMMIT_CRN = _carregar_crn()

import crn
if _COMMIT_CRN:
    crn.versao = lambda: _COMMIT_CRN                        # carimbo mostra o commit carregado

import csv
import time
import hmac
import base64
import hashlib
import calendar
import unicodedata
import threading
import requests
from datetime import datetime, date, timedelta
from collections import defaultdict
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
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

from crn.base import fuso, pipedrive, fontes
from crn.base.config import campo, tipo_atividade
from crn.base.texto import cf, norm as norm_crn, responsavel_id
from crn.regras import (m6_reunioes_sdr as m6, rc1_reunioes_closer as rc1, st1_status_reuniao as st1,
                        pr1_marcada_pelo_proprio as pr1, cv2_conversao_reuniao as cv2,
                        h1_hierarquia as h1, l3_lead_time_agendamento as l3,
                        lp1_leads_sdr as lp1, at1_ligacoes as at1, op2_fora_da_escala as op2)
from crn.regras._atividades import do_tipo, por_responsavel
from crn.regras._comum import deduplicar, criada_pela_ia

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
# opcionais -- se nao configuradas ainda, a secao "Distribuicao de Leads"
# simplesmente devolve um erro tratado nessa rota, sem derrubar o resto do app
DISTRIBUICAO_RESUMO_CSV_URL = env("DISTRIBUICAO_RESUMO_CSV_URL", "")
DISTRIBUICAO_LOG_CSV_URL = env("DISTRIBUICAO_LOG_CSV_URL", "")
# aba "escala_comercial" da planilha config_dashs (a CRN le a mesma variavel; a
# Distribuicao de Leads tem a propria leitura operacional)
ESCALA_COMERCIAL_CSV_URL = env("ESCALA_COMERCIAL_CSV_URL", "")
PIPEDRIVE_BASE_URL = "https://" + PIPEDRIVE_DOMAIN
REFRESH_SECONDS = int(env("REFRESH_SECONDS", 1200))  # 20 min

# ── nomes que a CRN espera (a Vercel continua com as variaveis de sempre) ──
os.environ.setdefault("PIPEDRIVE_TOKEN", PIPEDRIVE_API_TOKEN)
if ESCALA_COMERCIAL_CSV_URL:
    os.environ["ESCALA_COMERCIAL_CSV_URL"] = ESCALA_COMERCIAL_CSV_URL

# COLABORADORES_CSV_URL e a MESMA planilha de Colab e Metas (confirmado): as URLs das abas
# saem dela trocando o gid. Se URL_COLAB / URL_METAS ja estiverem nas variaveis, valem elas.
GID_COLAB = os.environ.get("GID_COLAB", "1782440078")   # fontes/planilhas.md
GID_METAS = os.environ.get("GID_METAS", "0")


def _url_aba(base, gid):
    p = urlsplit(base)
    q = dict(parse_qsl(p.query, keep_blank_values=True))
    q["gid"] = str(gid)
    q.setdefault("single", "true")
    q.setdefault("output", "csv")
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), p.fragment))


os.environ.setdefault("URL_COLAB", _url_aba(CSV_URL, GID_COLAB))
os.environ.setdefault("URL_METAS", _url_aba(CSV_URL, GID_METAS))


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


MESES_NOME = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
              "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

TTL = 300
# dados: leituras do Pipedrive/planilhas por mes; "csv", "dist_*" e "escala" sao da Distribuicao de Leads
_cache = {"dados": {}, "csv": None, "meta": None, "acts": {}, "deals": {}, "current": {}}
_lock = threading.Lock()
_locks_chave = defaultdict(threading.Lock)


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")


def norm(s):
    return norm_crn(s)


def _cache_seguro(chave, ttl, buscar, tamanho=None):
    """Cache com 2 protecoes contra leitura incompleta do Pipedrive:
    1) se a busca falhar, devolve a ultima leitura boa (se houver);
    2) se vier com QUEDA GRANDE (>10%) em relacao a ultima leitura boa, refaz a busca uma vez.
    Uma busca por chave de cada vez (as abas pedem juntas, a segunda espera a primeira)."""
    with _locks_chave[chave]:
        with _lock:
            c = _cache["dados"].get(chave)
        if c and time.time() - c["ts"] < ttl:
            return c["v"]
        try:
            v = buscar()
            if c and tamanho and tamanho(c["v"]) >= 20 and tamanho(v) < 0.9 * tamanho(c["v"]):
                print(f"[dados] queda suspeita {tamanho(c['v'])} -> {tamanho(v)}; refazendo a busca")
                v = buscar()
        except Exception as e:
            if c:
                print("[dados] falha ao atualizar, usando a ultima leitura boa:", e)
                return c["v"]
            raise
        with _lock:
            _cache["dados"][chave] = {"ts": time.time(), "v": v}
        return v


def parse_ym(texto):
    try:
        y, m = map(int, str(texto).split("-"))
        if 1 <= m <= 12:
            return y, m
    except Exception:
        pass
    h = fuso.hoje_brasil()
    return h.year, h.month


# ---------- contexto do mes (Colab + Metas + usuarios do Pipedrive) ----------

def usuarios_pipedrive():
    return _cache_seguro(("usuarios",), 600, pipedrive.usuarios)


def funis_pipedrive():
    return _cache_seguro(("funis",), 600, pipedrive.funis)


def _licenciado(squad):
    return norm(squad).startswith("licenciad")      # P7: Licenciados fora por padrao


def contexto_mes(ano, mes):
    """Quem e SDR / closer / lideranca no mes, pela CRN: papel pela planilha de Metas (R2),
    squad pela Colab do mes (P8 colab_do_mes), lideranca que agenda pela M6."""
    def montar():
        colab = fontes.carregar_colab(ano, mes)
        metas = fontes.carregar_metas(ano, mes)
        users = usuarios_pipedrive()
        id_por_nome = {}
        for uid, nome in users.items():
            id_por_nome.setdefault(norm(nome), uid)
        colab_por_nome = {p["nome_norm"]: p for p in colab}

        def time_de(nome_norm, padrao="SEM TIME"):
            p = colab_por_nome.get(nome_norm)
            return p["squad"].upper() if p and p["squad"] else padrao

        def licenc(nome_norm):
            p = colab_por_nome.get(nome_norm)
            return bool(p) and _licenciado(p["squad"])

        sdrs, closers = {}, {}
        for m in metas:
            if licenc(m["nome_norm"]):
                continue
            if m["papel"] == "sdr":
                sdrs[m["nome"]] = time_de(m["nome_norm"])
            elif m["papel"] == "closer":
                closers[m["nome"]] = time_de(m["nome_norm"])

        # lideranca que agenda (head e team leader de squad so-SDR + extras da config)
        lq_ids = m6.lideranca_que_agenda(colab, id_por_nome)
        lideres = {}
        for uid in lq_ids:
            nome = users.get(uid, "")
            p = colab_por_nome.get(norm(nome))
            nivel = h1.nivel(p, colab) if p else "team_leader"
            lideres[nome] = "Head" if nivel in ("head", "gerente") else "Team Leader"
            sdrs[nome] = time_de(norm(nome), "SNIPER")
        # todos os lideres/heads (H1) -- a M6 precisa deles para a regra do dono do deal
        lid_ids = {id_por_nome[p["nome_norm"]] for p in colab
                   if h1.nivel(p, colab) in ("gerente", "head", "team_leader") and p["nome_norm"] in id_por_nome}
        sdr_ids = {id_por_nome[m["nome_norm"]] for m in metas if m["papel"] == "sdr" and m["nome_norm"] in id_por_nome}
        return {
            "ano": ano, "mes": mes, "users": users, "id_por_nome": id_por_nome,
            "sdrs": sdrs, "closers": closers, "lideres": lideres,
            "sdr_ids": sdr_ids, "lideranca_ids": lid_ids, "lq_ids": set(lq_ids),
        }
    return _cache_seguro(("ctx", ano, mes), 600, montar)


def meses_disponiveis():
    """Meses com linha na Colab (ate 18 para tras); o mes atual sempre entra."""
    hoje = fuso.hoje_brasil()
    pares = [(hoje.year, hoje.month)]
    try:
        linhas = fontes.ler_csv("URL_COLAB")
        a, m = hoje.year, hoje.month
        for _ in range(18):
            m -= 1
            if m == 0:
                a, m = a - 1, 12
            try:
                fontes.carregar_colab(a, m, linhas=linhas)
                pares.append((a, m))
            except fontes.FonteInvalida:
                continue
    except Exception as e:
        print("[meses] nao consegui ler a Colab:", e)
    return [{"value": f"{a}-{m:02d}", "label": f"{MESES_NOME[m-1]}/{a}"} for a, m in pares]


# ---------- dados do periodo (atividades + deals) ----------

def _id_atividade_ou_obj(a):
    return a.get("id") if a.get("id") is not None else id(a)


def dados_periodo(ano, mes):
    """Atividades de reuniao / no-show / reagendamento do mes (+1 dia de margem) e os deals delas.
    Reunioes feitas: m6.carregar_periodo (busca padrao da M6). As nao feitas e os no-shows/reagendamentos
    entram pela mesma busca por periodo, so GET."""
    ini = date(ano, mes, 1)
    fim = date(ano, mes, calendar.monthrange(ano, mes)[1])

    def buscar():
        base = m6.carregar_periodo(ini, fim)
        um = timedelta(days=1)
        reu, ns, rg = tipo_atividade("reuniao"), tipo_atividade("no_show"), tipo_atividade("reagendamento")
        extra = pipedrive.atividades_do_periodo(ini - um, fim + um, tipos=[reu], done=False)
        extra += pipedrive.atividades_do_periodo(ini - um, fim + um, tipos=[ns, rg])
        acts, vistos = [], set()
        for a in list(base["atividades"]) + extra:
            k = _id_atividade_ou_obj(a)
            if k in vistos:
                continue
            vistos.add(k)
            acts.append(a)
        deals = {d["id"]: d for d in base["deals"]}
        faltam = [a.get("deal_id") for a in acts if a.get("deal_id") and a.get("deal_id") not in deals]
        if faltam:
            for d in pipedrive.deals_por_ids(faltam):
                deals[d["id"]] = d
        lista = list(deals.values())
        validados, donos = m6.mapas_dos_deals(lista)
        return {"ini": ini, "fim": fim, "acts": acts, "deals": deals,
                "status_do_deal": m6.status_dos_deals(lista),
                "deals_validados": validados, "dono_do_deal": donos}
    return _cache_seguro(("periodo", ano, mes), TTL, buscar, tamanho=lambda v: len(v["acts"]))


def carimbo(ano=None, mes=None, extra=""):
    agora = fuso.agora_brasil()
    partes = [f"CRN {crn.versao()}",
              "Eixo: data da reunião (due_date + hora, Brasília)",
              "Squads: todos exc. Licenciados",
              "Recorte: quem tem meta no mês (Metas)"]
    if extra:
        partes.append(extra)
    partes.append("Atualizado: " + agora.strftime("%d/%m/%Y %H:%M"))
    return " · ".join(partes)


# ---------- construcao do dashboard ----------

def novo_contador(com_validada=False):
    base = {"planned": 0, "done": 0, "no_show": 0, "reagendada": 0, "nao_validada": 0}
    if com_validada:
        base["validada"] = 0
    return base


def soma_contadores(dest, src):
    for k in dest:
        dest[k] += src.get(k, 0)


def _soma_em(counter, a, validada, nao_valida):
    tipo = a.get("type")
    counter["planned"] += 1
    if tipo == tipo_atividade("reuniao") and a.get("done") in (True, 1):
        counter["done"] += 1
        if validada and "validada" in counter:
            counter["validada"] += 1
        if nao_valida:
            counter["nao_validada"] += 1
    elif tipo == tipo_atividade("no_show"):
        counter["no_show"] += 1
    elif tipo == tipo_atividade("reagendamento"):
        counter["reagendada"] += 1


def _feita(a):
    return a.get("done") is True or a.get("done") == 1 or a.get("status") == "done"


def _hora(a):
    m = fuso.atividade_momento(a)
    return m.strftime("%H:%M") if m else ""


def _status_rotulo(a, validada, nao_valida, agora):
    s = st1.status(a, agora)            # ST1: Reagendada / No-show / Feita / Vencida / Planejada
    if s == "No-show":
        return "No Show"
    if s == "Feita":
        if validada:
            return "Validada"
        if nao_valida:
            return "Não validada"
    return s or "Planejada"


def _build_dashboard_generico(pessoas, ano, mes, privilegiado=False, com_validada=False, lideres=None):
    """pessoas = {nome: time}. Closer (com_validada=False) ou SDR (com_validada=True).
    Totais: RC1 (agendadas, feitas, nao validadas, no-show, reagendadas). Validadas: M6.
    Dia a dia, status e listas: as mesmas atividades que a RC1 contou (do_tipo)."""
    ctx = contexto_mes(ano, mes)
    P = dados_periodo(ano, mes)
    ini, fim = P["ini"], P["fim"]
    users, pipelines = ctx["users"], funis_pipedrive()
    ultimo = fim.day
    agora = fuso.agora_brasil()
    reu = tipo_atividade("reuniao")

    ids = {}
    nao_encontrados = []
    for nome in pessoas:
        uid = ctx["id_por_nome"].get(norm(nome))
        if uid is None:
            nao_encontrados.append(nome)
        else:
            ids[nome] = uid
    ids_set = set(ids.values())

    tot_rc1 = rc1.reunioes_closer(P["acts"], ini, fim, closer_ids=ids_set, status_do_deal=P["status_do_deal"])
    listas = por_responsavel(do_tipo(P["acts"], ["reuniao", "no_show", "reagendamento"], ini, fim,
                                     so_feitas=False, responsaveis=ids_set, sem_ia=True))
    validas_ids = set()
    if com_validada:
        val = m6.reunioes_validadas(P["acts"], ini, fim, deals_validados=P["deals_validados"],
                                    dono_do_deal=P["dono_do_deal"], sdr_ids=ctx["sdr_ids"],
                                    lideranca_ids=ctx["lideranca_ids"], lideranca_que_agenda_ids=ctx["lq_ids"])
        for lst in val.values():
            validas_ids |= {_id_atividade_ou_obj(a) for a in lst}
        val_por_resp = {r: len(l) for r, l in val.items()}
    else:
        val_por_resp = {}
    status_atual = {did: d.get("status") for did, d in P["deals"].items()}

    combined_days = {d: novo_contador(com_validada) for d in range(1, ultimo + 1)}
    geral_dia = {d: [] for d in range(1, ultimo + 1)}
    month_total = novo_contador(com_validada)
    por_closer = []
    por_time = defaultdict(lambda: novo_contador(com_validada))
    por_time_days = {}

    for nome, time_c in sorted(pessoas.items()):
        if time_c not in por_time_days:
            por_time_days[time_c] = {d: novo_contador(com_validada) for d in range(1, ultimo + 1)}
        uid = ids.get(nome)
        if uid is None:
            continue
        lista = listas.get(uid, [])
        c_days = {d: novo_contador(com_validada) for d in range(1, ultimo + 1)}
        c_pipes = defaultdict(lambda: novo_contador(com_validada))
        c_criadas = {"proprio": 0, "outro": 0}
        c_criadas_days = {d: {"proprio": 0, "outro": 0} for d in range(1, ultimo + 1)}
        c_met_days = {d: {"proprio_done": 0, "proprio_validada": 0, "ganhos_done": 0, "ganhos_validada": 0}
                      for d in range(1, ultimo + 1)}
        feitas_dia = {d: [] for d in range(1, ultimo + 1)}
        validas_dia = {d: [] for d in range(1, ultimo + 1)}
        c_negocios_mes, c_negocios_dia = {}, {d: [] for d in range(1, ultimo + 1)}
        proprio_done = proprio_val = 0

        for a in lista:
            dia = fuso.atividade_dia(a)
            if dia is None or dia.year != ano or dia.month != mes:
                continue
            d = dia.day
            did = a.get("deal_id")
            deal = P["deals"].get(did) or {}
            eh_reu = a.get("type") == reu
            feita = eh_reu and _feita(a)
            valida = com_validada and feita and _id_atividade_ou_obj(a) in validas_ids
            nao_valida = feita and P["status_do_deal"].get(did) == "nao"

            for alvo in (c_days[d], combined_days[d], por_time_days[time_c][d]):
                _soma_em(alvo, a, valida, nao_valida)
            pid = deal.get("pipeline_id")
            pnome = pipelines.get(pid, f"Funil {pid}") if pid else "Sem funil"
            _soma_em(c_pipes[pnome], a, valida, nao_valida)

            chave = "proprio" if pr1.marcada_pelo_proprio(a) else "outro"      # PR1
            c_criadas[chave] += 1
            c_criadas_days[d][chave] += 1
            if feita:
                feitas_dia[d].append(a)
                if chave == "proprio":
                    proprio_done += 1
                    c_met_days[d]["proprio_done"] += 1
                    if valida:
                        proprio_val += 1
                        c_met_days[d]["proprio_validada"] += 1
                if valida:
                    validas_dia[d].append(a)

            if privilegiado:
                titulo = deal.get("title") or ("Negocio " + str(did))
                url = PIPEDRIVE_BASE_URL + "/deal/" + str(did)
                status = _status_rotulo(a, valida, nao_valida, agora)
                status_negocio = {"open": "Aberto", "won": "Ganho", "lost": "Perdido"}.get(
                    deal.get("status"), deal.get("status") or "—")
                chave_rec = (str(a.get("due_date")), str(a.get("due_time") or ""), a.get("id") or 0)
                atual = c_negocios_mes.get(did)
                if atual is None or chave_rec > atual["_rec"]:
                    c_negocios_mes[did] = {"id": did, "title": titulo, "url": url, "status": status,
                                           "status_negocio": status_negocio, "_rec": chave_rec}
                item = {"id": did, "title": titulo, "url": url, "hora": _hora(a), "tipo": a.get("type"),
                        "done": bool(feita), "status": status, "status_negocio": status_negocio}
                c_negocios_dia[d].append(item)
                geral_dia[d].append({**item, "closer": nome, "time": time_c})

        # ganhos (CV2): das feitas / validadas, quantos negocios estao ganhos hoje
        for d in range(1, ultimo + 1):
            c_met_days[d]["ganhos_done"] = cv2.conversao(feitas_dia[d], status_atual)["ganhas"]
            c_met_days[d]["ganhos_validada"] = cv2.conversao(validas_dia[d], status_atual)["ganhas"]
        todas_feitas = [a for d in feitas_dia.values() for a in d]
        todas_validas = [a for d in validas_dia.values() for a in d]

        r = tot_rc1.get(uid, {})
        c_total = novo_contador(com_validada)
        c_total.update({"planned": r.get("agendadas", 0), "done": r.get("feitas", 0),
                        "no_show": r.get("no_show", 0), "reagendada": r.get("reagendadas", 0),
                        "nao_validada": r.get("nao_validadas", 0)})
        if com_validada:
            c_total["validada"] = val_por_resp.get(uid, 0)
        soma_contadores(month_total, c_total)
        soma_contadores(por_time[time_c], c_total)

        por_closer.append({
            "name": nome, "time": time_c,
            "lideranca": (lideres or {}).get(nome),
            "total": c_total,
            "days": [{"dia": d, "counter": c_days[d]} for d in range(1, ultimo + 1)],
            "by_pipeline": dict(c_pipes),
            "criadas": c_criadas,
            "criadas_days": [{"dia": d, "c": c_criadas_days[d]} for d in range(1, ultimo + 1)],
            "met_days": [{"dia": d, "c": c_met_days[d]} for d in range(1, ultimo + 1)],
            "proprio_done": proprio_done,
            "proprio_validada": proprio_val,
            "ganhos_done": cv2.conversao(todas_feitas, status_atual)["ganhas"],
            "ganhos_validada": cv2.conversao(todas_validas, status_atual)["ganhas"],
            "negocios": sorted(({k: v for k, v in n.items() if k != "_rec"} for n in c_negocios_mes.values()),
                               key=lambda x: x["id"]) if privilegiado else [],
            "negocios_dia": ([{"dia": d, "itens": sorted(c_negocios_dia[d], key=lambda x: x["hora"])}
                              for d in range(1, ultimo + 1)] if privilegiado else []),
        })

    por_closer.sort(key=lambda x: (bool(x.get("lideranca")), -x["total"]["planned"], x["name"]))
    return {
        "generated_at": fuso.agora_brasil().isoformat(),
        "year": ano, "month": mes,
        "month_label": f"{MESES_NOME[mes-1]}/{ano}",
        "carimbo": carimbo(),
        "days": [{"dia": d, "counter": combined_days[d]} for d in range(1, ultimo + 1)],
        "month_total": month_total,
        "por_time": dict(por_time),
        "por_time_days": {t: [{"dia": d, "counter": dd[d]} for d in range(1, ultimo + 1)]
                          for t, dd in por_time_days.items()},
        "por_closer": por_closer,
        "geral_dia": ([{"dia": d, "itens": sorted(geral_dia[d], key=lambda x: (x["hora"], x["closer"]))}
                       for d in range(1, ultimo + 1)] if privilegiado else []),
        "nao_encontrados": nao_encontrados,
    }


def _filtra(pessoas, time_filtro, quem_filtro):
    if time_filtro and time_filtro.upper() != "TODOS":
        pessoas = {n: t for n, t in pessoas.items() if str(t).upper() == time_filtro.upper()}
    if quem_filtro and quem_filtro.upper() != "TODOS":
        pessoas = {n: t for n, t in pessoas.items() if n == quem_filtro}
    return pessoas


def build_dashboard(ano, mes, time_filtro=None, closer_filtro=None, privilegiado=False):
    ctx = contexto_mes(ano, mes)
    return _build_dashboard_generico(_filtra(ctx["closers"], time_filtro, closer_filtro), ano, mes,
                                     privilegiado, com_validada=False)


def build_dashboard_sdr(ano, mes, time_filtro=None, sdr_filtro=None, privilegiado=False):
    ctx = contexto_mes(ano, mes)
    return _build_dashboard_generico(_filtra(ctx["sdrs"], time_filtro, sdr_filtro), ano, mes,
                                     privilegiado, com_validada=True, lideres=ctx["lideres"])


# ---------- auditoria: para quais closers cada SDR marca ----------

def _ranking_por_criador(auditados, ano, mes):
    """auditados = {nome: label}. Reunioes validadas (M6) de cada pessoa, agrupadas pelo dono do negocio."""
    ctx = contexto_mes(ano, mes)
    P = dados_periodo(ano, mes)
    users = ctx["users"]
    val = m6.reunioes_validadas(P["acts"], P["ini"], P["fim"], deals_validados=P["deals_validados"],
                                dono_do_deal=P["dono_do_deal"], sdr_ids=ctx["sdr_ids"],
                                lideranca_ids=ctx["lideranca_ids"], lideranca_que_agenda_ids=ctx["lq_ids"])
    saida = []
    for nome, label in sorted(auditados.items()):
        uid = ctx["id_por_nome"].get(norm(nome))
        contadores, negocios = defaultdict(int), defaultdict(list)
        total = 0
        for a in val.get(uid, []):
            did = a.get("deal_id")
            dono = P["dono_do_deal"].get(did)
            closer = users.get(dono) or f"user {dono}"
            contadores[closer] += 1
            total += 1
            negocios[closer].append({"id": did, "title": (P["deals"].get(did) or {}).get("title") or ("Negocio " + str(did)),
                                     "url": PIPEDRIVE_BASE_URL + "/deal/" + str(did)})
        ranking = sorted(contadores.items(), key=lambda x: (-x[1], x[0]))
        saida.append({
            "nome": nome, "label": label, "encontrado": uid is not None, "total": total,
            "closers": [{"closer": k, "qtd": v, "negocios": sorted(negocios[k], key=lambda x: x["id"])}
                        for k, v in ranking],
        })
    return saida


def build_auditoria_sdr(ano, mes):
    ctx = contexto_mes(ano, mes)
    lideres = ctx["lideres"]
    sdrs = {n: t for n, t in ctx["sdrs"].items() if n not in lideres}
    return {
        "year": ano, "month": mes, "month_label": f"{MESES_NOME[mes-1]}/{ano}",
        "carimbo": carimbo(),
        "sdrs": _ranking_por_criador(sdrs, ano, mes),
        "liderancas": _ranking_por_criador(dict(lideres), ano, mes),
    }


# ---------- evolucao por horario (LP1 + FR2 + L3) ----------

def _deals_atualizados_desde(desde):
    """Deals mexidos desde `desde` (inclui reaplicacoes: a LP1 usa a Data da ultima aplicacao).
    Busca unica por periodo, compartilhada por todos os SDRs."""
    ini_utc = datetime(desde.year, desde.month, desde.day, tzinfo=fuso.TZ_BR).astimezone(fuso.UTC)
    return pipedrive.deals(updated_since=ini_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
                           include_option_labels="true")


def _deals_do_periodo(desde):
    return _cache_seguro(("deals_lp1", desde.isoformat()), 900,
                         lambda: _deals_atualizados_desde(desde), tamanho=len)


def _atividades_criadas(desde, ate):
    """Reunioes criadas (add_time, Brasilia) entre desde e ate. A busca e pelo dia da reuniao: vai de
    uma semana antes (registro retroativo) ate 60 dias depois do fim."""
    ini = desde - timedelta(days=7)
    fim = ate + timedelta(days=60)
    return _cache_seguro(("reunioes_criadas", desde.isoformat(), ate.isoformat()), 900,
                         lambda: pipedrive.atividades_do_periodo(ini, fim, tipos=[tipo_atividade("reuniao")]),
                         tamanho=len)


def evolucao_horario_sdr(nome_sdr, desde_str, ate_str=None):
    """Para UMA SDR, entre `desde` e `ate` (Brasilia):
    - Leads por hora: LP1 (primeiro proprietario), hora da Data da ultima aplicacao
      (sem hora na data, hora do add_time do deal em Brasilia).
    - Agendados por hora: base da FR2 (reuniao criada pela SDR, sem as da IA), hora do add_time em Brasilia.
    - Prazo: L3 (dias entre a criacao e o dia da reuniao). Faixas mesmo dia / dia seguinte / mais adiante
      sao escolha do painel. Registro retroativo (negativo) fica fora das faixas e e contado a parte."""
    hoje = fuso.hoje_brasil()
    ctx = contexto_mes(hoje.year, hoje.month)
    sdr_id = ctx["id_por_nome"].get(norm(nome_sdr))
    if not sdr_id:
        return {"erro": "SDR nao encontrada no Pipedrive", "por_hora": [], "total": {}}
    try:
        desde = datetime.strptime(desde_str, "%Y-%m-%d").date()
    except Exception:
        desde = hoje - timedelta(days=7)
    try:
        ate = datetime.strptime(ate_str, "%Y-%m-%d").date() if ate_str else hoje
    except Exception:
        ate = hoje

    por_hora = {h: {"leads": 0, "agendados": 0} for h in range(24)}

    # ---- leads: LP1 ----
    sdr_nomes = {norm(n) for n in ctx["sdrs"]}
    opcoes_q = _cache_seguro(("opcoes_qualificador",), 3600, lambda: pipedrive.opcoes_campo(campo("qualificador")))
    for d in _deals_do_periodo(desde):
        if not lp1.entra(d):
            continue
        quem = lp1.primeiro_proprietario(d, sdr_nomes, ctx["users"], opcoes_q)
        if norm(quem) != norm(nome_sdr):
            continue
        ap, tem_hora = fuso.ultima_aplicacao(cf(d, campo("ultima_aplicacao")))
        criado = fuso.para_brasil(d.get("add_time"))
        if ap is None:
            marco_dia, hora = (criado.date() if criado else None), (criado.hour if criado else None)
        elif tem_hora:
            marco_dia, hora = ap.date(), ap.hour
        else:                                   # so data: dia da aplicacao, hora do add_time
            marco_dia, hora = ap, (criado.hour if criado else None)
        if marco_dia is None or hora is None or not (desde <= marco_dia <= ate):
            continue
        por_hora[hora]["leads"] += 1

    # ---- agendados: FR2 / prazo: L3 ----
    prazo = {"mesmo_dia": 0, "dia_seguinte": 0, "mais_adiante": 0, "sem_data": 0, "retroativos": 0}
    reu = tipo_atividade("reuniao")
    mine = [a for a in _atividades_criadas(desde, ate)
            if a.get("type") == reu and a.get("deal_id") and responsavel_id(a) == sdr_id and not criada_pela_ia(a)]
    for a in deduplicar(mine):
        criada = fuso.para_brasil(a.get("add_time"))
        if criada is None or not (desde <= criada.date() <= ate):
            continue
        por_hora[criada.hour]["agendados"] += 1
        dias, retro = l3.lead_time_agendamento(a)
        if retro:
            prazo["retroativos"] += 1
        elif dias is None:
            prazo["sem_data"] += 1
        elif dias == 0:
            prazo["mesmo_dia"] += 1
        elif dias == 1:
            prazo["dia_seguinte"] += 1
        else:
            prazo["mais_adiante"] += 1

    total_leads = sum(v["leads"] for v in por_hora.values())
    total_ag = sum(v["agendados"] for v in por_hora.values())
    base_prazo = total_ag - prazo["retroativos"]
    return {
        "sdr": nome_sdr, "desde": desde.isoformat(), "ate": ate.isoformat(),
        "por_hora": [{"hora": h, "leads": por_hora[h]["leads"], "agendados": por_hora[h]["agendados"]} for h in range(24)],
        "total": {"leads": total_leads, "agendados": total_ag},
        "taxa_agendamento": round(total_ag / total_leads * 100, 1) if total_leads else 0.0,
        "prazo_agendamento": prazo,
        "pct_agendado_dia_seguinte": round(prazo["dia_seguinte"] / base_prazo * 100, 1) if base_prazo > 0 else 0.0,
        "carimbo": carimbo(extra="Leads: LP1 por Data da última aplicação · Prazo: mesmo dia = 0 dia, dia seguinte = 1, mais adiante = 2+ (L3)"),
    }


# ---------- taxas: reunioes marcadas fora da escala (OP2) ----------

def _escala():
    try:
        return _cache_seguro(("escala_crn",), 600, fontes.carregar_escala), None
    except Exception as e:
        return {}, str(e)


def reunioes_fora_da_escala(ano, mes, date_de=None, date_ate=None):
    """Por SDR do mes: reunioes FEITAS e VALIDADAS (Sim/vazio), CRIADAS por ela (creator = responsavel),
    cujo negocio tem Data da ultima aplicacao no mes, e quantas foram criadas fora do turno (OP2).
    Escala pela chave da CRN: nome + funil do deal + dia da semana. Sem escala no dia = nao avaliada."""
    ctx = contexto_mes(ano, mes)
    P = dados_periodo(ano, mes)
    escala, erro_escala = _escala()
    pipelines = funis_pipedrive()
    di, df = (date_de, date_ate) if (date_de and date_ate) else (P["ini"], P["fim"])
    reu = tipo_atividade("reuniao")
    por_criador = defaultdict(list)
    for a in deduplicar([x for x in P["acts"] if x.get("type") == reu and _feita(x) and x.get("deal_id")]):
        c = a.get("creator_user_id")
        c = c.get("id") if isinstance(c, dict) else c
        if c is None or criada_pela_ia(a):
            continue
        dia = fuso.atividade_dia(a)
        if dia and di <= dia <= df:
            por_criador[c].append(a)

    lideres = ctx["lideres"]
    resultado = []
    hoje = fuso.hoje_brasil()
    for nome, time_sdr in sorted(ctx["sdrs"].items()):
        uid = ctx["id_por_nome"].get(norm(nome))
        if uid is None:
            resultado.append({"nome": nome, "time": time_sdr, "entrada": None, "saida": None,
                              "lideranca": lideres.get(nome), "total_mes": 0, "fora_da_escala": 0,
                              "pct_fora_escala": 0.0, "exemplos": [], "erro": "SDR nao encontrada no Pipedrive"})
            continue
        total = fora = sem_escala = 0
        exemplos = []
        for a in por_criador.get(uid, []):
            deal = P["deals"].get(a.get("deal_id")) or {}
            ap, _ = fuso.ultima_aplicacao(cf(deal, campo("ultima_aplicacao")))
            if not fuso.no_mes(ap, ano, mes):
                continue                                  # nao e "lead do mes" pela ultima aplicacao
            if P["status_do_deal"].get(a.get("deal_id")) == "nao":
                continue                                  # so validadas (Sim ou vazio)
            funil = pipelines.get(deal.get("pipeline_id"), "")
            r = op2.fora_da_escala(a, escala, nome, funil) if not erro_escala else None
            if r is None:
                sem_escala += 1
                continue
            total += 1
            if r:
                fora += 1
                if len(exemplos) < 15:
                    criada = fuso.para_brasil(a.get("add_time"))
                    exemplos.append({"deal_id": a.get("deal_id"),
                                     "titulo": deal.get("title") or ("Negocio " + str(a.get("deal_id"))),
                                     "data_hora_criacao": criada.strftime("%d/%m/%Y %H:%M") if criada else "",
                                     "url": PIPEDRIVE_BASE_URL + "/deal/" + str(a.get("deal_id"))})
        entrada = saida = None
        for (nn, _sub, dia_sem), (e, s) in escala.items():
            if nn == norm(nome) and dia_sem == fontes.DIAS[hoje.weekday()]:
                entrada, saida = e.strftime("%H:%M:%S"), s.strftime("%H:%M:%S")
                break
        resultado.append({"nome": nome, "time": time_sdr, "lideranca": lideres.get(nome),
                          "entrada": entrada, "saida": saida, "total_mes": total, "fora_da_escala": fora,
                          "sem_escala": sem_escala,
                          "pct_fora_escala": round(fora / total * 100, 1) if total else 0.0, "exemplos": exemplos})
    tg = sum(r["total_mes"] for r in resultado)
    fg = sum(r["fora_da_escala"] for r in resultado)
    if date_de and date_ate:
        periodo_label = f"{date_de.strftime('%d/%m/%Y')} a {date_ate.strftime('%d/%m/%Y')} (leads de {MESES_NOME[mes-1]}/{ano})"
    else:
        periodo_label = f"{MESES_NOME[mes-1]}/{ano}"
    return {
        "ano": ano, "mes": mes, "month_label": periodo_label,
        "escala_configurada": erro_escala is None and bool(escala), "erro_escala": erro_escala,
        "sdrs": resultado,
        "total": {"total_mes": tg, "fora_da_escala": fg, "pct_fora_escala": round(fg / tg * 100, 1) if tg else 0.0},
        "carimbo": carimbo(extra="Fora da escala: OP2 (nome + funil + dia da semana); sem escala no dia não entra na base"),
    }


# ---------- ligacoes do dia (AT1) ----------

LIGACOES_TTL = 120   # ligacoes do dia mudam toda hora; cache curto


def ligacoes_do_dia(time_filtro="SNIPER"):
    """{nome: ligacoes feitas HOJE} dos SDRs + lideranca do time. Hoje = dia de Brasilia;
    AT1: type call, feita, com negocio, no dia do due_date (Brasilia), do responsavel."""
    hoje = fuso.hoje_brasil()
    ctx = contexto_mes(hoje.year, hoje.month)
    nomes = [n for n, t in ctx["sdrs"].items() if str(t).upper() == time_filtro.upper()]

    def buscar():
        acts = pipedrive.atividades_do_periodo(hoje, hoje, tipos=[tipo_atividade("ligacao")], done=True)
        return at1.ligacoes_feitas(acts, hoje, hoje)
    por_resp = _cache_seguro(("ligacoes", hoje.isoformat()), LIGACOES_TTL, buscar)
    por_pessoa = {}
    for nome in nomes:
        uid = ctx["id_por_nome"].get(norm(nome))
        if uid is not None:
            por_pessoa[nome] = len(por_resp.get(uid, []))
    return {"date": hoje.isoformat(), "team": time_filtro, "por_pessoa": por_pessoa,
            "total": sum(por_pessoa.values()), "carimbo": carimbo(extra="Ligações: AT1 (due_date em Brasília)")}



def _parse_data_flex(texto):
    """Data em 'DD/MM/AAAA' ou 'AAAA-MM-DD' (com ou sem hora depois). None se vazia/invalida."""
    t = (texto or "").strip()
    if not t:
        return None
    t = t.replace(",", " ").split(" ")[0]
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d/%m/%y"):
        try:
            return datetime.strptime(t, fmt).date()
        except ValueError:
            continue
    return None


def carrega_distribuicao_resumo():
    """Le a aba de resumo de distribuicao de leads (planilha config_dashs):
    por colaborador, quantos leads ele deveria receber (QTD_REUNIOES),
    quantos ja recebeu hoje (RECEBIDAS_HOJE) e quantas reunioes atuais
    ele tem hoje (REUNIOES_ATUAIS_HOJE)."""
    if not DISTRIBUICAO_RESUMO_CSV_URL:
        raise RuntimeError("DISTRIBUICAO_RESUMO_CSV_URL nao configurada")
    with _lock:
        c = _cache.get("dist_resumo")
        if c and time.time() - c["ts"] < TTL:
            return c["rows"]
    resp = requests.get(DISTRIBUICAO_RESUMO_CSV_URL, timeout=30, allow_redirects=True,
                        headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    resp.encoding = "utf-8"
    reader = csv.DictReader(io.StringIO(resp.text))

    def _int(v):
        v = (v or "").strip()
        return int(v) if v.lstrip("-").isdigit() else 0

    rows = []
    for r in reader:
        cargo = (r.get("CARGO") or "").strip()
        qtd = _int(r.get("QTD_REUNIOES"))
        atuais = _int(r.get("REUNIOES_ATUAIS_HOJE"))
        # VEZES_NA_FILA: peso na fila; vazio (ou invalido/0) vale 1
        vezes = _int(r.get("VEZES_NA_FILA")) or 1
        # status na fila (regras da planilha): so reconhece quem tem "Closer" no cargo;
        # meta 0 = so recebe credito de negocios reatribuidos, nunca entra na fila;
        # a fila e o teto da meta usam REUNIOES_ATUAIS_HOJE (nao RECEBIDAS_HOJE)
        if "closer" not in norm(cargo):
            status_fila = "cargo_invalido"
        elif qtd <= 0:
            status_fila = "sem_meta"
        elif atuais >= qtd:
            status_fila = "na_meta"
        else:
            status_fila = "na_fila"
        rows.append({
            "nome": (r.get("NOME") or "").strip(),
            "email": (r.get("EMAIL") or "").strip(),
            "cargo": cargo,
            "qtd_reunioes": qtd,
            "recebidas_hoje": _int(r.get("RECEBIDAS_HOJE")),
            "reunioes_atuais_hoje": atuais,
            "vezes_na_fila": vezes,
            "ajuste_fila": _int(r.get("AJUSTE_FILA")),
            "status_fila": status_fila,
            "falta_para_meta": max(0, qtd - atuais) if qtd > 0 else 0,
        })
    with _lock:
        _cache["dist_resumo"] = {"ts": time.time(), "rows": rows}
    return rows


def carrega_distribuicao_log():
    """Le a aba de log detalhado de distribuicao de leads (planilha
    config_dashs): cada linha e um lead distribuido a alguem, com
    DATA_HORA exata -- inclui trocas de proprietario (ALTERADO='Sim',
    NOVO_PROPRIETARIO preenchido). Este e o registro historico de
    "quando o lead mudou de dono" que o Pipedrive nao guarda sozinho."""
    if not DISTRIBUICAO_LOG_CSV_URL:
        raise RuntimeError("DISTRIBUICAO_LOG_CSV_URL nao configurada")
    with _lock:
        c = _cache.get("dist_log")
        if c and time.time() - c["ts"] < TTL:
            return c["rows"]
    resp = requests.get(DISTRIBUICAO_LOG_CSV_URL, timeout=30, allow_redirects=True,
                        headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    resp.encoding = "utf-8"
    reader = csv.DictReader(io.StringIO(resp.text))

    rows = []
    for r in reader:
        data_hora_str = (r.get("DATA_HORA") or "").strip()
        dt = None
        try:
            dt = datetime.strptime(data_hora_str, "%d/%m/%Y, %H:%M:%S")
        except ValueError:
            pass
        reunioes_dia = (r.get("REUNIOES_DO_DIA") or "").strip()
        outro_dia_raw = (r.get("AGENDADA_OUTRO_DIA") or "").strip()
        dur_raw = (r.get("REUNIAO_DURACAO_MIN") or "").strip()
        rows.append({
            # REUNIAO_DATA / HORA / DURACAO_MIN (padrao 60) -- servem p/ checar escala e choque de horario
            "reuniao_data": _parse_data_flex(r.get("REUNIAO_DATA")),
            "reuniao_hora": _parse_hora_hhmmss(r.get("REUNIAO_HORA")),
            "duracao_min": int(float(dur_raw)) if dur_raw.replace(".", "", 1).isdigit() and float(dur_raw) > 0 else 60,
            "creditada_em": (r.get("CREDITADA_EM") or "").strip(),
            # AGENDADA_OUTRO_DIA agora traz a DATA da reuniao quando nao e hoje (antes era "Sim")
            "outro_dia_valor": outro_dia_raw,
            "data_hora": data_hora_str,
            "dt": dt,  # objeto datetime p/ ordenar -- nao serializavel, remover antes de devolver via API
            "deal_id": (r.get("DEAL_ID") or "").strip(),
            "colaborador": (r.get("COLABORADOR") or "").strip(),
            "funil": (r.get("FUNIL") or "").strip(),
            "reunioes_do_dia": int(reunioes_dia) if reunioes_dia.isdigit() else None,
            "alterado": (r.get("ALTERADO") or "").strip().lower() == "sim",
            "novo_proprietario": (r.get("NOVO_PROPRIETARIO") or "").strip() or None,
            "agendada_outro_dia": norm(outro_dia_raw) not in ("", "nao", "n", "0", "false"),
        })
    with _lock:
        _cache["dist_log"] = {"ts": time.time(), "rows": rows}
    return rows


def carrega_escala_comercial():
    """Le a aba "escala_comercial" da planilha config_dashs: Entrada/Saida
    de turno de cada pessoa comercial. Usada na aba "Taxas %" pra saber se
    uma reuniao foi marcada DEPOIS do fim do turno de quem marcou.
    Nomes de coluna tolerantes a grafia/acento (ex.: "Saida" ou "Saída")."""
    if not ESCALA_COMERCIAL_CSV_URL:
        raise RuntimeError("ESCALA_COMERCIAL_CSV_URL nao configurada")
    with _lock:
        c = _cache.get("escala")
        if c and time.time() - c["ts"] < TTL:
            return c["rows"]
    resp = requests.get(ESCALA_COMERCIAL_CSV_URL, timeout=30, allow_redirects=True,
                        headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    resp.encoding = "utf-8"
    reader = csv.DictReader(io.StringIO(resp.text))

    def achar(*nomes):
        for col in nomes:
            alvo = norm(col)
            for h in reader.fieldnames or []:
                if norm(h) == alvo:
                    return h
        return None

    col_nome = achar("Nome", "NOME")
    col_entrada = achar("Entrada", "ENTRADA")
    col_saida = achar("Saida", "Saída", "SAIDA", "SAÍDA")
    col_cargo = achar("Cargo", "CARGO")
    col_time = achar("Subarea", "Time", "Equipe", "SUBAREA", "TIME")
    col_dias = achar("dias_semana", "Dias da semana", "Dias")
    faltando = [n for n, c in [("Nome", col_nome), ("Saida", col_saida)] if not c]
    if faltando:
        print("[escala_comercial] Colunas nao encontradas:", faltando, "| Cabecalhos:", reader.fieldnames)

    rows = []
    for r in reader:
        nome = (r.get(col_nome) or "").strip() if col_nome else ""
        if not nome:
            continue
        rows.append({
            "nome": nome,
            "entrada": (r.get(col_entrada) or "").strip() if col_entrada else "",
            "saida": (r.get(col_saida) or "").strip() if col_saida else "",
            "cargo": norm(r.get(col_cargo)) if col_cargo else "",
            "time": (r.get(col_time) or "").strip().upper() if col_time else "",
            "dias": _parse_dias_semana(r.get(col_dias)) if col_dias else None,
        })
    with _lock:
        _cache["escala"] = {"ts": time.time(), "rows": rows}
    return rows


_DIAS_NOMES = {"seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sab": 5, "dom": 6}


def _parse_dias_semana(texto):
    """Dias da semana em que o turno vale -> set de 0..6 (0 = segunda). Aceita nomes
    ("seg,ter,qua", "Segunda a Sexta", "seg-sex") e numeros ISO 1..7 (1 = segunda, 7 = domingo;
    0 tambem vale domingo). Vazio ou ilegivel = None (turno vale todos os dias)."""
    import re as _re
    t = norm(texto)
    if not t:
        return None
    intervalo = bool(_re.search(r"\ba\b|-|ate", t))
    seq = []
    for w in _re.findall(r"[a-z]+|\d", t):
        if w in ("a", "ate", "e"):
            continue
        if w.isdigit():
            n = int(w)
            seq.append(6 if n in (0, 7) else (n - 1 if 1 <= n <= 6 else None))
        else:
            seq.append(_DIAS_NOMES.get(w[:3]))
    if not seq or None in seq:
        return None
    if intervalo and len(seq) == 2:
        out, i = set(), seq[0]
        while True:
            out.add(i)
            if i == seq[1]:
                break
            i = (i + 1) % 7
        return out
    return set(seq)


def escala_turno_por_nome():
    """{nome_normalizado: {"entrada": time|None, "saida": time|None, "dias": set|None}}"""
    out = {}
    for r in carrega_escala_comercial():
        out[norm(r["nome"])] = {"entrada": _parse_hora_hhmmss(r["entrada"]),
                                "saida": _parse_hora_hhmmss(r["saida"]), "dias": r.get("dias")}
    return out


def escala_saida_por_nome():
    """{nome_normalizado: 'HH:MM:SS'} -- horario de fim de turno de cada
    pessoa, tirado da escala comercial."""
    out = {}
    for r in carrega_escala_comercial():
        if r["saida"]:
            out[norm(r["nome"])] = r["saida"]
    return out


def escala_entrada_por_nome():
    """{nome_normalizado: 'HH:MM:SS'} -- horario de INICIO de turno de cada
    pessoa, tirado da escala comercial. Usada junto com escala_saida_por_nome
    na aba "Taxas %": uma reuniao marcada ANTES da entrada e tao "fora da
    escala" quanto uma marcada DEPOIS da saida (confirmado com o usuario a
    partir dos casos #112559 e #410476, ambos criados de manha, antes do
    turno da SDR comecar, e que so contavam como fora quando criados DEPOIS
    do fim do turno)."""
    out = {}
    for r in carrega_escala_comercial():
        if r["entrada"]:
            out[norm(r["nome"])] = r["entrada"]
    return out


def _parse_hora_hhmmss(texto):
    """Converte 'HH:MM' ou 'HH:MM:SS' num datetime.time. None se invalido/vazio."""
    texto = (texto or "").strip()
    for fmt in ("%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(texto[:8], fmt).time()
        except ValueError:
            continue
    return None


# ---------- rotas ----------

def _erro(e):
    import traceback
    traceback.print_exc()
    if isinstance(e, fontes.FonteInvalida):
        return jsonify({"error": f"Planilha: {e}"}), 500
    return jsonify({"error": str(e)}), 500


@app.route("/crn-versao")
def crn_versao():
    """Regra 11 da CRN: publico, so a versao das regras em uso (nenhum dado)."""
    return jsonify({"versao": crn.versao()})


@app.route("/api/init")
def api_init():
    hoje = fuso.hoje_brasil()
    teams, aviso = [], None
    try:
        ctx = contexto_mes(hoje.year, hoje.month)
        teams = sorted({t for t in list(ctx["sdrs"].values()) + list(ctx["closers"].values())})
    except Exception as e:
        aviso = str(e)
        print("[init] contexto do mes indisponivel:", e)
    out = {
        "months": meses_disponiveis(),
        "current": f"{hoje.year}-{hoje.month:02d}",
        "teams": ["Todos"] + teams,
        "refresh_seconds": REFRESH_SECONDS,
        "crn": crn.versao(),
    }
    if aviso:
        out["aviso"] = aviso
    return jsonify(out)


@app.route("/api/closers")
def api_closers():
    ano, mes = parse_ym(request.args.get("month", ""))
    try:
        return jsonify({"closers": ["Todos"] + sorted(contexto_mes(ano, mes)["closers"].keys())})
    except Exception as e:
        return _erro(e)


@app.route("/api/dashboard")
def api_dashboard():
    ano, mes = parse_ym(request.args.get("month", ""))
    try:
        return jsonify(build_dashboard(ano, mes, request.args.get("team"), request.args.get("closer"),
                                       privilegiado=eh_privilegiado(request)))
    except Exception as e:
        return _erro(e)


@app.route("/api/sdrs")
def api_sdrs():
    ano, mes = parse_ym(request.args.get("month", ""))
    try:
        return jsonify({"sdrs": ["Todos"] + sorted(contexto_mes(ano, mes)["sdrs"].keys())})
    except Exception as e:
        return _erro(e)


@app.route("/api/dashboard_sdr")
def api_dashboard_sdr():
    ano, mes = parse_ym(request.args.get("month", ""))
    try:
        return jsonify(build_dashboard_sdr(ano, mes, request.args.get("team"), request.args.get("sdr"),
                                           privilegiado=eh_privilegiado(request)))
    except Exception as e:
        return _erro(e)


@app.route("/api/ligacoes_hoje")
def api_ligacoes_hoje():
    team = request.args.get("team") or "SNIPER"
    try:
        return jsonify(ligacoes_do_dia(team))
    except Exception as e:
        return _erro(e)


@app.route("/api/auditoria_sdr")
def api_auditoria_sdr():
    # auditoria revela pra quem cada SDR marca -> so privilegiado
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito", "sdrs": []}), 401
    ano, mes = parse_ym(request.args.get("month", ""))
    try:
        return jsonify(build_auditoria_sdr(ano, mes))
    except Exception as e:
        return _erro(e)


@app.route("/api/evolucao_sdr")
def api_evolucao_sdr():
    # mostra quantos leads entraram por hora -> dado sensivel, so privilegiado
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    nome_sdr = request.args.get("sdr", "").strip()
    if not nome_sdr:
        return jsonify({"error": "informe ?sdr=<nome>"}), 400
    desde = request.args.get("desde", "").strip()
    if not desde:
        hoje = fuso.hoje_brasil()                       # default: segunda-feira desta semana
        desde = (hoje - timedelta(days=hoje.weekday())).isoformat()
    ate = request.args.get("ate", "").strip() or None   # opcional -- sem isso, vai ate hoje
    try:
        return jsonify(evolucao_horario_sdr(nome_sdr, desde, ate))
    except Exception as e:
        return _erro(e)


@app.route("/api/taxas_escala")
def api_taxas_escala():
    # reunioes fora do horario de escala -- dado operacional interno, so privilegiado
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    ano, mes = parse_ym(request.args.get("month", ""))
    date_de = date_ate = None
    de_str = request.args.get("de", "").strip()
    ate_str = request.args.get("ate", "").strip()
    if de_str and ate_str:
        try:
            date_de = datetime.strptime(de_str, "%Y-%m-%d").date()
            date_ate = datetime.strptime(ate_str, "%Y-%m-%d").date()
        except Exception:
            date_de = date_ate = None
    try:
        return jsonify(reunioes_fora_da_escala(ano, mes, date_de, date_ate))
    except Exception as e:
        return _erro(e)


@app.route("/api/debug_deals_owner")
def api_debug_deals_owner():
    """Diagnostico: mostra os negocios crus (add_time/update_time/status)
    de um owner, pra conferir o formato real das datas do Pipedrive.
    So privilegiado."""
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    oid = request.args.get("owner_id")
    if not oid:
        return jsonify({"error": "informe ?owner_id=<id>"}), 400
    try:
        deals = client.get_deals_by_owner(int(oid))
        resumo = [{"id": d.get("id"), "title": d.get("title"),
                   "add_time": d.get("add_time"), "update_time": d.get("update_time"),
                   "status": d.get("status")} for d in deals[:20]]
        return jsonify({"total": len(deals), "amostra": resumo})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def analisa_log_distribuicao(rows):
    """Checagens das regras da fila sobre o log (so a ULTIMA linha de cada negocio vale: as
    anteriores sao tentativas; linha ALTERADO=Sim perdeu o credito e fica fora das checagens).
    Devolve {id(linha): {"fora_escala": bool|None, "choque": bool}}.
      - fora_escala: horario da REUNIAO (nao o da distribuicao) fora do turno do closer na escala
        comercial (Entrada e Saida inclusive, e so nos dias_semana do turno). None = sem escala/horario.
      - choque: o closer tem outra reuniao que se sobrepoe (inicio < fim do outro e vice-versa;
        duracao padrao 60 min). Reunioes colando (fim = inicio) nao conflitam."""
    ultima = {}
    for r in rows:
        did = r.get("deal_id")
        if not did or not r.get("dt"):
            continue
        a = ultima.get(did)
        if a is None or r["dt"] > a["dt"]:
            ultima[did] = r
    try:
        turnos = escala_turno_por_nome()
    except Exception:
        turnos = {}
    por_closer_dia = defaultdict(list)
    for r in ultima.values():
        if r.get("alterado") or not (r.get("reuniao_data") and r.get("reuniao_hora")):
            continue
        ini = datetime.combine(r["reuniao_data"], r["reuniao_hora"])
        por_closer_dia[(norm(r["colaborador"]), r["reuniao_data"])].append(
            (ini, ini + timedelta(minutes=r.get("duracao_min") or 60), r))
    out = {}
    for (nome, dia), lst in por_closer_dia.items():
        t = turnos.get(nome)
        for ini, fim, r in lst:
            choque = any(o is not r and ini < ofim and oini < fim for oini, ofim, o in lst)
            fora = None
            if t and t.get("entrada") and t.get("saida"):
                h = ini.time()
                dentro = t["entrada"] <= h <= t["saida"]
                if t.get("dias") is not None and dia.weekday() not in t["dias"]:
                    dentro = False
                fora = not dentro
            out[id(r)] = {"fora_escala": fora, "choque": choque}
    return out


def status_reuniao_mais_recente_do_deal(deal_id):
    """Desfecho mais ATUAL da reuniao de um negocio (Distribuicao de Leads): a atividade
    meeting/no_show/reagendamento mais recente do negocio (qualquer responsavel), com o status da ST1.
    Cache curto por deal_id."""
    with _lock:
        c = _cache["acts"].get(("status_deal", deal_id))
        if c and time.time() - c["ts"] < TTL:
            return c["status"]
    try:
        acts = client.get_activities_by_deal(deal_id)
    except Exception:
        acts = []
    recente, recente_chave = None, None
    for a in acts:
        mom = fuso.atividade_momento(a)
        dia = fuso.atividade_dia(a)
        if dia is None:
            continue
        chave = (mom.replace(tzinfo=None) if mom else datetime(dia.year, dia.month, dia.day))
        if recente_chave is None or chave > recente_chave:
            recente_chave, recente = chave, a
    if recente is None:
        status = "—"
    else:
        s = st1.status(recente)
        status = "No Show" if s == "No-show" else (s or "—")
    with _lock:
        _cache["acts"][("status_deal", deal_id)] = {"ts": time.time(), "status": status}
    return status


@app.route("/api/distribuicao_resumo")
def api_distribuicao_resumo():
    """Resumo por colaborador de quantos leads deveria receber, ja
    recebeu hoje, reunioes atuais hoje, e quantos negocios voltaram pra
    ele HOJE (redistribuicao -- ALTERADO=Sim no log, mesmo escopo do
    resto do resumo). So privilegiado -- dado operacional interno."""
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    try:
        rows = carrega_distribuicao_resumo()

        # quantos negocios voltaram pra cada colaborador HOJE -- cruza
        # com o log de distribuicao (ALTERADO=Sim, DATA_HORA de hoje).
        # compara por nome NORMALIZADO (sem acento/maiusculas) -- as duas
        # abas da planilha (resumo e log) podem grafar o mesmo nome de
        # forma diferente (ex.: "Caique Klein" vs "Caíque Klein"), o que
        # fazia a contagem falhar silenciosamente pra quem tinha acento.
        #
        # o MESMO deal pode aparecer varias vezes seguidas no log (tentativas
        # de distribuicao ate fechar com alguem, confirmado com o usuario) --
        # entao so a ULTIMA linha (maior DATA_HORA) de cada deal_id no dia
        # representa o resultado final; as anteriores sao so tentativas e
        # NAO devem contar.
        hoje = fuso.hoje_brasil()
        # ALTERADO=Sim (DATA_HORA de hoje): o negocio SAIU do COLABORADOR da
        # linha e foi para NOVO_PROPRIETARIO. Conta por colaborador de origem
        # e guarda pra quem foi. Cada (deal, colaborador, destino) conta uma vez.
        alt_por_pessoa = {}
        try:
            vistos = set()
            for r in carrega_distribuicao_log():
                if not (r["dt"] and r["dt"].date() == hoje and r["alterado"]):
                    continue
                chave = norm(r["colaborador"])
                k = (r["deal_id"], chave, norm(r["novo_proprietario"]))
                if not chave or k in vistos:
                    continue
                vistos.add(k)
                alt_por_pessoa.setdefault(chave, []).append(r["novo_proprietario"] or "—")
        except Exception:
            pass  # log ainda nao configurado -- so fica sem essa coluna preenchida

        for r in rows:
            dest = alt_por_pessoa.get(norm(r["nome"]), [])
            r["alterados_hoje"] = len(dest)
            cont = {}
            for d in dest:
                cont[d] = cont.get(d, 0) + 1
            r["alterados_para"] = [{"nome": n, "qtd": q} for n, q in cont.items()]

        rows = sorted(rows, key=lambda r: r["qtd_reunioes"], reverse=True)

        total = {
            "na_fila": sum(1 for r in rows if r["status_fila"] == "na_fila"),
            "qtd_reunioes": sum(r["qtd_reunioes"] for r in rows),
            "recebidas_hoje": sum(r["recebidas_hoje"] for r in rows),
            "reunioes_atuais_hoje": sum(r["reunioes_atuais_hoje"] for r in rows),
            "alterados_hoje": sum(r["alterados_hoje"] for r in rows),
        }

        return jsonify({"resumo": rows, "total": total})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/distribuicao_log")
def api_distribuicao_log():
    """Log detalhado de distribuicao de leads (cada linha = um lead
    distribuido a alguem, com timestamp exato; ALTERADO=true quando o
    lead foi repassado depois pra outra pessoa). Filtrado pelo mes de
    referencia (?month=YYYY-MM; sem isso, usa o mes atual), mais
    recentes primeiro. So privilegiado -- dado operacional interno."""
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    mes = request.args.get("month", "")
    try:
        year, month = map(int, mes.split("-"))
    except Exception:
        hoje = fuso.hoje_brasil()
        year, month = hoje.year, hoje.month
    try:
        rows = carrega_distribuicao_log()
        todos = rows   # mesmos objetos: as checagens (escala/choque) olham o log inteiro
        rows = [r for r in rows if r["dt"] and r["dt"].year == year and r["dt"].month == month]
        rows = sorted(rows, key=lambda r: r["dt"], reverse=True)
        limit = int(request.args.get("limit", "5000") or "5000")
        rows = rows[:limit]

        # status da reuniao (Feita/No Show/Reagendada/...) -- cruza com o
        # Pipedrive, dedupe por deal_id pra nao bater a API 2x pro mesmo negocio
        status_por_deal = {}
        for r in rows:
            did = r["deal_id"]
            if did and did not in status_por_deal:
                try:
                    status_por_deal[did] = status_reuniao_mais_recente_do_deal(int(did))
                except (ValueError, TypeError):
                    status_por_deal[did] = "—"

        try:
            flags = analisa_log_distribuicao(todos)
        except Exception:
            flags = {}
        out = [{
            "data_hora": r["data_hora"], "deal_id": r["deal_id"],
            "reuniao_data": r["reuniao_data"].strftime("%d/%m/%Y") if r.get("reuniao_data") else None,
            "reuniao_hora": r["reuniao_hora"].strftime("%H:%M") if r.get("reuniao_hora") else None,
            "duracao_min": r.get("duracao_min"),
            "creditada_em": r.get("creditada_em") or None,
            "outro_dia_valor": r.get("outro_dia_valor") or None,
            "fora_escala": (flags.get(id(r)) or {}).get("fora_escala"),
            "choque": (flags.get(id(r)) or {}).get("choque", False),
            "url": (PIPEDRIVE_BASE_URL + "/deal/" + r["deal_id"]) if r["deal_id"] else None,
            "colaborador": r["colaborador"], "funil": r["funil"],
            "reunioes_do_dia": r["reunioes_do_dia"],
            "alterado": r["alterado"], "novo_proprietario": r["novo_proprietario"],
            "agendada_outro_dia": r["agendada_outro_dia"],
            "status_reuniao": status_por_deal.get(r["deal_id"], "—"),
        } for r in rows]
        return jsonify({"log": out, "total": len(rows), "year": year, "month": month})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/debug_m6")
def api_debug_m6():
    """Diagnostico (so privilegiado): para um negocio, mostra o que a M6 recebeu e o que ela decidiu.
    ?deal=<id>&month=YYYY-MM. Nao reimplementa regra: so expoe as entradas e a saida da CRN."""
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    did = request.args.get("deal", "").strip()
    if not did.isdigit():
        return jsonify({"error": "informe ?deal=<deal_id>"}), 400
    did = int(did)
    ano, mes = parse_ym(request.args.get("month", ""))
    try:
        ctx = contexto_mes(ano, mes)
        P = dados_periodo(ano, mes)
        nome = lambda uid: ctx["users"].get(uid, str(uid))
        deal = P["deals"].get(did)
        acts = [a for a in P["acts"] if a.get("deal_id") == did]
        val = m6.reunioes_validadas(P["acts"], P["ini"], P["fim"], deals_validados=P["deals_validados"],
                                    dono_do_deal=P["dono_do_deal"], sdr_ids=ctx["sdr_ids"],
                                    lideranca_ids=ctx["lideranca_ids"], lideranca_que_agenda_ids=ctx["lq_ids"])
        validadas = {a.get("id"): nome(r) for r, lst in val.items() for a in lst if a.get("deal_id") == did}
        dono = P["dono_do_deal"].get(did)
        return jsonify({
            "crn": crn.versao(),
            "deal": {"id": did, "no_periodo": deal is not None, "status": (deal or {}).get("status"),
                     "owner_id": dono, "owner": nome(dono),
                     "owner_eh_sdr": dono in ctx["sdr_ids"], "owner_eh_lideranca": dono in ctx["lideranca_ids"],
                     "status_validacao": P["status_do_deal"].get(did),
                     "validado": did in P["deals_validados"]},
            "atividades": [{
                "id": a.get("id"), "tipo": a.get("type"), "feita": _feita(a),
                "responsavel_id": responsavel_id(a), "responsavel": nome(responsavel_id(a)),
                "responsavel_eh_sdr": responsavel_id(a) in ctx["sdr_ids"],
                "responsavel_eh_lideranca_que_agenda": responsavel_id(a) in ctx["lq_ids"],
                "criador": nome(a.get("creator_user_id")), "criada_pela_ia": criada_pela_ia(a),
                "dia": str(fuso.atividade_dia(a)), "hora": _hora(a),
                "m6_validada_para": validadas.get(a.get("id")),
            } for a in sorted(acts, key=lambda x: (str(x.get("due_date")), str(x.get("due_time"))))],
        })
    except Exception as e:
        return _erro(e)


@app.route("/api/debug_activity")
def api_debug_activity():
    """Diagnostico: mostra o JSON cru de UMA activity, pra ver o formato
    exato do campo customizado 'Reuniao Validada?'. So privilegiado."""
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    aid = request.args.get("id")
    if not aid:
        return jsonify({"error": "informe ?id=<activity_id>"}), 400
    try:
        raw = client.get_activity_raw(aid)
        return jsonify(raw)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/debug_deal")
def api_debug_deal():
    """Diagnostico: mostra o JSON cru de UM negocio, caso o campo
    'Reuniao Validada?' esteja no deal em vez da activity. So privilegiado."""
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    did = request.args.get("id")
    if not did:
        return jsonify({"error": "informe ?id=<deal_id>"}), 400
    try:
        raw = client.get_deal_raw(did)
        return jsonify(raw)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/debug_deal_compare")
def api_debug_deal_compare():
    """Diagnostico: busca o MESMO negocio de duas formas -- fetch individual
    (/deals/{id}) e fetch em lote (/deals?ids=...), que e como o dashboard
    de verdade busca. O Pipedrive as vezes omite custom_fields na busca em
    lote; isso mostra se e esse o problema. So privilegiado."""
    if not eh_privilegiado(request):
        return jsonify({"error": "acesso restrito"}), 401
    did = request.args.get("id")
    if not did:
        return jsonify({"error": "informe ?id=<deal_id>"}), 400
    try:
        individual = client.get_deal_raw(did)
        lote_map = client.get_deals_info([did])
        em_lote = lote_map.get(int(did)) if did.isdigit() else None
        if em_lote is None:
            em_lote = lote_map.get(did)
        return jsonify({
            "busca_individual (GET /deals/{id})": individual,
            "busca_em_lote (GET /deals?ids=..., como o dashboard usa)": em_lote,
        })
    except Exception as e:
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


# CORS so de LEITURA nos dois endpoints publicos de reunioes -- permite que o
# wallpaper SNIPER (arquivo separado, fora do projeto) leia o placar do dia
@app.after_request
def cors_leitura(resp):
    if request.method == "GET" and request.path in ("/api/dashboard_sdr", "/api/dashboard", "/api/ligacoes_hoje"):
        resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


# servir o front (HTML vem embutido em front.py -- garante que vai no bundle)
# "/" = local; "/api/index" = destino do rewrite da Vercel (vercel.json)
@app.route("/")
@app.route("/api/index")
def index():
    return Response(HTML, mimetype="text/html")


# rotas de API "de verdade" que existem
_API_ROTAS = ("/crn-versao", "/api/init", "/api/closers", "/api/dashboard", "/api/sdrs", "/api/dashboard_sdr", "/api/login", "/api/me", "/api/auditoria_sdr", "/api/evolucao_sdr", "/api/debug_activity", "/api/debug_m6", "/api/debug_deal", "/api/debug_deal_compare", "/api/debug_deals_owner", "/api/distribuicao_resumo", "/api/distribuicao_log", "/api/taxas_escala", "/api/ligacoes_hoje")


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
    app.run(debug=True, port=5000, use_reloader=False)
