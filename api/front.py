# -*- coding: utf-8 -*-
"""Front-end do dashboard embutido como string.

O HTML mora aqui dentro (e nao como arquivo .html solto) porque o bundler
da Vercel so empacota os .py na funcao serverless.
"""

HTML = r"""<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>REUNIÕES</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.2.0/chartjs-plugin-datalabels.min.js"></script>
<style>
  :root {
    --bg:#f4f5f7; --card:#ffffff; --card2:#f0f1f3; --border:#dfe1e5;
    --text:#141414; --muted:#6b7280;
    --gold:#FFD700; --gold-ink:#8a6d00; --gold-soft:#fff8db;
    --done:#0f8a4d; --nsw:#c62828; --reag:#b26a00;
    --head:#0d0d0d; --head-text:#f2f2f2; --head-muted:#9a9a9a; --head-border:#2a2a2a;
  }
  * { box-sizing:border-box; }
  body { font-family:'Segoe UI',Arial,sans-serif; background:var(--bg); color:var(--text); margin:0; padding:0; }
  .page { padding:24px; max-width:1500px; margin:0 auto; }

  .site-header { background:var(--head); color:var(--head-text); padding:18px 24px 16px; border-bottom:3px solid var(--gold); }
  .site-header .hdr-top { display:flex; align-items:flex-start; justify-content:space-between; flex-wrap:wrap; gap:12px; }
  .brand { font-size:13px; font-weight:800; letter-spacing:3px; color:var(--gold); text-transform:uppercase; margin-bottom:4px; }
  h1 { font-size:23px; margin:6px 0 14px; font-weight:700; letter-spacing:1px; color:var(--head-text); }
  h1 .sep { color:var(--gold); }
  h1 .sep { color:var(--gold-ink); }

  .filters { display:flex; gap:12px; align-items:flex-end; flex-wrap:wrap; background:transparent;
             border:none; padding:0; margin:0; box-shadow:none; }
  .field { display:flex; flex-direction:column; gap:4px; }
  .field label { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }
  select { background:var(--card2); color:var(--text); border:1px solid var(--border);
           border-radius:8px; padding:8px 10px; font-size:14px; min-width:160px; }
  select:focus { outline:none; border-color:var(--gold); box-shadow:0 0 0 3px rgba(255,215,0,.18); }
  input[type=date] { background:var(--card2); color:var(--text); border:1px solid var(--border);
           border-radius:8px; padding:8px 10px; font-size:14px; }
  input[type=date]:focus { outline:none; border-color:var(--gold); box-shadow:0 0 0 3px rgba(255,215,0,.18); }
  button { background:var(--gold); color:#1a1a1a; border:none; border-radius:8px;
           padding:9px 22px; font-size:14px; font-weight:800; cursor:pointer; letter-spacing:.5px; }
  button:hover { background:#e6c200; }
  button:disabled { opacity:.5; cursor:wait; }
  /* cabecalho: todos os controles do filtro (Mes/De/Ate/Time/Closer/Pesquisar)
     menores e mais delicados -- so nesse filtro, as outras abas mantem o
     tamanho padrao acima */
  .mes-badge{padding:6px 10px;font-size:12px;font-weight:700;letter-spacing:.04em;border-radius:6px;border:1px solid #555;color:#ddd;background:#222;white-space:nowrap}
.mes-badge.atual{background:#ffd600;color:#111;border-color:#ffd600}
.site-header .filters select,
  .site-header .filters input[type=date] { min-width:0; width:132px; padding:6px 8px; font-size:12px; border-radius:6px; }
  .site-header .filters .field label { font-size:10px; }
  .site-header .filters button { padding:6px 16px; font-size:12px; border-radius:6px; }
  .updated { color:var(--head-muted); font-size:12px; margin-left:auto; align-self:center; text-align:right; }
  .auto { color:var(--gold); font-size:11px; }

  .kpi-head { font-size:13px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; margin:0 0 8px; font-weight:600; }
  .kpis { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px; }
  .kpi { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:14px 20px; min-width:130px;
         box-shadow:none; }
  .kpi.plan { border-color:var(--gold); background:var(--gold-soft); }
  .kpi .lbl { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }
  .kpi .val { font-size:30px; font-weight:800; line-height:1.1; }
  .kpi.plan .val{color:var(--text);} .kpi.done .val{color:var(--text);} .kpi.valid .val{color:var(--text);}
  .kpi.nsw .val{color:var(--text);} .kpi.reag .val{color:var(--text);}

  .month-strip { display:flex; gap:16px; flex-wrap:wrap; align-items:center; background:var(--card);
                 border:1px solid var(--border); border-left:4px solid var(--gold); border-radius:10px;
                 padding:10px 16px; margin-bottom:20px; font-size:13px; box-shadow:none; }
  .month-strip .ms-title { color:var(--gold-ink); text-transform:uppercase; letter-spacing:.5px; font-size:11px; font-weight:700; }
  .month-strip .ms-item b { font-weight:700; }

  /* cards de time */
  .team-cards { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:22px; }
  .team-card { background:rgba(74,78,86,.95); color:#f2f2f2; border:1px solid rgba(255,255,255,.10);
               border-left:4px solid var(--gold); border-radius:12px; padding:14px 18px; min-width:290px;
               box-shadow:0 3px 12px rgba(0,0,0,.14); }
  .team-card .tc-name { font-size:15px; font-weight:800; letter-spacing:1px; color:var(--gold); margin-bottom:10px; }
  .team-card .tc-row { display:flex; align-items:baseline; gap:10px; padding:5px 0; font-size:13px; flex-wrap:wrap; }
  .team-card .tc-row + .tc-row { border-top:1px dashed rgba(255,255,255,.12); }
  .team-card .tc-lbl { font-size:10px; color:#9a9a9a; text-transform:uppercase; letter-spacing:.5px; min-width:78px; font-weight:700; }
  .team-card .tc-big { font-size:20px; font-weight:800; color:#ffffff; }
  .team-card .tc-sub { color:#9a9a9a; }

  .panel { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:20px;
           box-shadow:none; }
  .panel h2 { font-size:14px; margin:0 0 12px; color:var(--gold-ink); text-transform:uppercase; letter-spacing:.5px; font-weight:700; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th, td { padding:7px 10px; text-align:center; border-bottom:1px solid var(--border); }
  th { color:var(--muted); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:.5px; }
  td.l, th.l { text-align:left; }
  tr.total td { font-weight:800; border-top:2px solid var(--gold); background:var(--gold-soft); color:var(--text); }
  tr.today td { background:var(--gold-soft); }
  .c-plan{color:var(--text); font-weight:800;} .c-done{color:var(--done);} .c-valid{color:#0a5f36; font-weight:700;} .c-nsw{color:var(--nsw);} .c-reag{color:var(--reag);}
  .warn { color:var(--nsw); font-size:12px; margin-bottom:16px; }
  .muted { color:var(--muted); }

  .matrix-wrap { overflow-x:auto; }
  table.matrix { border-collapse:collapse; font-size:12px; white-space:nowrap; min-width:100%; }
  table.matrix th, table.matrix td { padding:8px 12px; border-bottom:1px solid var(--border); text-align:center; }
  table.matrix th.closer, table.matrix td.closer { position:sticky; left:0; background:var(--card); text-align:left; z-index:2; min-width:150px; font-weight:600; }
  table.matrix th.team, table.matrix td.team { text-align:left; color:var(--muted); }
  table.matrix td, table.matrix th { border-left:1px solid #1e1e1e; }
  table.matrix thead tr.grp th.grp-day, table.matrix thead tr.grp th.grp-tot {
    border-bottom:1px solid #3a3a3a; border-left:1px solid #3a3a3a;
    color:#f2f2f2; font-size:11px; letter-spacing:.5px; background:#2a2d33; }
  table.matrix thead tr.grp th.grp-day .muted { color:#c9c9c9; }
  table.matrix thead tr.grp th.today { background:var(--gold); color:#1a1a1a; }
  table.matrix thead tr.grp th.today .muted { color:#5a4a00; }
  table.matrix tr.sub th { font-size:10px; padding:4px 8px; }
  table.matrix th.today, table.matrix td.today { background:var(--gold-soft); }
  table.matrix .mtot { border-left:2px solid var(--gold) !important; }
  table.matrix tr.foot td { border-top:2px solid var(--gold); background:var(--gold-soft); font-weight:800; }
  table.matrix tr.foot td.closer { background:var(--gold-soft); }
  table.matrix tbody tr:hover td, table.matrix tbody tr:hover td.closer { background:#f7f8fa; }

  /* dropdown criador por closer */
  td.closer .cl-wrap { display:flex; align-items:center; gap:6px; }
  td.closer .cl-toggle { cursor:pointer; user-select:none; color:var(--muted); font-size:10px;
                         border:1px solid var(--border); border-radius:4px; padding:1px 5px; line-height:1.4; }
  td.closer .cl-toggle:hover { color:var(--gold); border-color:var(--gold); }
  tr.creator-row > td { background:#f7f8fa !important; padding:6px 12px 10px !important; }
  .creator-wrap { display:flex; gap:28px; flex-wrap:wrap; align-items:stretch; padding-left:6px; }
  .creator-sep { width:1px; background:var(--border); align-self:stretch; }
  .creator-col .cc-title { font-size:10px; color:var(--text); text-transform:uppercase; letter-spacing:.5px; margin-bottom:6px; font-weight:700; }
  .creator-box { display:flex; gap:22px; flex-wrap:wrap; font-size:12px; }
  .creator-box .ci-lbl { color:var(--muted); text-transform:uppercase; letter-spacing:.5px; font-size:10px; }
  .creator-box .ci-val { font-size:18px; font-weight:800; color:var(--text); }
  .creator-box .ci-item { display:flex; flex-direction:column; gap:2px; }

  /* login / acesso privilegiado */
  .authbar { display:flex; align-items:center; gap:10px; font-size:12px; }
  .authbar .who { color:var(--gold); }
  .btn-auth { background:transparent; color:var(--head-muted); border:1px solid var(--head-border); border-radius:8px;
              padding:6px 14px; font-size:12px; font-weight:600; cursor:pointer; letter-spacing:.3px; }
  .btn-auth:hover { color:var(--gold); border-color:var(--gold); }
  .modal-bg { position:fixed; inset:0; background:rgba(0,0,0,.7); display:none; align-items:center;
              justify-content:center; z-index:100; }
  .modal-bg.show { display:flex; }
  .modal { background:#0d0d0d; color:#f2f2f2; border:1px solid #2a2a2a; border-top:3px solid var(--gold);
           border-radius:14px; padding:24px; width:320px; max-width:90vw; box-shadow:0 10px 40px rgba(0,0,0,.5); }
  .modal h3 { margin:0 0 16px; font-size:15px; color:var(--gold); text-transform:uppercase; letter-spacing:.5px; }
  .modal label { display:block; font-size:11px; color:#9a9a9a; text-transform:uppercase; letter-spacing:.5px; margin:10px 0 4px; }
  .modal input { width:100%; background:#1a1a1a; color:#f2f2f2; border:1px solid #2a2a2a;
                 border-radius:8px; padding:9px 10px; font-size:14px; }
  .modal input:focus { outline:none; border-color:var(--gold); }
  .modal .m-actions { display:flex; gap:10px; margin-top:18px; }
  .modal .m-actions button { flex:1; padding:9px; border-radius:8px; font-size:13px; font-weight:700; cursor:pointer; border:none; }
  .modal .m-ok { background:var(--gold); color:#1a1a1a; }
  .modal .m-cancel { background:#1a1a1a; color:#f2f2f2; border:1px solid #2a2a2a; }
  .modal .m-erro { color:var(--nsw); font-size:12px; margin-top:10px; min-height:14px; }

  .neg-box { margin-top:12px; padding-top:10px; border-top:1px dashed var(--border); }
  .neg-box .nb-title { font-size:10px; color:#141414 !important; text-transform:uppercase; letter-spacing:.5px; margin-bottom:6px; font-weight:700; }
  table.neg-tbl { width:100%; font-size:12px; border-collapse:collapse; }
  table.neg-tbl { table-layout:fixed; }
  table.neg-tbl th { font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px;
                     text-align:left; padding:4px 10px; border-bottom:1px solid var(--border); }
  table.neg-tbl td { padding:5px 10px; border-bottom:1px solid var(--border); text-align:left; }
  table.neg-tbl a { color:var(--text); text-decoration:none; }
  table.neg-tbl a:hover { text-decoration:underline; color:var(--gold); }
  table.neg-tbl tr:hover td { background:#eef0f3; }
  table.neg-tbl td.neg-hora { color:var(--muted); font-size:10px; white-space:nowrap; }
  table.neg-tbl td, table.neg-tbl th { overflow:hidden; text-overflow:ellipsis; }
  table.neg-tbl col.c-hora { width:60px; }
  table.neg-tbl col.c-id { width:120px; }
  table.neg-tbl col.c-status { width:90px; }
  /* linha vertical separando ID do Negocio (2a coluna), alinhada nas duas tabelas */
  table.neg-tbl th:nth-child(2), table.neg-tbl td:nth-child(2) { border-right:1px solid var(--border); }
  .status-badge { display:inline-block; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:700;
                  text-transform:uppercase; letter-spacing:.3px; white-space:nowrap; }
  .status-badge.st-planejada { background:#eceff1; color:var(--muted); }
  .status-badge.st-feita { background:#e6f6ee; color:var(--done); }
  .status-badge.st-validada { background:#e0f2e9; color:#0a5f36; }
  .status-badge.st-noshow { background:#fdeaea; color:var(--nsw); }
  .status-badge.st-reagendada { background:#fdf3e3; color:var(--reag); }
  .status-badge.st-vencida { background:#fdeaea; color:#8a1f1f; }
  .deal-badge { display:inline-block; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:700;
                text-transform:uppercase; letter-spacing:.3px; white-space:nowrap; }
  .deal-badge.dl-aberto { background:#eaf1fb; color:#1a4d8f; }
  .deal-badge.dl-ganho { background:#e6f6ee; color:var(--done); }
  .deal-badge.dl-perdido { background:#fdeaea; color:var(--nsw); }
  tr.dd-click { cursor:pointer; }
  tr.dd-click:hover td { background:#eef0f3; }
  td.dd-arrow { color:var(--muted); font-size:10px; text-align:center; width:24px; }
  tr.dd-detail > td { background:#f7f8fa !important; padding:4px 10px 12px !important; }
  .dd-box { padding-left:6px; }
  table.dd-tbl { width:100%; font-size:12px; border-collapse:collapse; }
  table.dd-tbl th { font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; text-align:left; padding:4px 10px; border-bottom:1px solid var(--border); }
  table.dd-tbl td { padding:4px 10px; border-bottom:1px solid var(--border); text-align:left; }
  table.dd-tbl td.neg-hora { color:var(--muted); font-size:10px; white-space:nowrap; }
  table.dd-tbl a { color:var(--text); text-decoration:none; }
  table.dd-tbl a:hover { text-decoration:underline; color:var(--gold-ink); }
  table.dd-tbl tr:hover td { background:#eef0f3; }

  /* abas */
  .tabs { display:flex; gap:6px; margin-bottom:18px; border-bottom:2px solid var(--border); }
  .tab { padding:9px 18px; font-size:13px; font-weight:700; cursor:pointer; color:var(--muted);
         border:none; background:transparent; border-bottom:3px solid transparent; margin-bottom:-2px;
         letter-spacing:.3px; }
  .tab:hover { color:var(--text); }
  .tab.active { color:var(--text); border-bottom-color:var(--gold); }
  .tab.locked { opacity:.5; }

  /* auditoria SDR */
  .aud-section-title { font-size:12px; font-weight:800; color:var(--muted); text-transform:uppercase;
                       letter-spacing:1px; margin:22px 0 10px; padding-bottom:6px; border-bottom:2px solid var(--border); }
  .aud-section-title:first-of-type { margin-top:8px; }
  .aud-sdr { background:var(--card); border:1px solid var(--border); border-radius:12px; margin-bottom:12px; overflow:hidden; }
  .aud-head { display:flex; align-items:center; gap:12px; padding:14px 18px; cursor:pointer; user-select:none; }
  .aud-head:hover { background:#f7f8fa; }
  .aud-arrow { color:var(--muted); font-size:11px; width:14px; }
  .aud-name { font-weight:700; font-size:15px; }
  .aud-team { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }
  .aud-total { margin-left:auto; font-size:13px; color:var(--muted); }
  .aud-total b { color:var(--text); font-size:16px; }
  .aud-body { display:none; padding:0 18px 14px; }
  .aud-body.open { display:block; }
  table.aud-tbl { width:100%; border-collapse:collapse; font-size:13px; }
  table.aud-tbl th .th-sub { display:block; font-weight:400; font-size:10px; text-transform:none;
                             letter-spacing:0; margin-top:2px; }
  table.aud-tbl td.qtd-pct { text-align:center; padding:6px 10px; }
  table.aud-tbl td.qtd-pct .qtd { font-weight:800; font-size:14px; color:var(--text); line-height:1.2; }
  table.aud-tbl td.qtd-pct .pct-sub { font-size:11px; line-height:1.2; margin-top:1px; }
  table.aud-tbl td.aud-negs { font-size:12px; }
  table.aud-tbl td.aud-negs a { color:var(--text); text-decoration:none; margin-right:6px; }
  table.aud-tbl td.aud-negs a:hover { text-decoration:underline; color:var(--gold-ink); }
  table.aud-tbl th { font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; text-align:left; padding:6px 10px; border-bottom:1px solid var(--border); }
  table.aud-tbl td { padding:7px 10px; border-bottom:1px solid var(--border); }
  table.aud-tbl td.qtd { font-weight:800; width:70px; }
  table.aud-tbl .barcell { width:45%; }
  .aud-bar { height:10px; background:var(--gold); border-radius:6px; }
  .aud-empty { color:var(--muted); font-size:13px; padding:8px 0; }

  details.diaria { margin-bottom:20px; border:1px solid var(--border); border-radius:12px; background:var(--card);
                   box-shadow:none; }
  details.diaria summary { cursor:pointer; padding:14px 16px; font-size:14px; color:var(--gold-ink);
                           text-transform:uppercase; letter-spacing:.5px; font-weight:700; list-style:none; }
  details.diaria summary::-webkit-details-marker { display:none; }
  details.diaria summary::before { content:'▸ '; }
  details.diaria[open] summary::before { content:'▾ '; }
  details.diaria .inner { padding:0 16px 16px; }
</style>
</head>
<body>
  <div class="modal-bg" id="loginModal">
    <div class="modal">
      <h3>Acesso restrito</h3>
      <label>Usuário</label>
      <input id="in-user" autocomplete="username" />
      <label>Senha</label>
      <input id="in-pass" type="password" autocomplete="current-password" />
      <div class="m-erro" id="loginErro"></div>
      <div class="m-actions">
        <button class="m-cancel" id="loginCancel">Cancelar</button>
        <button class="m-ok" id="loginOk">Entrar</button>
      </div>
    </div>
  </div>

  <header class="site-header">
    <div class="hdr-top">
      <div>
        <div class="brand">BOARD ACADEMY</div>
        <h1>REUNIÕES</h1>
      </div>
      <div class="authbar">
        <span class="who" id="authWho"></span>
        <button class="btn-auth" id="btnAuth">Entrar</button>
      </div>
    </div>
    <div class="filters">
      <div class="field" style="display:none"><label>Mês</label><select id="f-mes"></select></div>
      <div class="field"><label>Período exibido</label><div id="mes-badge" class="mes-badge">—</div></div>
      <div class="field"><label>De</label><input type="date" id="f-de"></div>
      <div class="field"><label>Até</label><input type="date" id="f-ate"></div>
      <div class="field"><label>Time</label><select id="f-time"></select></div>
      <div class="field"><label id="f-closer-label">Closer</label><select id="f-closer"></select></div>
      <button id="btn">Pesquisar</button>
      <div class="updated"><div id="updated"></div><div class="auto" id="auto"></div></div>
    </div>
  </header>

  <div class="page">
    <div class="tabs" id="tabs">
      <button class="tab active" id="tab-reunioes" data-tab="reunioes">Reuniões - Closers</button>
      <button class="tab" id="tab-sdrs" data-tab="sdrs">Reuniões - SDRs</button>
      <button class="tab" id="tab-auditoria" data-tab="auditoria">Auditoria SDR</button>
      <button class="tab" id="tab-distribuicao" data-tab="distribuicao">Distribuição</button>
      <button class="tab" id="tab-taxas" data-tab="taxas">Taxas %</button>
    </div>
    <div id="root"><div class="muted">Carregando filtros…</div></div>
    <div id="root-sdr" style="display:none"><div class="muted">Carregando filtros…</div></div>
    <div id="root-aud" style="display:none"><div class="muted">Carregando auditoria…</div></div>
    <div id="root-dist" style="display:none"><div class="muted">Carregando distribuição…</div></div>
    <div id="root-taxas" style="display:none"><div class="muted">Carregando taxas…</div></div>
  </div>

<script>
const $ = id => document.getElementById(id);
const hoje = new Date();
let TOKEN = sessionStorage.getItem('dash_token') || null;
let USUARIO = sessionStorage.getItem('dash_user') || null;

function authHeaders() {
  return TOKEN ? { 'Authorization': 'Bearer ' + TOKEN } : {};
}
function ehPriv() { return !!TOKEN; }
const diaHojeNum = hoje.getDate();
let CURRENT_MONTH = null;
let REFRESH_MS = 1200000;
let LAST_DATA = null;
let LAST_DATA_SDR = null;
let MODO_PESSOA = 'closer';  // 'closer' | 'sdr' -- controla o filtro compartilhado e o botao Pesquisar

function opt(sel, arr, getV, getL) {
  sel.innerHTML = '';
  for (const item of arr) {
    const o = document.createElement('option');
    o.value = getV(item); o.textContent = getL(item);
    sel.appendChild(o);
  }
}

function ehDefaultAtual() {
  return MODO_PESSOA === 'closer'
      && $('f-mes').value === CURRENT_MONTH
      && $('f-time').value === 'Todos'
      && $('f-closer').value === 'Todos';
}

function diasNoMes(valorMes) {
  const [y, m] = valorMes.split('-').map(Number);
  return new Date(y, m, 0).getDate();
}

// "De"/"Até" no cabeçalho substituem o antigo seletor de "Dia" e filtram a
// pagina toda: no recorte de 3 dias das abas Reuniões (Closers/SDRs) usam o
// "De" como o dia de referencia (mesmo papel que "Dia" tinha); na aba
// Taxas % usam o intervalo completo pra restringir pela data REALIZADA da
// reuniao, mantendo a condicao de leads do mes (ver buscaTaxasAba).
function dataPadraoHeader(valorMes) {
  const mes = valorMes || $('f-mes').value;
  const [y, m] = mes.split('-').map(Number);
  const n = diasNoMes(mes);
  const d = (mes === CURRENT_MONTH && diaHojeNum <= n) ? diaHojeNum : 1;
  return mes + '-' + String(d).padStart(2, '0');
}

function preencheDatasHeader() {
  const padrao = dataPadraoHeader();
  $('f-de').value = padrao;
  $('f-ate').value = padrao;
}

function atualizaBadgeMes() {
  const lab = v => {
    const m = (MESES_DISPONIVEIS || []).find(x => x.value === (v || '').slice(0, 7));
    return (m ? m.label : (v || '').slice(0, 7)).toUpperCase();
  };
  const de = $('f-de').value, ate = $('f-ate').value;
  const base = de || $('f-mes').value;
  let txt = lab(base);
  if (de && ate && de <= ate && de.slice(0, 7) !== ate.slice(0, 7)) txt += ' → ' + lab(ate);
  $('mes-badge').textContent = txt;
  const atual = (base || '').slice(0, 7) === CURRENT_MONTH;
  $('mes-badge').classList.toggle('atual', atual);
}

function diaSelecionado() {
  const v = $('f-de').value;
  if (!v) return 1;
  return parseInt(v.split('-')[2], 10);
}

async function init() {
  // valida token salvo (pode ter expirado)
  if (TOKEN) {
    try {
      const me = await (await fetch('/api/me', { headers: authHeaders() })).json();
      if (!me.privilegiado) { TOKEN = null; USUARIO = null;
        sessionStorage.removeItem('dash_token'); sessionStorage.removeItem('dash_user'); }
      else { USUARIO = me.usuario; }
    } catch (e) {}
    atualizaAuthUI();
  }
  const d = await (await fetch('/api/init')).json();
  CURRENT_MONTH = d.current;
  REFRESH_MS = (d.refresh_seconds || 1200) * 1000;
  MESES_DISPONIVEIS = d.months;
  opt($('f-mes'), d.months, x=>x.value, x=>x.label);
  $('f-mes').value = d.current;
  opt($('f-time'), d.teams, x=>x, x=>x);
  preencheDatasHeader();
  atualizaBadgeMes();
  await carregaPessoas();
  buscar(false);
  setInterval(() => { if (ehDefaultAtual()) buscar(true); }, REFRESH_MS);
}

async function carregaPessoas() {
  const endpoint = MODO_PESSOA === 'sdr' ? '/api/sdrs' : '/api/closers';
  const campo = MODO_PESSOA === 'sdr' ? 'sdrs' : 'closers';
  $('f-closer-label').textContent = MODO_PESSOA === 'sdr' ? 'SDR' : 'Closer';
  const d = await (await fetch(endpoint + '?month=' + $('f-mes').value)).json();
  opt($('f-closer'), d[campo], x=>x, x=>x);
}

$('f-mes').addEventListener('change', async () => {
  preencheDatasHeader();
  atualizaBadgeMes();
  await carregaPessoas();
  if (ABA === 'taxas') buscaTaxasAba(true);
});
// De/Ate: nas abas Reunioes (Closers/SDRs) e so recorte visual (re-renderiza
// na hora, sem nova requisicao) -- "De" define o dia do bloco Anterior/Dia/
// Seguinte, e quando os dois formam um intervalo dentro do mes exibido, a
// coluna "Total do mes" (e os cards por time / faixa do topo) passam a somar
// so os dias desse intervalo (ver periodoAtivoPara); na aba Taxas % os dois
// campos refazem a busca com o novo intervalo
function reRenderizaAbaAtual() {
  atualizaBadgeMes();
  if (MODO_PESSOA === 'sdr') { if (LAST_DATA_SDR) renderSdr(LAST_DATA_SDR); }
  else { if (LAST_DATA) render(LAST_DATA); }
  if (ABA === 'taxas') buscaTaxasAba(true);
}
// o periodo so soma quando De/Ate estao no MESMO mes que esta sendo exibido;
// se o usuario escolhe datas de outro mes (ex.: 16/09 a 30/09 com "outubro"
// selecionado), troca o filtro Mes pro mes de "De" e busca de novo, em vez de
// continuar mostrando o total do mes errado
function mesDaData(v) { return v ? v.slice(0, 7) : ''; }
// "De" manda no mes exibido; "Ate" pode cair em outro mes (intervalo que
// atravessa meses) -- os meses seguintes sao buscados a parte (buscaExtras)
async function aoMudarData(campo) {
  const de = $('f-de').value;
  atualizaBadgeMes();
  let mudouMes = false;
  if (campo === 'de') {
    const alvo = mesDaData(de);
    if (alvo && alvo !== $('f-mes').value && MESES_DISPONIVEIS.some(m => m.value === alvo)) {
      $('f-mes').value = alvo;
      await carregaPessoas();
      mudouMes = true;
    }
  }
  const dataAtual = (MODO_PESSOA === 'sdr') ? LAST_DATA_SDR : LAST_DATA;
  if (mudouMes || faltaExtras(dataAtual)) {
    AUD_CARREGADA_MES = null;
    if (ABA === 'taxas') { buscaTaxasAba(true); return; }
    if (MODO_PESSOA === 'sdr') buscarSdr(false); else buscar(false);
    return;
  }
  reRenderizaAbaAtual();
}
$('f-de').addEventListener('change', () => aoMudarData('de'));
$('f-ate').addEventListener('change', () => aoMudarData('ate'));
$('btn').addEventListener('click', () => {
  if (MODO_PESSOA === 'sdr') buscarSdr(false); else buscar(false);
});

async function buscar(isAuto) {
  // virada de dia: se a data mudou desde que a pagina abriu, recarrega
  if (isAuto) {
    const agora = new Date();
    if (agora.getDate() !== diaHojeNum && $('f-mes').value === CURRENT_MONTH) {
      location.reload();
      return;
    }
  }
  if (!isAuto) {
    $('btn').disabled = true;
    $('root').innerHTML = '<div class="muted">Buscando no Pipedrive… (pode levar alguns segundos)</div>';
  }
  const p = new URLSearchParams({
    month: $('f-mes').value, team: $('f-time').value, closer: $('f-closer').value,
  });
  try {
    const res = await fetch('/api/dashboard?' + p.toString(), { headers: authHeaders() });
    const data = await res.json();
    if (data.error) $('root').innerHTML = '<div class="warn">Erro: ' + data.error + '</div>';
    else { await buscaExtras(data, '/api/dashboard', p); LAST_DATA = data; render(data); }
  } catch (e) {
    if (!isAuto) $('root').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  } finally {
    $('btn').disabled = false;
  }
}

async function buscarSdr(isAuto) {
  if (!isAuto) {
    $('btn').disabled = true;
    $('root-sdr').innerHTML = '<div class="muted">Buscando no Pipedrive… (pode levar alguns segundos)</div>';
  }
  const p = new URLSearchParams({
    month: $('f-mes').value, team: $('f-time').value, sdr: $('f-closer').value,
  });
  try {
    const res = await fetch('/api/dashboard_sdr?' + p.toString(), { headers: authHeaders() });
    const data = await res.json();
    if (data.error) $('root-sdr').innerHTML = '<div class="warn">Erro: ' + data.error + '</div>';
    else { await buscaExtras(data, '/api/dashboard_sdr', p); LAST_DATA_SDR = data; renderSdr(data); }
  } catch (e) {
    if (!isAuto) $('root-sdr').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  } finally {
    $('btn').disabled = false;
  }
}

function dealBadge(status) {
  const mapa = { 'Aberto': 'dl-aberto', 'Ganho': 'dl-ganho', 'Perdido': 'dl-perdido' };
  const cls = mapa[status] || 'dl-aberto';
  return `<span class="deal-badge ${cls}">${status || '—'}</span>`;
}

function statusBadge(status) {
  const mapa = {
    'Planejada': 'st-planejada', 'Feita': 'st-feita', 'Validada': 'st-validada',
    'No Show': 'st-noshow', 'Reagendada': 'st-reagendada', 'Vencida': 'st-vencida',
  };
  const cls = mapa[status] || 'st-planejada';
  return `<span class="status-badge ${cls}">${status || '—'}</span>`;
}

function cols(c, comValidada) {
  const meio = comValidada ? `<td class="c-valid">${c.validada||0}</td>` : '';
  return `<td class="c-plan">${c.planned}</td><td class="c-done">${c.done}</td>${meio}`
       + `<td class="c-nsw">${c.no_show}</td><td class="c-reag">${c.reagendada}</td>`;
}

// quando "De"/"Até" do cabeçalho formam um intervalo valido DENTRO do
// mes/ano que esta sendo exibido, os totais "do mes" (faixa superior, cards
// por time e coluna final da tabela "Por Closer/SDR") passam a somar so os
// dias desse intervalo -- pedido pelo usuario pra "De"/"Até" filtrar a
// pagina toda, nao so o recorte de dia unico (Anterior/Dia/Seguinte)
// meses (YYYY-MM) cobertos pelo intervalo De..Ate -- o intervalo pode
// atravessar meses (ex.: 30/09 a 07/10); o mes de "De" e o que esta em
// `data` e os demais ficam em data._extras[mes] (buscados em buscaExtras)
function mesesDoIntervalo(deVal, ateVal) {
  const out = [];
  let [y, m] = deVal.slice(0, 7).split('-').map(Number);
  const fim = ateVal.slice(0, 7);
  for (let n = 0; n < 24; n++) {
    const k = y + '-' + String(m).padStart(2, '0');
    out.push(k);
    if (k >= fim) break;
    m++; if (m > 12) { m = 1; y++; }
  }
  return out;
}

function periodoAtivoPara(data) {
  const deVal = $('f-de').value, ateVal = $('f-ate').value;
  if (!deVal || !ateVal || deVal > ateVal) return null;
  const mesData = data.year + '-' + String(data.month).padStart(2, '0');
  if (deVal.slice(0, 7) !== mesData) return null;
  const meses = mesesDoIntervalo(deVal, ateVal);
  const segs = [];
  meses.forEach((mes, i) => {
    const d = (mes === mesData) ? data : ((data._extras || {})[mes]);
    if (!d) return;
    const ini = (i === 0) ? parseInt(deVal.slice(8, 10), 10) : 1;
    const fim = (i === meses.length - 1) ? parseInt(ateVal.slice(8, 10), 10) : 31;
    segs.push({ d, de: ini, ate: fim });
  });
  const fmt = v => v.slice(8, 10) + '/' + v.slice(5, 7);
  return { segs, rotulo: fmt(deVal) + ' a ' + fmt(ateVal) };
}

// soma os dias do intervalo em todos os meses cobertos; `getter` extrai de
// cada mes (objeto de dados) o array de dias que interessa
function somaPeriodo(periodo, getter) {
  const soma = {planned:0, done:0, validada:0, no_show:0, reagendada:0};
  for (const seg of periodo.segs) {
    for (const item of (getter(seg.d) || [])) {
      if (item.dia < seg.de || item.dia > seg.ate) continue;
      const c = item.counter || {};
      soma.planned += c.planned||0; soma.done += c.done||0; soma.validada += c.validada||0;
      soma.no_show += c.no_show||0; soma.reagendada += c.reagendada||0;
    }
  }
  return soma;
}

// soma, no periodo, os contadores "marcadas pelo proprio" / "ganhos" (met_days)
function somaMetPeriodo(periodo, nome) {
  const t = {proprio_done:0, proprio_validada:0, ganhos_done:0, ganhos_validada:0};
  for (const seg of periodo.segs) {
    const x = (seg.d.por_closer || []).find(y => y.name === nome);
    for (const it of ((x && x.met_days) || [])) {
      if (it.dia < seg.de || it.dia > seg.ate) continue;
      for (const k in t) t[k] += (it.c && it.c[k]) || 0;
    }
  }
  return t;
}

// busca os meses seguintes do intervalo (se houver) e guarda em data._extras
async function buscaExtras(data, endpoint, paramsBase) {
  data._extras = {};
  const deVal = $('f-de').value, ateVal = $('f-ate').value;
  if (!deVal || !ateVal || deVal > ateVal) return;
  const mesData = data.year + '-' + String(data.month).padStart(2, '0');
  if (deVal.slice(0, 7) !== mesData) return;
  const extras = mesesDoIntervalo(deVal, ateVal).filter(m => m !== mesData);
  await Promise.all(extras.map(async mes => {
    const p = new URLSearchParams(paramsBase);
    p.set('month', mes);
    const r = await fetch(endpoint + '?' + p.toString(), { headers: authHeaders() });
    const d = await r.json();
    if (!d.error) data._extras[mes] = d;
  }));
}

function faltaExtras(data) {
  if (!data) return false;
  const deVal = $('f-de').value, ateVal = $('f-ate').value;
  if (!deVal || !ateVal || deVal > ateVal) return false;
  const mesData = data.year + '-' + String(data.month).padStart(2, '0');
  if (deVal.slice(0, 7) !== mesData) return false;
  return mesesDoIntervalo(deVal, ateVal).some(m => m !== mesData && !(data._extras || {})[m]);
}

// no intervalo que atravessa meses, a tabela lista quem aparece em QUALQUER
// um dos meses (quem so existe no mes seguinte entra como linha sem dados do
// mes de "De"), pra soma das linhas bater com o TOTAL
function linhasPorPessoa(data, periodo) {
  const base = data.por_closer || [];
  if (!periodo) return base;
  const vistos = new Set(base.map(c => c.name));
  const extra = [];
  for (const seg of periodo.segs) {
    if (seg.d === data) continue;
    for (const c of (seg.d.por_closer || [])) {
      if (vistos.has(c.name)) continue;
      vistos.add(c.name);
      extra.push({ ...c, days: [], criadas_days: [], negocios: [], negocios_dia: [] });
    }
  }
  return base.concat(extra);
}

function renderGenerico(data, cfg) {
  $('updated').innerText = 'Atualizado: ' + new Date(data.generated_at).toLocaleString('pt-BR');
  $('auto').innerText = (cfg.ehAtual && cfg.ehAtual()) ? '● atualiza sozinho a cada ' + Math.round(REFRESH_MS/60000) + ' min' : '';
  const periodo = periodoAtivoPara(data);
  const mt = periodo ? somaPeriodo(periodo, d => d.days) : data.month_total;
  const rotuloTotal = periodo
    ? `Total do período — ${periodo.rotulo}`
    : `Total do mês — ${data.month_label}`;
  const nDays = data.days.length;
  const dSel = Math.min(diaSelecionado() || 1, nDays);
  const dSelStr = String(dSel).padStart(2,'0');
  const mesStr = String(data.month).padStart(2,'0');
  const zero = {planned:0, done:0, validada:0, no_show:0, reagendada:0};
  const getDia = (lista, n) => { const r = (lista||[]).find(x => x.dia === n); return r ? r.counter : null; };

  const tresDias = [];
  if (dSel - 1 >= 1)      tresDias.push({n: dSel-1, rot: 'Anterior'});
  tresDias.push({n: dSel, rot: 'Dia ' + dSelStr});
  if (dSel + 1 <= nDays)  tresDias.push({n: dSel+1, rot: 'Seguinte'});

  const quatro = (c, mtotCls) => {
    const meio = cfg.comValidada ? `<td class="c-valid">${c.validada||0}</td>` : '';
    return `<td class="c-plan${mtotCls?' mtot':''}">${c.planned}</td><td class="c-done">${c.done}</td>${meio}`
         + `<td class="c-nsw">${c.no_show}</td><td class="c-reag">${c.reagendada}</td>`;
  };
  const subHead = extra => {
    const meio = cfg.comValidada ? `<th class="c-valid">V</th>` : '';
    return `<th class="c-plan${extra||''}">P</th><th class="c-done">F</th>${meio}<th class="c-nsw">NS</th><th class="c-reag">R</th>`;
  };
  const nColsPorBloco = cfg.comValidada ? 5 : 4;

  // com periodo ativo, os blocos do topo mostram a soma do periodo (nao so o dia de "De")
  const diaCounter = periodo ? mt : (getDia(data.days, dSel) || zero);
  const rotuloMes = periodo ? periodo.rotulo : data.month_label;

  let html = '';

  const kpiValidaHtml = cfg.comValidada
    ? `<div class="kpi valid"><div class="lbl">Validadas</div><div class="val">${diaCounter.validada||0}</div></div>` : '';
  html += `<div class="kpi-head">${periodo ? 'Período ' + periodo.rotulo : 'Dia ' + dSelStr + '/' + mesStr}</div>`;
  html += `<div class="kpis">
    <div class="kpi plan"><div class="lbl">Planejadas</div><div class="val">${diaCounter.planned}</div></div>
    <div class="kpi done"><div class="lbl">Feitas</div><div class="val">${diaCounter.done}</div></div>
    ${kpiValidaHtml}
    <div class="kpi nsw"><div class="lbl">No Show</div><div class="val">${diaCounter.no_show}</div></div>
    <div class="kpi reag"><div class="lbl">Reagendadas</div><div class="val">${diaCounter.reagendada}</div></div>
  </div>`;

  const msValidaHtml = cfg.comValidada
    ? `<span class="ms-item c-valid">Validadas <b>${mt.validada||0}</b></span>` : '';
  html += `<div class="month-strip">
    <span class="ms-title">${rotuloTotal}</span>
    <span class="ms-item c-plan">Planejadas <b>${mt.planned}</b></span>
    <span class="ms-item c-done">Feitas <b>${mt.done}</b></span>
    ${msValidaHtml}
    <span class="ms-item c-nsw">No Show <b>${mt.no_show}</b></span>
    <span class="ms-item c-reag">Reagendadas <b>${mt.reagendada}</b></span>
  </div>`;

  const times = Object.keys(data.por_time).sort();
  if (times.length) {
    html += '<div class="team-cards">';
    for (const t of times) {
      const cd = getDia((data.por_time_days || {})[t], dSel) || zero;
      const cm = periodo ? somaPeriodo(periodo, d => (d.por_time_days || {})[t]) : data.por_time[t];
      html += `<div class="team-card">
        <div class="tc-name">${t}</div>
        <div class="tc-row">
          <span class="tc-lbl">Total dia ${dSelStr}</span>
          <span class="tc-big">${cd.planned}</span>
          <span class="tc-sub">plan · <span class="c-done">${cd.done}</span> feitas${cfg.comValidada ? ' · <span class=\"c-valid\">' + (cd.validada||0) + '</span> valid' : ''} · <span class="c-nsw">${cd.no_show}</span> NS · <span class="c-reag">${cd.reagendada}</span> reag</span>
        </div>
        <div class="tc-row">
          <span class="tc-lbl">${periodo ? 'Total período' : 'Total mês'}</span>
          <span class="tc-big">${cm.planned}</span>
          <span class="tc-sub">plan · <span class="c-done">${cm.done}</span> feitas${cfg.comValidada ? ' · <span class=\"c-valid\">' + (cm.validada||0) + '</span> valid' : ''} · <span class="c-nsw">${cm.no_show}</span> NS · <span class="c-reag">${cm.reagendada}</span> reag</span>
        </div>
      </div>`;
    }
    html += '</div>';
  }

  if (data.por_closer.length) {
    html += `<div class="panel"><h2>Por ${cfg.label}</h2><div class="matrix-wrap"><table class="matrix">`;
    html += `<thead><tr class="grp">
      <th class="closer l" rowspan="2">${cfg.label}</th><th class="team l" rowspan="2">Time</th>`;
    for (const d of tresDias) {
      const cls = (d.n === dSel) ? ' today' : '';
      html += `<th colspan="${nColsPorBloco}" class="grp-day${cls}">${d.rot} <span class="muted">${String(d.n).padStart(2,'0')}</span></th>`;
    }
    html += `<th colspan="${nColsPorBloco}" class="grp-tot mtot">${periodo ? 'Total do período' : 'Total do mês'}</th></tr>`;
    html += `<tr class="sub">`;
    for (const d of tresDias) html += subHead((d.n === dSel) ? ' today' : '');
    html += subHead(' mtot');
    html += `</tr></thead><tbody>`;

    const nCols = 2 + tresDias.length * nColsPorBloco + nColsPorBloco;
    linhasPorPessoa(data, periodo).forEach((c, i) => {
      const cid = cfg.idPrefix + '-' + i;
      const nomeCel = cfg.comCriador
        ? `<span class="cl-wrap"><span class="cl-toggle" data-cr="${cid}" id="${cid}-t">▸ criador</span>${c.name}</span>`
        : `<span class="cl-wrap"><span class="cl-toggle" data-cr="${cid}" id="${cid}-t">▸ detalhes</span>${c.name}</span>`;
      html += `<tr><td class="closer l">${nomeCel}</td><td class="team l">${c.time}</td>`;
      for (const d of tresDias) html += quatro(getDia(c.days, d.n) || zero);
      const t = periodo ? somaPeriodo(periodo, d => { const x = (d.por_closer || []).find(y => y.name === c.name); return x ? x.days : []; }) : c.total;
      html += quatro(t, true) + `</tr>`;

      let blocos = '';
      if (cfg.comCriador) {
        const crGet = (dia) => ((c.criadas_days || []).find(x => x.dia === dia) || {}).c || {proprio:0, outro:0};
        const crHoje = crGet(dSel);
        const dAnt = dSel - 1;
        const blocoCriador = (titulo, cc) => `
            <div class="creator-col">
              <div class="cc-title">${titulo}</div>
              <div class="creator-box">
                <div class="ci-item"><span class="ci-lbl">Criadas pelo próprio</span><span class="ci-val">${cc.proprio}</span></div>
                <div class="ci-item"><span class="ci-lbl">Criadas por outro</span><span class="ci-val">${cc.outro}</span></div>
                <div class="ci-item"><span class="ci-lbl">Total</span><span class="ci-val">${cc.proprio + cc.outro}</span></div>
              </div>
            </div>`;
        const sep = '<div class="creator-sep"></div>';
        if (dAnt >= 1) blocos += blocoCriador('Dia anterior ' + String(dAnt).padStart(2,'0') + '/' + mesStr, crGet(dAnt)) + sep;
        blocos += blocoCriador('Dia ' + dSelStr + '/' + mesStr, crHoje);
      }
      let negHtml = '';
      if (ehPriv()) {
        // --- negocios do DIA selecionado (com hora) ---
        const nd = ((c.negocios_dia || []).find(x => x.dia === dSel) || {}).itens || [];
        negHtml += `<div class="neg-box"><div class="nb-title">Negócios do dia ${dSelStr}/${mesStr} (${nd.length}) — clique para abrir no Pipedrive</div>`;
        if (nd.length) {
          negHtml += `<table class="neg-tbl"><colgroup><col class="c-hora"><col class="c-id"><col><col class="c-status"><col class="c-status"></colgroup><tr><th>Hora</th><th>ID</th><th>Negócio</th><th>Status</th><th>Situação</th></tr>`;
          for (const n of nd) {
            negHtml += `<tr><td class="neg-hora">${n.hora || '--:--'}</td>
              <td><a href="${n.url}" target="_blank" rel="noopener">#${n.id}</a></td>
              <td><a href="${n.url}" target="_blank" rel="noopener">${n.title}</a></td>
              <td>${statusBadge(n.status)}</td>
              <td>${dealBadge(n.status_negocio)}</td></tr>`;
          }
          negHtml += `</table>`;
        } else {
          negHtml += `<div class="muted" style="font-size:12px">Nenhum negócio nesse dia.</div>`;
        }
        negHtml += `</div>`;

        // --- negocios do MES (dedupe) ---
        const nm = c.negocios || [];
        negHtml += `<div class="neg-box"><div class="nb-title">Negócios do mês (${nm.length})</div>`;
        if (nm.length) {
          negHtml += `<table class="neg-tbl"><colgroup><col class="c-hora"><col class="c-id"><col><col class="c-status"><col class="c-status"></colgroup><tr><th></th><th>ID</th><th>Negócio</th><th>Status</th><th>Situação</th></tr>`;
          for (const n of nm) {
            negHtml += `<tr><td class="neg-hora"></td><td><a href="${n.url}" target="_blank" rel="noopener">#${n.id}</a></td>
              <td><a href="${n.url}" target="_blank" rel="noopener">${n.title}</a></td>
              <td>${statusBadge(n.status)}</td>
              <td>${dealBadge(n.status_negocio)}</td></tr>`;
          }
          negHtml += `</table>`;
        } else {
          negHtml += `<div class="muted" style="font-size:12px">Nenhum negócio no mês.</div>`;
        }
        negHtml += `</div>`;
      }
      html += `<tr class="creator-row" id="${cid}" style="display:none"><td colspan="${nCols}">
        <div class="creator-wrap">${blocos}</div>${negHtml}</td></tr>`;
    });

    html += `<tr class="foot"><td class="closer l">TOTAL</td><td class="team l"></td>`;
    for (const d of tresDias) html += quatro(getDia(data.days, d.n) || zero);
    html += quatro(mt, true) + `</tr>`;
    const legendaValid = cfg.comValidada ? ' · V = validadas' : '';
    html += `</tbody></table></div>
      <div class="muted" style="font-size:11px;margin-top:8px">P = planejadas · F = feitas${legendaValid} · NS = no-show · R = reagendadas</div></div>`;

    // ---- distribuicao: Validadas (se disponivel) ou Feitas -- numero+% empilhados na mesma celula ----
    const metricaDist = cfg.comValidada ? 'validada' : 'done';
    const campoProprio = cfg.comValidada ? 'proprio_validada' : 'proprio_done';
    const campoGanhos = cfg.comValidada ? 'ganhos_validada' : 'ganhos_done';
    const tituloDist = cfg.comValidada ? 'reuniões validadas' : 'reuniões feitas';
    const linhasDist = linhasPorPessoa(data, periodo);
    const totPessoa = new Map();
    for (const c of linhasDist) {
      totPessoa.set(c.name, periodo
        ? somaPeriodo(periodo, d => { const x = (d.por_closer || []).find(y => y.name === c.name); return x ? x.days : []; })
        : c.total);
    }
    const tp = c => totPessoa.get(c.name) || c.total;
    const metP = new Map();
    if (periodo) for (const c of linhasDist) metP.set(c.name, somaMetPeriodo(periodo, c.name));
    const campoDe = (c, campo) => periodo ? ((metP.get(c.name) || {})[campo] || 0) : (c[campo] || 0);
    const totalTodos = linhasDist.reduce((soma, c) => soma + (tp(c)[metricaDist]||0), 0);
    const totalProprioTodos = linhasDist.reduce((soma, c) => soma + campoDe(c, campoProprio), 0);
    const totalGanhosTodos = linhasDist.reduce((soma, c) => soma + campoDe(c, campoGanhos), 0);
    const distOrdenada = linhasDist.slice().sort((a,b) => (tp(b)[metricaDist]||0) - (tp(a)[metricaDist]||0));
    const celula = (num, pct) => `<td class="qtd-pct"><div class="qtd">${num}</div><div class="muted pct-sub">${pct.toFixed(1)}%</div></td>`;
    html += `<div class="panel"><h2>Distribuição por ${cfg.label} — ${tituloDist} · ${rotuloMes}</h2>
      <table class="aud-tbl">
      <tr>
        <th class="l" rowspan="2">${cfg.label}</th>
        <th colspan="2">Reuniões ${cfg.comValidada ? 'validadas' : 'feitas'} do closer<br><span class="muted th-sub">quantidade e % do total do time</span></th>
        <th colspan="1">Marcadas pelo próprio<br><span class="muted th-sub">criador = responsável, % do total do time</span></th>
        <th colspan="1">Ganhos<br><span class="muted th-sub">taxa de conversão sobre as feitas do closer</span></th>
      </tr>
      <tr><th></th><th class="barcell"></th><th></th><th></th></tr>`;
    for (const c of distOrdenada) {
      const qtd = tp(c)[metricaDist] || 0;
      const pct = totalTodos ? (qtd / totalTodos * 100) : 0;
      const qtdProprio = campoDe(c, campoProprio);
      const pctProprio = totalTodos ? (qtdProprio / totalTodos * 100) : 0;
      const qtdGanhos = campoDe(c, campoGanhos);
      const taxaConversao = qtd ? (qtdGanhos / qtd * 100) : 0;
      html += `<tr><td class="l">${c.name}</td>
        ${celula(qtd, pct)}
        <td class="barcell"><div class="aud-bar" style="width:${pct}%"></div></td>
        ${celula(qtdProprio, pctProprio)}
        ${celula(qtdGanhos, taxaConversao)}</tr>`;
    }
    const taxaConversaoTotal = totalTodos ? (totalGanhosTodos / totalTodos * 100) : 0;
    html += `<tr class="total"><td class="l">TOTAL</td>
      ${celula(totalTodos, 100)}
      <td></td>
      ${celula(totalProprioTodos, totalTodos ? (totalProprioTodos/totalTodos*100) : 0)}
      ${celula(totalGanhosTodos, taxaConversaoTotal)}</tr>`;
    html += `</table></div>`;

    // ---- distribuicao QUEBRADA POR TIME: total do time + closers dentro dele ----
    const times = Array.from(new Set(linhasDist.map(c => c.time))).sort();
    html += `<div class="panel"><h2>Reuniões ${cfg.comValidada ? 'validadas' : 'feitas'} por Time · ${rotuloMes}</h2>`;
    for (const time of times) {
      const doTime = linhasDist.filter(c => c.time === time)
        .slice().sort((a,b) => (tp(b)[metricaDist]||0) - (tp(a)[metricaDist]||0));
      const totalTime = doTime.reduce((soma, c) => soma + (tp(c)[metricaDist]||0), 0);
      html += `<div class="nb-title" style="margin-top:14px">${time} — ${totalTime} reunião(ões) no total</div>
        <table class="aud-tbl"><tr><th class="l">${cfg.label}</th><th>Quantidade</th><th>% do time</th><th class="barcell"></th></tr>`;
      for (const c of doTime) {
        const qtd = tp(c)[metricaDist] || 0;
        const pctTime = totalTime ? (qtd / totalTime * 100) : 0;
        html += `<tr><td class="l">${c.name}</td>
          ${celula(qtd, pctTime)}
          <td class="barcell"><div class="aud-bar" style="width:${pctTime}%"></div></td></tr>`;
      }
      html += `</table>`;
    }
    html += `</div>`;
  }

  const priv = ehPriv();
  // dia a dia: com periodo ativo lista so os dias do intervalo (de todos os meses cobertos)
  const diasLista = [];
  const fontes = periodo ? periodo.segs : [{ d: data, de: 1, ate: 31 }];
  for (const seg of fontes) {
    const gm = {};
    if (priv) for (const g of (seg.d.geral_dia || [])) gm[g.dia] = g.itens || [];
    for (const row of seg.d.days) {
      if (row.dia < seg.de || row.dia > seg.ate) continue;
      diasLista.push({ row, mes: seg.d.month, itens: gm[row.dia] || [], ehSel: seg.d === data && row.dia === dSel });
    }
  }
  const multiMes = periodo && periodo.segs.length > 1;
  html += `<details class="diaria"><summary>Dia a dia — todos os times (${rotuloMes})${priv ? ' · clique num dia para ver as reuniões' : ''}</summary><div class="inner">
    <table><tr>${priv ? '<th style="width:24px"></th>' : ''}<th class="l">Dia</th><th>Planejado</th><th>Feitas</th>${cfg.comValidada ? '<th>Validadas</th>' : ''}<th>No Show</th><th>Reagendadas</th></tr>`;

  for (const it0 of diasLista) {
    const row = it0.row, itens = priv ? it0.itens : [];
    const cls = it0.ehSel ? ' class="today"' : '';
    const temItens = itens.length > 0;
    const rid = 'ddrow-' + it0.mes + '-' + row.dia;
    const arrow = priv ? `<td class="dd-arrow">${temItens ? '▸' : ''}</td>` : '';
    const clickable = (priv && temItens) ? ` class="dd-click${cls ? ' today' : ''}" data-dd="${rid}"` : cls;
    const rotDia = String(row.dia).padStart(2,'0') + (multiMes ? '/' + String(it0.mes).padStart(2,'0') : '');
    html += `<tr${clickable}>${arrow}<td class="l">${rotDia}</td>${cols(row.counter, cfg.comValidada)}</tr>`;
    if (priv && temItens) {
      let sub = `<table class="dd-tbl"><tr><th>Hora</th><th>${cfg.label}</th><th>Time</th><th>ID</th><th>Negócio</th></tr>`;
      for (const it of itens) {
        sub += `<tr><td class="neg-hora">${it.hora || '--:--'}</td>
          <td>${it.closer}</td><td class="muted">${it.time}</td>
          <td><a href="${it.url}" target="_blank" rel="noopener">#${it.id}</a></td>
          <td><a href="${it.url}" target="_blank" rel="noopener">${it.title}</a></td></tr>`;
      }
      sub += `</table>`;
      const colspan = (cfg.comValidada ? 6 : 5) + 1; // arrow + Dia + colunas
      html += `<tr class="dd-detail" id="${rid}" style="display:none"><td colspan="${colspan}"><div class="dd-box">${sub}</div></td></tr>`;
    }
  }
  const totLead = priv ? '<td></td>' : '';
  html += `<tr class="total">${totLead}<td class="l">TOTAL</td>${cols(mt, cfg.comValidada)}</tr></table></div></details>`;

  if (data.nao_encontrados && data.nao_encontrados.length) {
    html += `<div class="warn">⚠ Sem correspondência no Pipedrive: ${data.nao_encontrados.join(', ')}</div>`;
  }

  $(cfg.rootId).innerHTML = html;
  ligaCriador();
  ligaDiaADia();
}

function render(data) {
  renderGenerico(data, {
    rootId: 'root', label: 'Closer', comCriador: true, idPrefix: 'cr',
    ehAtual: ehDefaultAtual, comValidada: false,
  });
}

function renderSdr(data) {
  renderGenerico(data, {
    rootId: 'root-sdr', label: 'SDR', comCriador: false, idPrefix: 'sr',
    ehAtual: null, comValidada: true,
  });
}

function ligaCriador() {
  document.querySelectorAll('.cl-toggle[data-cr]').forEach(el => {
    el.addEventListener('click', () => {
      const id = el.getAttribute('data-cr');
      const row = document.getElementById(id);
      if (!row) return;
      const aberto = row.style.display !== 'none';
      row.style.display = aberto ? 'none' : 'table-row';
      const rotulo = el.textContent.replace(/^./, '').trim();  // preserva o texto ("criador"/"detalhes")
      el.textContent = (aberto ? '▸' : '▾') + ' ' + rotulo;
    });
  });
}

function ligaDiaADia() {
  document.querySelectorAll('tr.dd-click[data-dd]').forEach(el => {
    el.addEventListener('click', () => {
      const row = document.getElementById(el.getAttribute('data-dd'));
      if (!row) return;
      const aberto = row.style.display !== 'none';
      row.style.display = aberto ? 'none' : 'table-row';
      const arw = el.querySelector('.dd-arrow');
      if (arw) arw.textContent = aberto ? '▸' : '▾';
    });
  });
}

// ---- login ----
function abreLogin() {
  $('loginErro').textContent = '';
  $('in-user').value = ''; $('in-pass').value = '';
  $('loginModal').classList.add('show');
  $('in-user').focus();
}
function fechaLogin() { $('loginModal').classList.remove('show'); }

async function fazLogin() {
  const usuario = $('in-user').value.trim();
  const senha = $('in-pass').value;
  $('loginErro').textContent = '';
  try {
    const res = await fetch('/api/login', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({usuario, senha}),
    });
    const d = await res.json();
    if (!res.ok) { $('loginErro').textContent = d.error || 'Falha no login'; return; }
    TOKEN = d.token; USUARIO = d.usuario;
    sessionStorage.setItem('dash_token', TOKEN);
    sessionStorage.setItem('dash_user', USUARIO);
    fechaLogin();
    atualizaAuthUI();
    buscar(false);  // recarrega ja com os negocios
  } catch (e) {
    $('loginErro').textContent = 'Erro de conexão';
  }
}

function logout() {
  TOKEN = null; USUARIO = null;
  sessionStorage.removeItem('dash_token');
  sessionStorage.removeItem('dash_user');
  atualizaAuthUI();
  buscar(false);
}

function atualizaAuthUI() {
  if (ehPriv()) {
    $('authWho').textContent = USUARIO ? ('● ' + USUARIO) : '● conectado';
    $('btnAuth').textContent = 'Sair';
    $('tab-auditoria').style.display = '';
    $('tab-taxas').style.display = '';
  } else {
    $('authWho').textContent = '';
    $('btnAuth').textContent = 'Entrar';
    $('tab-auditoria').style.display = 'none';
    $('tab-taxas').style.display = 'none';
    // se estava numa aba privilegiada e deslogou, volta pra reunioes
    if (ABA === 'auditoria' || ABA === 'taxas') trocaAba('reunioes');
  }
}

$('btnAuth').addEventListener('click', () => { ehPriv() ? logout() : abreLogin(); });
$('loginCancel').addEventListener('click', fechaLogin);
$('loginOk').addEventListener('click', fazLogin);
$('in-pass').addEventListener('keydown', e => { if (e.key === 'Enter') fazLogin(); });
$('loginModal').addEventListener('click', e => { if (e.target.id === 'loginModal') fechaLogin(); });

// ---- abas ----
let ABA = 'reunioes';
let AUD_CARREGADA_MES = null;
let MESES_DISPONIVEIS = [];
let DIST_CARREGADA_MES = null;

async function trocaAba(nome) {
  if ((nome === 'auditoria' || nome === 'distribuicao' || nome === 'taxas') && !ehPriv()) return;
  ABA = nome;
  $('tab-reunioes').classList.toggle('active', nome === 'reunioes');
  $('tab-sdrs').classList.toggle('active', nome === 'sdrs');
  $('tab-auditoria').classList.toggle('active', nome === 'auditoria');
  $('tab-distribuicao').classList.toggle('active', nome === 'distribuicao');
  $('tab-taxas').classList.toggle('active', nome === 'taxas');
  $('root').style.display = (nome === 'reunioes') ? '' : 'none';
  $('root-sdr').style.display = (nome === 'sdrs') ? '' : 'none';
  $('root-aud').style.display = (nome === 'auditoria') ? '' : 'none';
  $('root-dist').style.display = (nome === 'distribuicao') ? '' : 'none';
  $('root-taxas').style.display = (nome === 'taxas') ? '' : 'none';

  if (nome === 'sdrs' && MODO_PESSOA !== 'sdr') {
    MODO_PESSOA = 'sdr';
    await carregaPessoas();
    buscarSdr(false);
  } else if (nome === 'reunioes' && MODO_PESSOA !== 'closer') {
    MODO_PESSOA = 'closer';
    await carregaPessoas();
    buscar(false);
  } else if (nome === 'sdrs' && !LAST_DATA_SDR) {
    buscarSdr(false);
  }
  if (nome === 'auditoria') carregaAuditoria();
  if (nome === 'distribuicao') carregaDistribuicaoAba();
  if (nome === 'taxas') carregaTaxasAba();
}

$('tab-reunioes').addEventListener('click', () => trocaAba('reunioes'));
$('tab-sdrs').addEventListener('click', () => trocaAba('sdrs'));
$('tab-auditoria').addEventListener('click', () => trocaAba('auditoria'));
$('tab-distribuicao').addEventListener('click', () => trocaAba('distribuicao'));
$('tab-taxas').addEventListener('click', () => trocaAba('taxas'));

async function carregaAuditoria(forcar) {
  const mes = $('f-mes').value;
  if (!forcar && AUD_CARREGADA_MES === mes) return;  // ja carregada p/ esse mes
  $('root-aud').innerHTML = '<div class="muted">Buscando no Pipedrive… (pode levar alguns segundos)</div>';
  try {
    const res = await fetch('/api/auditoria_sdr?month=' + mes, { headers: authHeaders() });
    const data = await res.json();
    if (data.error) { $('root-aud').innerHTML = '<div class="warn">Erro: ' + data.error + '</div>'; return; }
    AUD_CARREGADA_MES = mes;
    renderAuditoria(data);
  } catch (e) {
    $('root-aud').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  }
}

const EV_SDRS = ['Bruna Goes', 'Vitor Soares'];
const EV_DESDE = '2026-08-17'; // segunda-feira combinada como inicio da analise
let EV_CHARTS = {}; // canvasId -> instancia do Chart

async function buscaEvolucaoHorario() {
  $('ev-resultado').innerHTML = '<div class="muted">Buscando no Pipedrive… (pode levar alguns segundos)</div>';
  try {
    const resultados = await Promise.all(EV_SDRS.map(sdr => {
      const p = new URLSearchParams({ sdr, desde: EV_DESDE });
      return fetch('/api/evolucao_sdr?' + p.toString(), { headers: authHeaders() }).then(r => r.json());
    }));
    renderEvolucaoComparativo(resultados);
  } catch (e) {
    $('ev-resultado').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  }
}

function renderEvolucaoComparativo(resultados) {
  const validos = resultados.filter(d => !d.erro && !d.error);
  const comErro = resultados.filter(d => d.erro || d.error);

  if (!validos.length) {
    $('ev-resultado').innerHTML = '<div class="warn">Nenhum dado encontrado.</div>';
    return;
  }

  let html = `<div class="muted" style="margin-bottom:10px">de ${validos[0].desde.split('-').reverse().join('/')} até ${validos[0].ate.split('-').reverse().join('/')} · todas as horas (00h–23h) · horário de Brasília</div>`;

  // ---- quadro comparativo no topo ----
  html += `<table class="aud-tbl" style="margin-bottom:20px">
    <tr><th class="l">SDR</th><th>Vol. Leads</th><th>Vol. Agendados</th><th>Taxa de Agendamento</th></tr>`;
  for (const d of validos) {
    const t = d.total || {leads:0, agendados:0};
    html += `<tr><td class="l">${d.sdr}</td><td class="qtd">${t.leads}</td>
      <td class="qtd">${t.agendados}</td><td class="qtd">${d.taxa_agendamento}%</td></tr>`;
  }
  html += `</table>`;
  for (const d of comErro) {
    html += `<div class="muted" style="font-size:11px;margin-bottom:10px">${d.sdr || 'SDR'}: ${d.erro || d.error}</div>`;
  }

  // ---- um grafico por SDR, empilhados ----
  for (let i = 0; i < validos.length; i++) {
    html += `<div class="nb-title" style="margin-top:18px">${validos[i].sdr}</div>
      <div style="max-width:1000px"><canvas id="ev-canvas-${i}" height="60"></canvas></div>`;
  }

  $('ev-resultado').innerHTML = html;

  if (window.ChartDataLabels && !Chart._boardAcademyDatalabelsRegistrado) {
    Chart.register(window.ChartDataLabels);
    Chart._boardAcademyDatalabelsRegistrado = true;
  }
  for (let i = 0; i < validos.length; i++) {
    desenhaGraficoEvolucao('ev-canvas-' + i, validos[i]);
  }
}

function desenhaGraficoEvolucao(canvasId, d) {
  const horas = (d.por_hora || []).map(h => String(h.hora).padStart(2,'0') + 'h');
  const leads = (d.por_hora || []).map(h => h.leads);
  const agendados = (d.por_hora || []).map(h => h.agendados);

  if (EV_CHARTS[canvasId]) { EV_CHARTS[canvasId].destroy(); }
  const ctx = document.getElementById(canvasId).getContext('2d');
  EV_CHARTS[canvasId] = new Chart(ctx, {
    data: {
      labels: horas,
      datasets: [
        { type: 'bar', label: 'Vol. Leads', data: leads, backgroundColor: '#FFD700',
          borderRadius: 3, yAxisID: 'y', order: 2, datalabels: { display: false } },
        { type: 'line', label: 'Vol. Agendados', data: agendados, borderColor: '#141414',
          backgroundColor: '#141414', tension: 0, borderDash: [6, 4], pointRadius: 4, pointHoverRadius: 5,
          pointBackgroundColor: '#141414', borderWidth: 2.5, yAxisID: 'y1', order: 1,
          datalabels: { align: 'top', anchor: 'end', color: '#141414', font: { weight: 'bold', size: 11 },
                        formatter: (v) => v > 0 ? v : '' } },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 2.4,
      devicePixelRatio: Math.max(window.devicePixelRatio || 1, 2),
      interaction: { mode: 'index', intersect: false },
      plugins: { legend: { position: 'top' } },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: 'Vol. Leads' },
             position: 'left' },
        y1: { beginAtZero: true, ticks: { precision: 0, stepSize: 1 },
              title: { display: true, text: 'Vol. Agendados' },
              position: 'right', grid: { drawOnChartArea: false } },
        x: { title: { display: true, text: 'Hora (00h–23h)' } },
      },
    },
  });
}

function carregaDistribuicaoAba() {
  if (!document.getElementById('dist-mes')) {
    let html = `<div class="filters" style="margin-bottom:14px">
      <div class="field"><label>Mês (log)</label><select id="dist-mes"></select></div>
    </div>
    <div id="dist-resultado"><div class="muted">Carregando…</div></div>`;
    $('root-dist').innerHTML = html;
    $('dist-mes').addEventListener('change', () => buscaDistribuicaoLeads(true));
  }
  // repovoa as opcoes sempre que ainda estiverem vazias -- evita ficar vazio
  // pra sempre se essa aba foi aberta antes de MESES_DISPONIVEIS carregar
  if (MESES_DISPONIVEIS.length && $('dist-mes').options.length === 0) {
    opt($('dist-mes'), MESES_DISPONIVEIS, x=>x.value, x=>x.label);
    $('dist-mes').value = CURRENT_MONTH;
  }
  buscaDistribuicaoLeads();
}

async function buscaDistribuicaoLeads(forcar) {
  const mes = $('dist-mes').value;
  if (!forcar && DIST_CARREGADA_MES === mes) return;  // ja carregada p/ esse mes
  $('dist-resultado').innerHTML = '<div class="muted">Buscando na planilha… (pode levar alguns segundos)</div>';
  try {
    const [resResumo, resLog] = await Promise.all([
      fetch('/api/distribuicao_resumo', { headers: authHeaders() }).then(r => r.json()),
      fetch('/api/distribuicao_log?month=' + mes, { headers: authHeaders() }).then(r => r.json()),
    ]);
    DIST_CARREGADA_MES = mes;
    renderDistribuicaoLeads(resResumo, resLog);
  } catch (e) {
    $('dist-resultado').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  }
}

function renderDistribuicaoLeads(resResumo, resLog) {
  if (resResumo.erro || resResumo.error) {
    $('dist-resultado').innerHTML = '<div class="warn">Erro: ' + (resResumo.erro || resResumo.error) + '</div>';
    return;
  }

  let html = '';

  // ---- resumo por colaborador ----
  html += `<div class="nb-title">Resumo por colaborador</div>
    <table class="aud-tbl"><tr><th class="l">Nome</th><th class="l">Cargo</th>
      <th>Meta de reuniões</th><th>Recebidas hoje</th><th class="barcell"></th>
      <th>Reuniões atuais hoje</th><th>Voltaram hoje</th></tr>`;
  const resumo = resResumo.resumo || [];
  for (const r of resumo) {
    const pct = r.qtd_reunioes ? Math.min(100, Math.round((r.recebidas_hoje / r.qtd_reunioes) * 100)) : 0;
    html += `<tr><td class="l">${r.nome}</td><td class="l muted">${r.cargo}</td>
      <td class="qtd">${r.qtd_reunioes}</td>
      <td class="qtd">${r.recebidas_hoje}</td>
      <td class="barcell"><div class="aud-bar" style="width:${pct}%"></div></td>
      <td class="qtd">${r.reunioes_atuais_hoje}</td>
      <td class="qtd">${r.voltaram_hoje || 0}</td></tr>`;
  }
  if (!resumo.length) {
    html += `<tr><td colspan="7" class="aud-empty">Sem dados no resumo.</td></tr>`;
  }
  const t = resResumo.total || {};
  if (resumo.length) {
    html += `<tr class="total"><td class="l">TOTAL</td><td></td>
      <td class="qtd">${t.qtd_reunioes || 0}</td>
      <td class="qtd">${t.recebidas_hoje || 0}</td>
      <td></td>
      <td class="qtd">${t.reunioes_atuais_hoje || 0}</td>
      <td class="qtd">${t.voltaram_hoje || 0}</td></tr>`;
  }
  html += `</table>`;

  // ---- log detalhado ----
  if (resLog.erro || resLog.error) {
    html += `<div class="warn" style="margin-top:14px">Erro no log: ${resLog.erro || resLog.error}</div>`;
  } else {
    const log = resLog.log || [];
    html += `<div class="nb-title" id="dist-log-toggle" style="margin-top:18px; cursor:pointer">
      <span class="aud-arrow" id="dist-log-arw">▸</span> Log de distribuição — ${resLog.total} registro(s) no mês (mais recentes primeiro)</div>
      <div id="dist-log-body" style="display:none">
      <table class="neg-tbl"><colgroup><col class="c-hora"><col class="c-id"><col><col><col><col><col></colgroup>
      <tr><th>Data/Hora</th><th>Deal</th><th>Colaborador</th><th>Funil</th><th>Status</th><th>Situação</th><th>Outro dia</th></tr>`;
    for (const l of log) {
      const situacao = l.alterado
        ? `<span class="status-badge st-reagendada">alterado → ${l.novo_proprietario || '—'}</span>`
        : `<span class="muted">—</span>`;
      const outroDia = l.agendada_outro_dia
        ? `<span class="status-badge st-reagendada">Sim</span>`
        : `<span class="muted">—</span>`;
      html += `<tr><td class="neg-hora">${l.data_hora}</td>
        <td><a href="${l.url}" target="_blank" rel="noopener">#${l.deal_id}</a></td>
        <td>${l.colaborador}</td>
        <td class="muted">${l.funil}</td>
        <td>${statusBadge(l.status_reuniao)}</td>
        <td>${situacao}</td>
        <td>${outroDia}</td></tr>`;
    }
    if (!log.length) {
      html += `<tr><td colspan="7" class="aud-empty">Sem registros no log.</td></tr>`;
    }
    html += `</table></div>`;
  }

  $('dist-resultado').innerHTML = html;

  const togg = document.getElementById('dist-log-toggle');
  if (togg) {
    togg.addEventListener('click', () => {
      const body = document.getElementById('dist-log-body');
      const arw = document.getElementById('dist-log-arw');
      const aberto = body.style.display !== 'none';
      body.style.display = aberto ? 'none' : '';
      arw.textContent = aberto ? '▸' : '▾';
    });
  }
}

// ---- Taxas % -- reune num so lugar as taxas ja calculadas em outras abas,
// mais a nova metrica principal (reunioes agendadas fora da escala) ----
let TAXAS_CARREGADA_MES = null;

function carregaTaxasAba() {
  if (!document.getElementById('taxas-resultado')) {
    $('root-taxas').innerHTML = '<div id="taxas-resultado"><div class="muted">Carregando…</div></div>';
  }
  buscaTaxasAba();
}

// fora da escala: se De..Ate atravessa meses, consulta cada mes (com o
// intervalo recortado nele, mantendo "leads do mes" de cada mes) e soma
async function buscaEscalaPeriodo(mes, de, ate) {
  const um = (m, d1, d2) => {
    let u = '/api/taxas_escala?month=' + m;
    if (d1 && d2) u += '&de=' + d1 + '&ate=' + d2;
    return fetch(u, { headers: authHeaders() }).then(r => r.json());
  };
  if (!de || !ate || de.slice(0, 7) === ate.slice(0, 7)) return um(mes, de, ate);
  const meses = mesesDoIntervalo(de, ate);
  const res = await Promise.all(meses.map((m, i) => {
    const [y, mm] = m.split('-').map(Number);
    const ultimo = m + '-' + String(new Date(y, mm, 0).getDate()).padStart(2, '0');
    return um(m, i === 0 ? de : m + '-01', i === meses.length - 1 ? ate : ultimo);
  }));
  const erro = res.find(r => r.error || r.erro);
  if (erro) return erro;
  const porNome = {};
  for (const r of res) {
    for (const s of (r.sdrs || [])) {
      const a = porNome[s.nome];
      if (!a) { porNome[s.nome] = JSON.parse(JSON.stringify(s)); continue; }
      if (s.erro) continue;
      a.total_mes = (a.total_mes || 0) + (s.total_mes || 0);
      a.fora_da_escala = (a.fora_da_escala || 0) + (s.fora_da_escala || 0);
      a.exemplos = (a.exemplos || []).concat(s.exemplos || []);
      a.entrada = a.entrada || s.entrada; a.saida = a.saida || s.saida;
    }
  }
  const sdrs = Object.values(porNome);
  let tm = 0, tf = 0;
  for (const s of sdrs) {
    if (s.erro) continue;
    s.pct_fora_escala = s.total_mes ? Math.round(s.fora_da_escala / s.total_mes * 1000) / 10 : 0;
    tm += s.total_mes || 0; tf += s.fora_da_escala || 0;
  }
  const f = v => v.slice(8, 10) + '/' + v.slice(5, 7) + '/' + v.slice(0, 4);
  return {
    sdrs, escala_configurada: res.every(r => r.escala_configurada),
    total: { total_mes: tm, fora_da_escala: tf, pct_fora_escala: tm ? Math.round(tf / tm * 1000) / 10 : 0 },
    month_label: f(de) + ' a ' + f(ate),
  };
}

async function buscaTaxasAba(forcar) {
  // usa o filtro do cabecalho (Mes / De / Ate), o mesmo que as outras abas
  const mes = $('f-mes').value;
  // "De"/"Até" (dia em que a reunião foi REALIZADA): só entra em vigor
  // quando os dois campos estão preenchidos e formam um intervalo de fato
  // (De <= Até); senão o backend segue usando o mês inteiro (mantendo a
  // condição de leads do mês, pela "Data da última aplicação")
  const de = $('f-de').value;
  const ate = $('f-ate').value;
  const usaRange = !!(de && ate && de <= ate);
  const chave = mes + '|' + (usaRange ? de + '|' + ate : '');
  if (!forcar && TAXAS_CARREGADA_MES === chave) return;
  $('taxas-resultado').innerHTML = '<div class="muted">Buscando no Pipedrive… (pode levar alguns segundos)</div>';
  try {
    const [resEscala, resDash, ...resEvolucoes] = await Promise.all([
      buscaEscalaPeriodo(mes, usaRange ? de : '', usaRange ? ate : ''),
      fetch('/api/dashboard?month=' + mes, { headers: authHeaders() }).then(r => r.json()),
      ...EV_SDRS.map(sdr => {
        const p = new URLSearchParams({ sdr, desde: EV_DESDE });
        return fetch('/api/evolucao_sdr?' + p.toString(), { headers: authHeaders() }).then(r => r.json());
      }),
    ]);
    TAXAS_CARREGADA_MES = chave;
    renderTaxasAba(resEscala, resDash, resEvolucoes);
  } catch (e) {
    $('taxas-resultado').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  }
}

function renderTaxasAba(resEscala, resDash, resEvolucoes) {
  let html = '';

  // ---- 1) reunioes agendadas fora da escala (metrica principal, nova) ----
  html += `<div class="nb-title">Reuniões agendadas fora da escala — ${resEscala.month_label || ''}</div>`;
  if (resEscala.error || resEscala.erro) {
    html += `<div class="warn">Erro: ${resEscala.error || resEscala.erro}</div>`;
  } else {
    if (!resEscala.escala_configurada) {
      html += `<div class="warn" style="margin-bottom:8px">A escala comercial ainda não está configurada (ESCALA_COMERCIAL_CSV_URL) — o total de reuniões do mês aparece, mas "fora da escala" fica zerado até isso ser configurado.</div>`;
    }
    html += `<div class="muted" style="margin-bottom:8px">Conta, por SDR, quantas reuniões AGENDADAS, REALIZADAS neste mês e VALIDADAS (de leads/reaplicações também deste mês, pela "Data da última aplicação") ela mesma agendou FORA do horário de trabalho dela na escala comercial (antes da entrada ou depois da saída). Preenchendo "De" e "Até" no cabeçalho, restringe pelo dia em que a reunião foi realizada (mantendo a condição de leads do mês selecionado).</div>`;
    html += `<table class="aud-tbl"><tr><th class="l">SDR</th><th class="l">Time</th><th class="l">Entrada</th><th class="l">Saída</th>
      <th>Validadas do mês</th><th>Fora da escala</th><th class="barcell"></th></tr>`;
    const sdrsEscala = (resEscala.sdrs || []).slice().sort((a,b) => (b.fora_da_escala||0) - (a.fora_da_escala||0));
    for (const s of sdrsEscala) {
      if (s.erro) {
        html += `<tr><td class="l">${s.nome}</td><td class="l muted">${s.time||''}</td>
          <td class="l muted" colspan="5">${s.erro}</td></tr>`;
        continue;
      }
      const exemplos = (s.exemplos || []).map(e =>
        `<a href="${e.url}" target="_blank" rel="noopener" title="${e.titulo} — ${e.data_hora_criacao}">#${e.deal_id}</a>`
      ).join(', ');
      html += `<tr><td class="l">${s.nome}</td><td class="l muted">${s.time||''}</td>
        <td class="l muted">${s.entrada || '—'}</td>
        <td class="l muted">${s.saida || '—'}</td>
        <td class="qtd">${s.total_mes}</td>
        <td class="qtd">${s.fora_da_escala}<div class="muted" style="font-size:11px">${s.pct_fora_escala}%</div></td>
        <td class="aud-negs">${exemplos}</td></tr>`;
    }
    if (!sdrsEscala.length) {
      html += `<tr><td colspan="7" class="aud-empty">Nenhum SDR encontrado no mês.</td></tr>`;
    }
    const t = resEscala.total || {};
    html += `<tr class="total"><td class="l">TOTAL</td><td></td><td></td><td></td>
      <td class="qtd">${t.total_mes||0}</td>
      <td class="qtd">${t.fora_da_escala||0}<div class="muted" style="font-size:11px">${t.pct_fora_escala||0}%</div></td>
      <td></td></tr>`;
    html += `</table>`;
  }

  // ---- 2) taxa de conversao por closer (mesma conta da aba Reuniões - Closers) ----
  html += `<div class="nb-title" style="margin-top:22px">Taxa de Conversão por Closer — ${resDash.month_label || ''}</div>`;
  if (resDash.error || resDash.erro) {
    html += `<div class="warn">Erro: ${resDash.error || resDash.erro}</div>`;
  } else {
    const porCloser = (resDash.por_closer || []).slice()
      .sort((a,b) => (b.ganhos_done||0) - (a.ganhos_done||0));
    html += `<table class="aud-tbl"><tr><th class="l">Closer</th><th class="l">Time</th>
      <th>Feitas</th><th>Ganhos</th><th>Taxa de conversão</th></tr>`;
    for (const c of porCloser) {
      const feitas = (c.total && c.total.done) || 0;
      const ganhos = c.ganhos_done || 0;
      const taxa = feitas ? (ganhos / feitas * 100) : 0;
      html += `<tr><td class="l">${c.name}</td><td class="l muted">${c.time||''}</td>
        <td class="qtd">${feitas}</td><td class="qtd">${ganhos}</td>
        <td class="qtd">${taxa.toFixed(1)}%</td></tr>`;
    }
    if (!porCloser.length) {
      html += `<tr><td colspan="5" class="aud-empty">Nenhum closer no mês.</td></tr>`;
    }
    html += `</table>`;
  }

  // ---- 3) taxa de agendamento (Evolução por Horário, mesmas SDRs da Auditoria) ----
  html += `<div class="nb-title" style="margin-top:22px">Taxa de Agendamento — Evolução por Horário</div>`;
  const validos = (resEvolucoes || []).filter(d => d && !d.erro && !d.error);
  if (validos.length) {
    html += `<table class="aud-tbl"><tr><th class="l">SDR</th><th>Vol. Leads</th><th>Vol. Agendados</th><th>Taxa de Agendamento</th></tr>`;
    for (const d of validos) {
      const t = d.total || {leads:0, agendados:0};
      html += `<tr><td class="l">${d.sdr}</td><td class="qtd">${t.leads}</td>
        <td class="qtd">${t.agendados}</td><td class="qtd">${d.taxa_agendamento}%</td></tr>`;
    }
    html += `</table>`;
  } else {
    html += `<div class="aud-empty">Sem dados de evolução por horário.</div>`;
  }

  $('taxas-resultado').innerHTML = html;
}

function auditoriaBloco(pessoa, idx, prefixo) {
  const aid = prefixo + '-' + idx;
  const maxq = pessoa.closers.length ? pessoa.closers[0].qtd : 1;
  let linhas = '';
  if (pessoa.closers.length) {
    linhas = `<table class="aud-tbl"><tr><th>Closer</th><th>Reuniões marcadas</th><th class="barcell"></th><th>Negócios</th></tr>`;
    for (const c of pessoa.closers) {
      const pct = Math.round((c.qtd / maxq) * 100);
      const negs = (c.negocios || []).map(n =>
        `<a href="${n.url}" target="_blank" rel="noopener" title="${n.title}">#${n.id}</a>`
      ).join(', ');
      linhas += `<tr><td>${c.closer}</td><td class="qtd">${c.qtd}</td>
        <td class="barcell"><div class="aud-bar" style="width:${pct}%"></div></td>
        <td class="aud-negs">${negs}</td></tr>`;
    }
    linhas += `</table>`;
  } else if (!pessoa.encontrado) {
    linhas = `<div class="aud-empty">Sem correspondência no Pipedrive (nome não bateu).</div>`;
  } else {
    linhas = `<div class="aud-empty">Nenhuma reunião marcada para closers nesse mês.</div>`;
  }
  return `<div class="aud-sdr">
    <div class="aud-head" data-aud="${aid}">
      <span class="aud-arrow" id="${aid}-arw">▸</span>
      <span class="aud-name">${pessoa.nome}</span>
      <span class="aud-team">${pessoa.label}</span>
      <span class="aud-total"><b>${pessoa.total}</b> reuniões</span>
    </div>
    <div class="aud-body" id="${aid}">${linhas}</div>
  </div>`;
}

function renderAuditoria(data) {
  let html = `<div class="kpi-head">Auditoria — pra quais closers cada pessoa marcou reuniões · ${data.month_label}</div>`;

  html += `<div class="aud-section-title">SDRs</div>`;
  if (data.sdrs && data.sdrs.length) {
    const sdrs = data.sdrs.slice().sort((a,b) => b.total - a.total);
    sdrs.forEach((s, i) => { html += auditoriaBloco(s, i, 'aud-sdr'); });
  } else {
    html += '<div class="aud-empty">Nenhum SDR encontrado no CSV para esse mês.</div>';
  }

  html += `<div class="aud-section-title">Liderança</div>`;
  if (data.liderancas && data.liderancas.length) {
    const lids = data.liderancas.slice().sort((a,b) => b.total - a.total);
    lids.forEach((s, i) => { html += auditoriaBloco(s, i, 'aud-lid'); });
  } else {
    html += '<div class="aud-empty">Nenhum Team Leader ou Head encontrado no CSV para esse mês.</div>';
  }

  html += `<div class="aud-section-title">Evolução por Horário — Comparativo (Bruna Goes x Vitor Soares)</div>
    <div class="panel">
      <div id="ev-resultado"><div class="muted">Carregando…</div></div>
    </div>`;

  $('root-aud').innerHTML = html;
  buscaEvolucaoHorario();
  document.querySelectorAll('.aud-head[data-aud]').forEach(el => {
    el.addEventListener('click', () => {
      const body = document.getElementById(el.getAttribute('data-aud'));
      const arw = document.getElementById(el.getAttribute('data-aud') + '-arw');
      const aberto = body.classList.contains('open');
      body.classList.toggle('open', !aberto);
      if (arw) arw.textContent = aberto ? '▸' : '▾';
    });
  });
}

// quando muda o mes, invalida a auditoria carregada
$('f-mes').addEventListener('change', () => { AUD_CARREGADA_MES = null; if (ABA === 'auditoria') carregaAuditoria(true); });

atualizaAuthUI();
init();
</script>
</body>
</html>
"""
