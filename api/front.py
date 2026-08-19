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
<title>REUNIÕES - CLOSERS</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js"></script>
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
  select#f-dia { min-width:110px; }
  select:focus { outline:none; border-color:var(--gold); box-shadow:0 0 0 3px rgba(255,215,0,.18); }
  button { background:var(--gold); color:#1a1a1a; border:none; border-radius:8px;
           padding:9px 22px; font-size:14px; font-weight:800; cursor:pointer; letter-spacing:.5px; }
  button:hover { background:#e6c200; }
  button:disabled { opacity:.5; cursor:wait; }
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
        <h1>REUNIÕES <span class="sep">-</span> CLOSERS</h1>
      </div>
      <div class="authbar">
        <span class="who" id="authWho"></span>
        <button class="btn-auth" id="btnAuth">Entrar</button>
      </div>
    </div>
    <div class="filters">
      <div class="field"><label>Mês</label><select id="f-mes"></select></div>
      <div class="field"><label>Dia</label><select id="f-dia"></select></div>
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
    </div>
    <div id="root"><div class="muted">Carregando filtros…</div></div>
    <div id="root-sdr" style="display:none"><div class="muted">Carregando filtros…</div></div>
    <div id="root-aud" style="display:none"><div class="muted">Carregando auditoria…</div></div>
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

function preencheDias() {
  const mes = $('f-mes').value;
  const n = diasNoMes(mes);
  const arr = [];
  for (let d = 1; d <= n; d++) arr.push(d);
  opt($('f-dia'), arr, x=>x, x=>String(x).padStart(2,'0'));
  $('f-dia').value = (mes === CURRENT_MONTH && diaHojeNum <= n) ? diaHojeNum : 1;
}

function diaSelecionado() { return parseInt($('f-dia').value, 10); }

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
  opt($('f-mes'), d.months, x=>x.value, x=>x.label);
  $('f-mes').value = d.current;
  opt($('f-time'), d.teams, x=>x, x=>x);
  preencheDias();
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
  preencheDias();
  await carregaPessoas();
});
// dia e so recorte visual: re-renderiza na hora, sem nova requisicao
$('f-dia').addEventListener('change', () => {
  if (MODO_PESSOA === 'sdr') { if (LAST_DATA_SDR) renderSdr(LAST_DATA_SDR); }
  else { if (LAST_DATA) render(LAST_DATA); }
});
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
    else { LAST_DATA = data; render(data); }
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
    else { LAST_DATA_SDR = data; renderSdr(data); }
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

function renderGenerico(data, cfg) {
  $('updated').innerText = 'Atualizado: ' + new Date(data.generated_at).toLocaleString('pt-BR');
  $('auto').innerText = (cfg.ehAtual && cfg.ehAtual()) ? '● atualiza sozinho a cada ' + Math.round(REFRESH_MS/60000) + ' min' : '';
  const mt = data.month_total;
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

  const diaCounter = getDia(data.days, dSel) || zero;

  let html = '';

  const kpiValidaHtml = cfg.comValidada
    ? `<div class="kpi valid"><div class="lbl">Validadas</div><div class="val">${diaCounter.validada||0}</div></div>` : '';
  html += `<div class="kpi-head">Dia ${dSelStr}/${mesStr}</div>`;
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
    <span class="ms-title">Total do mês — ${data.month_label}</span>
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
      const cm = data.por_time[t];
      html += `<div class="team-card">
        <div class="tc-name">${t}</div>
        <div class="tc-row">
          <span class="tc-lbl">Total dia ${dSelStr}</span>
          <span class="tc-big">${cd.planned}</span>
          <span class="tc-sub">plan · <span class="c-done">${cd.done}</span> feitas${cfg.comValidada ? ' · <span class=\"c-valid\">' + (cd.validada||0) + '</span> valid' : ''} · <span class="c-nsw">${cd.no_show}</span> NS · <span class="c-reag">${cd.reagendada}</span> reag</span>
        </div>
        <div class="tc-row">
          <span class="tc-lbl">Total mês</span>
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
    html += `<th colspan="${nColsPorBloco}" class="grp-tot mtot">Total do mês</th></tr>`;
    html += `<tr class="sub">`;
    for (const d of tresDias) html += subHead((d.n === dSel) ? ' today' : '');
    html += subHead(' mtot');
    html += `</tr></thead><tbody>`;

    const nCols = 2 + tresDias.length * nColsPorBloco + nColsPorBloco;
    data.por_closer.forEach((c, i) => {
      const cid = cfg.idPrefix + '-' + i;
      const nomeCel = cfg.comCriador
        ? `<span class="cl-wrap"><span class="cl-toggle" data-cr="${cid}" id="${cid}-t">▸ criador</span>${c.name}</span>`
        : `<span class="cl-wrap"><span class="cl-toggle" data-cr="${cid}" id="${cid}-t">▸ detalhes</span>${c.name}</span>`;
      html += `<tr><td class="closer l">${nomeCel}</td><td class="team l">${c.time}</td>`;
      for (const d of tresDias) html += quatro(getDia(c.days, d.n) || zero);
      const t = c.total;
      html += `<td class="c-plan mtot">${t.planned}</td><td class="c-done">${t.done}</td><td class="c-nsw">${t.no_show}</td><td class="c-reag">${t.reagendada}</td></tr>`;

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

    // ---- distribuicao: Validadas (se disponivel) ou Feitas + % sobre o total de todos ----
    // + quantidade/% do que cada um marcou PRA SI MESMO (creator == owner), mesma metrica
    const metricaDist = cfg.comValidada ? 'validada' : 'done';
    const campoProprio = cfg.comValidada ? 'proprio_validada' : 'proprio_done';
    const tituloDist = cfg.comValidada ? 'reuniões validadas' : 'reuniões feitas';
    const totalTodos = data.por_closer.reduce((soma, c) => soma + (c.total[metricaDist]||0), 0);
    const totalProprioTodos = data.por_closer.reduce((soma, c) => soma + (c[campoProprio]||0), 0);
    const distOrdenada = data.por_closer.slice().sort((a,b) => (b.total[metricaDist]||0) - (a.total[metricaDist]||0));
    html += `<div class="panel"><h2>Distribuição por ${cfg.label} — ${tituloDist} · ${data.month_label}</h2>
      <table class="aud-tbl"><tr><th class="l">${cfg.label}</th><th>Quantidade</th><th>%</th><th class="barcell"></th><th>Quantidade (próprio)</th><th>% (próprio)</th></tr>`;
    for (const c of distOrdenada) {
      const qtd = c.total[metricaDist] || 0;
      const pct = totalTodos ? (qtd / totalTodos * 100) : 0;
      const qtdProprio = c[campoProprio] || 0;
      const pctProprio = totalTodos ? (qtdProprio / totalTodos * 100) : 0;
      html += `<tr><td class="l">${c.name}</td><td class="qtd">${qtd}</td>
        <td>${pct.toFixed(1)}%</td>
        <td class="barcell"><div class="aud-bar" style="width:${pct}%"></div></td>
        <td class="qtd">${qtdProprio}</td>
        <td>${pctProprio.toFixed(1)}%</td></tr>`;
    }
    html += `<tr class="total"><td class="l">TOTAL</td><td class="qtd">${totalTodos}</td><td>100%</td><td></td>
      <td class="qtd">${totalProprioTodos}</td><td>${totalTodos ? (totalProprioTodos/totalTodos*100).toFixed(1) : '0.0'}%</td></tr>`;
    html += `</table></div>`;
  }

  const priv = ehPriv();
  const gdMap = {};
  if (priv) for (const g of (data.geral_dia || [])) gdMap[g.dia] = g.itens || [];
  html += `<details class="diaria"><summary>Dia a dia — todos os times (${data.month_label})${priv ? ' · clique num dia para ver as reuniões' : ''}</summary><div class="inner">
    <table><tr>${priv ? '<th style="width:24px"></th>' : ''}<th class="l">Dia</th><th>Planejado</th><th>Feitas</th>${cfg.comValidada ? '<th>Validadas</th>' : ''}<th>No Show</th><th>Reagendadas</th></tr>`;

  for (const row of data.days) {
    const cls = (row.dia === dSel) ? ' class="today"' : '';
    const itens = priv ? (gdMap[row.dia] || []) : [];
    const temItens = itens.length > 0;
    const arrow = priv ? `<td class="dd-arrow">${temItens ? '▸' : ''}</td>` : '';
    const clickable = (priv && temItens) ? ` class="dd-click${cls ? ' today' : ''}" data-dd="ddrow-${row.dia}"` : cls;
    html += `<tr${clickable}>${arrow}<td class="l">${String(row.dia).padStart(2,'0')}</td>${cols(row.counter, cfg.comValidada)}</tr>`;
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
      html += `<tr class="dd-detail" id="ddrow-${row.dia}" style="display:none"><td colspan="${colspan}"><div class="dd-box">${sub}</div></td></tr>`;
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
  } else {
    $('authWho').textContent = '';
    $('btnAuth').textContent = 'Entrar';
    $('tab-auditoria').style.display = 'none';
    // se estava na aba auditoria e deslogou, volta pra reunioes
    if (ABA === 'auditoria') trocaAba('reunioes');
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

async function trocaAba(nome) {
  if (nome === 'auditoria' && !ehPriv()) return;
  ABA = nome;
  $('tab-reunioes').classList.toggle('active', nome === 'reunioes');
  $('tab-sdrs').classList.toggle('active', nome === 'sdrs');
  $('tab-auditoria').classList.toggle('active', nome === 'auditoria');
  $('root').style.display = (nome === 'reunioes') ? '' : 'none';
  $('root-sdr').style.display = (nome === 'sdrs') ? '' : 'none';
  $('root-aud').style.display = (nome === 'auditoria') ? '' : 'none';

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
}

$('tab-reunioes').addEventListener('click', () => trocaAba('reunioes'));
$('tab-sdrs').addEventListener('click', () => trocaAba('sdrs'));
$('tab-auditoria').addEventListener('click', () => trocaAba('auditoria'));

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

async function buscaEvolucaoHorario() {
  const sdr = 'Bruna Goes';
  const desde = '2026-08-17'; // segunda-feira combinada como inicio da analise
  $('ev-resultado').innerHTML = '<div class="muted">Buscando no Pipedrive… (pode levar alguns segundos)</div>';
  try {
    const p = new URLSearchParams({ sdr, desde });
    const res = await fetch('/api/evolucao_sdr?' + p.toString(), { headers: authHeaders() });
    const d = await res.json();
    if (d.erro || d.error) {
      $('ev-resultado').innerHTML = '<div class="warn">Erro: ' + (d.erro || d.error) + '</div>';
      return;
    }
    renderEvolucaoHorario(d);
  } catch (e) {
    $('ev-resultado').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  }
}

let EV_CHART = null;

function renderEvolucaoHorario(d) {
  const t = d.total || {leads:0, agendados:0};
  let html = `<div class="muted" style="margin-bottom:10px">${d.sdr} — de ${d.desde.split('-').reverse().join('/')} até ${d.ate.split('-').reverse().join('/')} · todas as horas (00h–23h) · horário de Brasília</div>`;
  html += `<div class="creator-box" style="margin-bottom:14px">
    <div class="ci-item"><span class="ci-lbl">Vol. Leads</span><span class="ci-val">${t.leads}</span></div>
    <div class="ci-item"><span class="ci-lbl">Vol. Agendados</span><span class="ci-val">${t.agendados}</span></div>
    <div class="ci-item"><span class="ci-lbl">Taxa de Agendamento</span><span class="ci-val">${d.taxa_agendamento}%</span></div>
  </div>`;
  html += `<div style="max-width:900px"><canvas id="ev-canvas" height="90"></canvas></div>`;

  $('ev-resultado').innerHTML = html;

  const horas = (d.por_hora || []).map(h => String(h.hora).padStart(2,'0') + 'h');
  const leads = (d.por_hora || []).map(h => h.leads);
  const agendados = (d.por_hora || []).map(h => h.agendados);

  if (EV_CHART) { EV_CHART.destroy(); }
  const ctx = document.getElementById('ev-canvas').getContext('2d');
  EV_CHART = new Chart(ctx, {
    data: {
      labels: horas,
      datasets: [
        { type: 'bar', label: 'Vol. Leads', data: leads, backgroundColor: '#FFD700', order: 2 },
        { type: 'line', label: 'Vol. Agendados', data: agendados, borderColor: '#0a5f36',
          backgroundColor: '#0a5f36', tension: 0.35, pointRadius: 3, order: 1 },
      ],
    },
    options: {
      responsive: true,
      plugins: { legend: { position: 'top' } },
      scales: {
        y: { beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: 'Vol.' } },
        x: { title: { display: true, text: 'Hora (00h–23h)' } },
      },
    },
  });
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

  html += `<div class="aud-section-title">Evolução por Horário — Bruna Goes</div>
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
