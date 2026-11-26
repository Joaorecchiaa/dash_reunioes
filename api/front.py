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
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
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
  .carimbo { font-size:10.5px; opacity:.8; max-width:640px; margin-top:2px; line-height:1.3; }
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
  .kpi.nsw .val{color:var(--text);} .kpi.nvalid .val{color:var(--text);} .kpi.reag .val{color:var(--text);}

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

  .grf-bar { display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:6px 0; font-size:12px; }
  .grf-bar .lbl { font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); font-weight:700; min-width:90px; }
  .grf-chip { display:inline-flex; align-items:center; gap:5px; padding:3px 9px; border:1px solid var(--border); border-radius:999px; background:#fff; cursor:pointer; user-select:none; font-size:12px; }
  .grf-chip.on { background:#fff8d6; border-color:#e0c200; font-weight:600; }
  .grf-chip input { display:none; }
  .grf-chip .dot { width:9px; height:9px; border-radius:50%; display:inline-block; }
  .grf-pessoas { max-height:96px; overflow:auto; padding:2px; }
  .grf-btn { font-size:11px; padding:2px 8px; border:1px solid var(--border); border-radius:6px; background:#fff; cursor:pointer; }
  .grf-leg { display:flex; flex-wrap:wrap; gap:4px 14px; font-size:11px; color:var(--muted); margin-top:6px; }
  .grf-leg i { display:inline-block; width:11px; height:11px; margin-right:5px; vertical-align:middle; border-radius:2px; }
  .grf-leg { font-size:12px; }
  .panel { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:20px;
           box-shadow:none; }
  .panel h2 { font-size:14px; margin:0 0 12px; color:var(--gold-ink); text-transform:uppercase; letter-spacing:.5px; font-weight:700; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th, td { padding:7px 10px; text-align:center; border-bottom:1px solid var(--border); }
  th { color:var(--muted); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:.5px; }
  td.l, th.l { text-align:left; }
  tr.total td { font-weight:800; border-top:2px solid var(--gold); background:var(--gold-soft); color:var(--text); }
  tr.today td { background:var(--gold-soft); }
  .sec-lider td{background:#f6efd0; color:#6b5400; font-weight:800; font-size:11px; letter-spacing:.06em; text-transform:uppercase; padding:6px 10px; border-top:2px solid #FFD700;}
  .cargo-lider{font-size:10px; font-weight:700; color:#8a6d00; background:#fff3b0; border-radius:8px; padding:1px 7px; margin-left:6px;}
  .c-plan{color:var(--text); font-weight:800;} .c-done{color:var(--done);} .c-valid{color:#0a5f36; font-weight:700;} .c-nvalid{color:#a1262d; font-weight:700;} .c-nsw{color:var(--nsw);} .c-reag{color:var(--reag);}
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
  .modal-bg.obrig { background:#0b0b0b; }
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
  .flt-bar { font-size:11px; color:var(--muted); margin:2px 0 6px; text-align:left; }
  .flt-bar .flt-status { margin-left:4px; }
  .flt-status { font-size:11px; padding:2px 6px; border:1px solid var(--border); border-radius:6px; background:#fff; color:var(--text); text-transform:none; letter-spacing:0; font-weight:400; }
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
  table.neg-tbl col.c-status { width:150px; }
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
  /* Auditoria SDR: matriz SDR x Closer */
  table.val-tab tr.mk:hover td{background:rgba(255,200,0,.12)}
  table.val-tab td.n{text-align:right} table.val-tab td:first-child{text-align:left;font-weight:600}
  .mx-wrap { overflow-x:auto; border:1px solid var(--border); border-radius:12px; background:var(--card); -webkit-overflow-scrolling:touch; }
  table.mx { border-collapse:separate; border-spacing:0; font-size:13px; width:100%; }
  table.mx th, table.mx td { padding:8px 5px; text-align:center; border-bottom:1px solid var(--border); }
  table.mx td { white-space:nowrap; }
  table.mx th { white-space:normal; word-break:break-word; line-height:1.25; }
  table.mx th.l, table.mx td.l { width:190px; min-width:150px; white-space:normal; padding-left:10px; }
  table.mx th { font-size:11px; color:var(--text); font-weight:700; background:#f7f8fa; cursor:pointer; vertical-align:bottom; }
  table.mx th:hover { background:#eceff3; }
  table.mx th.l, table.mx td.l { text-align:left; position:sticky; left:0; z-index:1; background:var(--card); }
  table.mx th.l { background:#f7f8fa; z-index:2; }
  table.mx td.l { cursor:pointer; font-weight:600; }
  table.mx td.l:hover { background:#f2f4f7; }
  table.mx td.c { cursor:pointer; font-weight:700; }
  table.mx td.c:hover { outline:2px solid #8a6d00; outline-offset:-2px; }
  table.mx td.sel, table.mx td.l.sel, table.mx th.sel { outline:2px solid var(--text); outline-offset:-2px; }
  table.mx td.z { color:#c4c8cf; font-weight:400; cursor:default; }
  table.mx td.t, table.mx th.t { font-weight:800; cursor:pointer; background:#fafbfc; }
  table.mx tr.tot td { font-weight:800; background:#fff8d6; border-top:2px solid var(--border); }
  table.mx th .th-sub { display:block; font-weight:400; font-size:10px; text-transform:none; color:var(--muted); }
  .mx-lista { margin-top:14px; }
  .mx-det { border:1px solid var(--border); border-radius:12px; background:var(--card); padding:10px 14px; }
  .mx-det summary { cursor:pointer; font-size:14px; }
  .mx-det .cab { margin:10px 0 8px; }
  .mx-lista .cab { display:flex; flex-wrap:wrap; align-items:center; gap:10px; margin-bottom:8px; }
  .mx-lista .cab b { font-size:14px; }
  .mx-lista .rol { max-height:520px; overflow:auto; border:1px solid var(--border); border-radius:10px; background:var(--card); }
  .mx-lista table { width:100%; border-collapse:collapse; font-size:13px; }
  .mx-lista th { position:sticky; top:0; background:#f7f8fa; font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); text-align:left; padding:6px 10px; border-bottom:1px solid var(--border); }
  .mx-lista td { padding:7px 10px; border-bottom:1px solid var(--border); }
  .mx-lista td a { color:var(--text); font-weight:700; text-decoration:none; }
  .mx-lista td a:hover { text-decoration:underline; color:var(--gold-ink); }
  @media (max-width:700px) { table.mx th.l, table.mx td.l { width:120px; min-width:100px; } table.mx { font-size:12px; } table.mx th, table.mx td { padding:6px 7px; } .mx-lista td.hide-m, .mx-lista th.hide-m { display:none; } }


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
      <h3 id="loginTitulo">Acesso ao dashboard</h3>
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
      <div class="updated"><div id="updated"></div><div class="auto" id="auto"></div><div class="carimbo" id="carimbo"></div></div>
    </div>
  </header>

  <div class="page">
    <div class="tabs" id="tabs">
      <button class="tab active" id="tab-reunioes" data-tab="reunioes">Reuniões - Closers</button>
      <button class="tab" id="tab-sdrs" data-tab="sdrs">Reuniões - SDRs</button>
      <button class="tab" id="tab-auditoria" data-tab="auditoria">Auditoria</button>
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
let PAPEL = sessionStorage.getItem('dash_papel') || null;

// toda chamada a /api/ leva o token; se o servidor responder "login obrigatorio" (token vencido, usuario
// desativado), limpa a sessao e volta pra tela de login
const _fetchOrig = window.fetch.bind(window);
window.fetch = (u, o) => {
  const url = String(u);
  const api = url.startsWith('/api/') && !url.startsWith('/api/login');
  if (api && TOKEN) o = Object.assign({}, o, { headers: Object.assign({}, (o && o.headers) || {}, { 'Authorization': 'Bearer ' + TOKEN }) });
  return _fetchOrig(u, o).then(r => { if (api && r.status === 401 && TOKEN) exigeLogin(true); return r; });
};

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
  // login obrigatorio: sem token valido so aparece a tela de login
  if (!TOKEN) { exigeLogin(false); return; }
  try {
    const me = await (await fetch('/api/me', { headers: authHeaders() })).json();
    if (!me.privilegiado) { exigeLogin(true); return; }
    USUARIO = me.usuario; PAPEL = me.papel; sessionStorage.setItem('dash_papel', PAPEL || '');
  } catch (e) {}
  atualizaAuthUI();
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
  if (ABA === 'taxas') { buscaTaxasAba(true); return; }   // aba Taxas % tem busca propria (De/Até)
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

// ---- filtro por status (negocios do dia / do mes / dia a dia) ----
let filtroStatus = '';
const STATUS_OPCOES = ['Planejada','Feita','Validada','Feita/Não validada','No Show','Reagendada','Vencida'];
function filtroStatusHtml() {
  const ops = ['<option value="">Todos os status</option>'].concat(
    STATUS_OPCOES.map(s => `<option value="${s}"${s === filtroStatus ? ' selected' : ''}>${s}</option>`));
  return `<select class="flt-status" onchange="setFiltroStatus(this.value)" onclick="event.stopPropagation()">${ops.join('')}</select>`;
}
function setFiltroStatus(v) {
  filtroStatus = v || '';
  document.querySelectorAll('.flt-status').forEach(s => { s.value = filtroStatus; });
  aplicaFiltroStatus();
}
function aplicaFiltroStatus() {
  document.querySelectorAll('tr[data-st]').forEach(tr => {
    tr.style.display = (!filtroStatus || tr.dataset.st === filtroStatus) ? '' : 'none';
  });
}

const porNome = (a, b) => String(a.title || '').localeCompare(String(b.title || ''), 'pt-BR', { sensitivity: 'base' });

function statusBadge(status) {
  const mapa = {
    'Planejada': 'st-planejada', 'Feita': 'st-feita', 'Validada': 'st-validada', 'Feita/Não validada': 'st-vencida',
    'No Show': 'st-noshow', 'Reagendada': 'st-reagendada', 'Vencida': 'st-vencida',
  };
  const cls = mapa[status] || 'st-planejada';
  return `<span class="status-badge ${cls}">${status || '—'}</span>`;
}

function cols(c, comValidada) {
  const meio = comValidada ? `<td class="c-valid">${c.validada||0}</td>` : '';
  return `<td class="c-plan">${c.planned}</td><td class="c-done">${c.done}</td>${meio}<td class="c-nvalid">${c.nao_validada||0}</td>`
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
  const soma = {planned:0, done:0, validada:0, nao_validada:0, no_show:0, reagendada:0};
  for (const seg of periodo.segs) {
    for (const item of (getter(seg.d) || [])) {
      if (item.dia < seg.de || item.dia > seg.ate) continue;
      const c = item.counter || {};
      soma.planned += c.planned||0; soma.done += c.done||0; soma.validada += c.validada||0; soma.nao_validada += c.nao_validada||0;
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

// negocios da pessoa DENTRO do periodo (De/Ate), 1 por negocio, com o status da
// reuniao mais recente do periodo -- vem de negocios_dia (so os dias do intervalo)
function negociosPeriodo(periodo, nome) {
  const m = new Map();
  for (const seg of periodo.segs) {
    const x = (seg.d.por_closer || []).find(y => y.name === nome);
    const dias = ((x && x.negocios_dia) || []).slice().sort((a, b) => a.dia - b.dia);
    for (const di of dias) {
      if (di.dia < seg.de || di.dia > seg.ate) continue;
      for (const it of (di.itens || [])) m.set(it.id, it);   // cronologico: o ultimo vence
    }
  }
  return Array.from(m.values()).sort((a, b) => a.id - b.id);
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
  if (!periodo) return base.filter(c => !c.lideranca).concat(base.filter(c => c.lideranca));
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
  const todas = base.concat(extra);
  return todas.filter(c => !c.lideranca).concat(todas.filter(c => c.lideranca));  // lideranca por ultimo
}

// ---- grafico dia a dia (volume por colaborador x status) ----
const GRF_STATUS = [
  ['planned','Planejadas','#64748b'], ['done','Feitas','#0ea5e9'], ['validada','Validadas','#15803d'],
  ['nao_validada','Não validadas','#b91c1c'], ['no_show','No Show','#db2777'], ['reagendada','Reagendadas','#d97706'],
];
const GRF_DASH = ['', '6 3', '2 3', '8 3 2 3', '1 4', '10 4'];
const GRF_CTX = {}, GRF_EST = {};
const grfCor = (i, n) => `hsl(${Math.round((i * 360 / Math.max(n, 1)) % 360)},60%,42%)`;

function grfPrepara(prefix, cfg, data, periodo) {
  const nomes = linhasPorPessoa(data, periodo).map(c => c.name);
  const fontes = periodo ? periodo.segs : [{ d: data, de: 1, ate: 31 }];
  const dias = [];
  for (const seg of fontes) {
    const mp = new Map((seg.d.por_closer || []).map(x => [x.name, new Map((x.days || []).map(d => [d.dia, d.counter]))]));
    const multi = periodo && periodo.segs.length > 1;
    for (const row of seg.d.days) {
      if (row.dia < seg.de || row.dia > seg.ate) continue;
      const por = {};
      for (const n of nomes) por[n] = (mp.get(n) || new Map()).get(row.dia) || {};
      dias.push({ rot: String(row.dia).padStart(2, '0') + (multi ? '/' + String(seg.d.month).padStart(2, '0') : ''), por });
    }
  }
  GRF_CTX[prefix] = { nomes, dias, label: cfg.label, comValidada: cfg.comValidada };
  if (!GRF_EST[prefix]) GRF_EST[prefix] = { pessoas: null, status: new Set([cfg.comValidada ? 'validada' : 'done']), soma: false };
}

function grfHtmlBase(prefix) {
  const c = GRF_CTX[prefix];
  return `<div class="panel" id="grf-${prefix}"><h2>Gráfico dia a dia — por ${c.label}</h2>
    <div class="grf-bar"><span class="lbl">Status</span><span id="grf-${prefix}-st"></span></div>
    <div class="grf-bar"><span class="lbl">${c.label}</span>
      <button class="grf-btn" data-grf="${prefix}" data-acao="todos">Todos</button>
      <button class="grf-btn" data-grf="${prefix}" data-acao="nenhum">Nenhum</button>
      <label class="grf-chip" id="grf-${prefix}-somalbl"><input type="checkbox" id="grf-${prefix}-soma">Somar selecionados</label></div>
    <div class="grf-bar grf-pessoas" id="grf-${prefix}-ps"></div>
    <div id="grf-${prefix}-svg"></div><div class="grf-leg" id="grf-${prefix}-leg"></div></div>`;
}

function grfMonta(prefix) {
  const c = GRF_CTX[prefix], e = GRF_EST[prefix];
  const box = document.getElementById('grf-' + prefix);
  if (!c || !box) return;
  const sts = GRF_STATUS.filter(s => s[0] !== 'validada' || c.comValidada).map(s => s);
  [...e.status].forEach(k => { if (!sts.some(s => s[0] === k)) e.status.delete(k); });
  const sel = new Set(e.pessoas ? c.nomes.filter(n => e.pessoas.has(n)) : c.nomes);
  document.getElementById('grf-' + prefix + '-st').innerHTML = sts.map(s =>
    `<label class="grf-chip${e.status.has(s[0]) ? ' on' : ''}"><input type="checkbox" data-grf="${prefix}" data-st="${s[0]}" ${e.status.has(s[0]) ? 'checked' : ''}><span class="dot" style="background:${s[2]}"></span>${s[1]}</label>`).join(' ');
  document.getElementById('grf-' + prefix + '-ps').innerHTML = c.nomes.map((n, i) =>
    `<label class="grf-chip${sel.has(n) ? ' on' : ''}"><input type="checkbox" data-grf="${prefix}" data-p="${i}" ${sel.has(n) ? 'checked' : ''}><span class="dot" style="background:${grfCor(i, c.nomes.length)}"></span>${n}</label>`).join(' ');
  const cb = document.getElementById('grf-' + prefix + '-soma');
  cb.checked = e.soma;
  document.getElementById('grf-' + prefix + '-somalbl').className = 'grf-chip' + (e.soma ? ' on' : '');

  // modelo: grupos de colunas dentro de cada dia. Cor = status quando há mais de um status;
  // com um status só, cor = pessoa.
  const stAtivos = sts.filter(s => e.status.has(s[0]));
  const pessoas = c.nomes.map((n, i) => ({ n, i })).filter(x => sel.has(x.n));
  const curto = n => { const p = n.split(' '); const dup = pessoas.filter(x => x.n.split(' ')[0] === p[0]).length > 1; return dup && p[1] ? p[0] + ' ' + p[1][0] + '.' : p[0]; };
  let grupos = [], legenda = '', dica = '';
  if (e.soma) {
    grupos = [{ rot: '', bars: stAtivos.map(s => ({ nome: s[1], cor: s[2], vals: c.dias.map(d => pessoas.reduce((t, p) => t + ((d.por[p.n] || {})[s[0]] || 0), 0)) })) }];
    legenda = stAtivos.map(s => `<span><i style="background:${s[2]}"></i>${s[1]}</span>`).join('');
    dica = `Soma dos ${c.label.toLowerCase()}s selecionados · cada cor é um status`;
  } else if (stAtivos.length > 1) {
    grupos = pessoas.map(p => ({ rot: curto(p.n), bars: stAtivos.map(s => ({ nome: p.n + ' · ' + s[1], cor: s[2], vals: c.dias.map(d => (d.por[p.n] || {})[s[0]] || 0) })) }));
    legenda = stAtivos.map(s => `<span><i style="background:${s[2]}"></i>${s[1]}</span>`).join('');
    dica = pessoas.length > 1 ? `Cada cor é um status · cada grupo de colunas é um ${c.label.toLowerCase()} (nome embaixo)` : `Cada cor é um status`;
  } else if (stAtivos.length === 1) {
    grupos = [{ rot: '', bars: pessoas.map(p => ({ nome: p.n, cor: grfCor(p.i, c.nomes.length), vals: c.dias.map(d => (d.por[p.n] || {})[stAtivos[0][0]] || 0) })) }];
    legenda = grupos[0].bars.map(b => `<span><i style="background:${b.cor}"></i>${b.nome}</span>`).join('');
    dica = `Status: ${stAtivos[0][1]} · cada cor é um ${c.label.toLowerCase()}`;
  }
  const alvo = document.getElementById('grf-' + prefix + '-svg');
  if (!grupos.length || !grupos[0].bars.length) { alvo.innerHTML = `<div class="muted" style="font-size:12px;padding:20px 0">Selecione ao menos um status e um ${c.label.toLowerCase()}.</div>`; document.getElementById('grf-' + prefix + '-leg').innerHTML = ''; return; }
  const G = grupos.length, S = grupos[0].bars.length;
  const W = 1000, L = 38, R = 12, T = 18;
  const n = c.dias.length;
  const slot = (W - L - R) / Math.max(n, 1);
  const gapDia = Math.min(14, slot * 0.2), gapGrupo = G > 1 ? Math.min(6, slot * 0.06) : 0;
  const bw = Math.max(2, Math.min(26, (slot - gapDia - gapGrupo * (G - 1)) / (G * S)));
  const larguraGrupo = bw * S;
  const rotular = G > 1;
  const girar = rotular && (larguraGrupo + gapGrupo) < 46;
  const B = rotular ? (girar ? 78 : 44) : 28, H = 280 + B - 28;
  const max0 = Math.max(1, ...grupos.flatMap(g => g.bars.flatMap(b => b.vals)));
  const passo = max0 <= 5 ? 1 : max0 <= 10 ? 2 : max0 <= 25 ? 5 : max0 <= 50 ? 10 : 20;
  const max = Math.ceil(max0 / passo) * passo;
  const y = v => T + (H - T - B) * (1 - v / max);
  let g = '';
  for (let v = 0; v <= max; v += passo) g += `<line x1="${L}" x2="${W - R}" y1="${y(v)}" y2="${y(v)}" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="2 4"/><text x="${L - 6}" y="${y(v) + 4}" font-size="11" fill="#6b7280" text-anchor="end">${v}</text>`;
  for (let i = 1; i < n; i++) g += `<line x1="${L + i * slot}" x2="${L + i * slot}" y1="${T}" y2="${H - B}" stroke="#e2e8f0" stroke-width="1" stroke-dasharray="2 5"/>`;
  const cada = Math.ceil(n / 31);
  const totalW = G * larguraGrupo + (G - 1) * gapGrupo;
  const yDia = H - B + (rotular ? (girar ? 72 : 36) : 20);
  c.dias.forEach((d, i) => { if (i % cada === 0) g += `<text x="${L + i * slot + slot / 2}" y="${H - 6}" font-size="11" font-weight="600" fill="#374151" text-anchor="middle">${d.rot}</text>`; });
  const comNum = bw >= 9;
  grupos.forEach((gr, gi) => {
    c.dias.forEach((d, i) => {
      const gx = L + i * slot + (slot - totalW) / 2 + gi * (larguraGrupo + gapGrupo);
      if (rotular && i % cada === 0) {
        const cx = gx + larguraGrupo / 2, ty = H - B + 12;
        g += girar
          ? `<text x="${cx.toFixed(1)}" y="${ty}" font-size="9" fill="#6b7280" text-anchor="end" transform="rotate(-60 ${cx.toFixed(1)} ${ty})">${gr.rot}</text>`
          : `<text x="${cx.toFixed(1)}" y="${ty}" font-size="9" fill="#6b7280" text-anchor="middle">${gr.rot}</text>`;
      }
      gr.bars.forEach((bar, j) => {
        const v = bar.vals[i], bx = gx + j * bw, h = (H - T - B) * (v / max);
        g += `<rect x="${bx.toFixed(1)}" y="${y(v).toFixed(1)}" width="${(bw - 1).toFixed(1)}" height="${Math.max(h, v > 0 ? 1 : 0).toFixed(1)}" rx="2" fill="${bar.cor}" fill-opacity="0.92"><title>${bar.nome} — dia ${d.rot}: ${v}</title></rect>`;
        if (comNum && v > 0) g += `<text x="${(bx + (bw - 1) / 2).toFixed(1)}" y="${(y(v) - 3).toFixed(1)}" font-size="10" font-weight="600" fill="#374151" text-anchor="middle">${v}</text>`;
      });
    });
  });
  alvo.innerHTML = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;max-height:420px">${g}</svg>`;
  document.getElementById('grf-' + prefix + '-leg').innerHTML =
    `<div style="width:100%;font-size:12px;color:#374151;margin-bottom:2px"><b>Como ler:</b> ${dica}. Passe o mouse numa coluna para ver o valor.</div>` + (legenda.length > 0 && grupos[0].bars.length <= 40 ? legenda : '');
}

document.addEventListener('change', ev => {
  const t = ev.target, prefix = t.dataset && t.dataset.grf;
  if (!prefix || !GRF_EST[prefix]) return;
  const e = GRF_EST[prefix], c = GRF_CTX[prefix];
  if (t.dataset.st) { t.checked ? e.status.add(t.dataset.st) : e.status.delete(t.dataset.st); }
  else if (t.dataset.p !== undefined) {
    if (!e.pessoas) e.pessoas = new Set(c.nomes);
    const nome = c.nomes[+t.dataset.p];
    t.checked ? e.pessoas.add(nome) : e.pessoas.delete(nome);
  }
  grfMonta(prefix);
});
document.addEventListener('change', ev => {
  const m = ev.target.id && ev.target.id.match(/^grf-(.+)-soma$/);
  if (m && GRF_EST[m[1]]) { GRF_EST[m[1]].soma = ev.target.checked; grfMonta(m[1]); }
});
document.addEventListener('click', ev => {
  const b = ev.target.closest && ev.target.closest('button.grf-btn');
  if (!b) return;
  const prefix = b.dataset.grf, e = GRF_EST[prefix], c = GRF_CTX[prefix];
  if (!e) return;
  e.pessoas = b.dataset.acao === 'todos' ? null : new Set();
  grfMonta(prefix);
});

function renderGenerico(data, cfg) {
  $('updated').innerText = 'Atualizado: ' + new Date(data.generated_at).toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  $('carimbo').innerText = (data.carimbo || '').replace(/\s*·\s*Atualizado:.*$/, '');
  $('auto').innerText = (cfg.ehAtual && cfg.ehAtual()) ? '● atualiza sozinho a cada ' + Math.round(REFRESH_MS/60000) + ' min' : '';
  const lblPlan = 'Planejadas';
  const lblPlanAbrev = 'plan';
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
    return `<td class="c-plan${mtotCls?' mtot':''}">${c.planned}</td><td class="c-done">${c.done}</td>${meio}<td class="c-nvalid">${c.nao_validada||0}</td>`
         + `<td class="c-nsw">${c.no_show}</td><td class="c-reag">${c.reagendada}</td>`;
  };
  const subHead = extra => {
    const meio = cfg.comValidada ? `<th class="c-valid">V</th>` : '';
    return `<th class="c-plan${extra||''}">P</th><th class="c-done">F</th>${meio}<th class="c-nvalid">NV</th><th class="c-nsw">NS</th><th class="c-reag">R</th>`;
  };
  const nColsPorBloco = cfg.comValidada ? 6 : 5;

  // com periodo ativo, os blocos do topo mostram a soma do periodo (nao so o dia de "De")
  const diaCounter = periodo ? mt : (getDia(data.days, dSel) || zero);
  const rotuloMes = periodo ? periodo.rotulo : data.month_label;

  let html = '';

  const kpiValidaHtml = cfg.comValidada
    ? `<div class="kpi valid"><div class="lbl">Validadas</div><div class="val">${diaCounter.validada||0}</div></div>` : '';
  html += `<div class="kpi-head">${periodo ? 'Período ' + periodo.rotulo : 'Dia ' + dSelStr + '/' + mesStr}</div>`;
  html += `<div class="kpis">
    <div class="kpi plan"><div class="lbl">${lblPlan}</div><div class="val">${diaCounter.planned}</div></div>
    <div class="kpi done"><div class="lbl">Feitas</div><div class="val">${diaCounter.done}</div></div>
    ${kpiValidaHtml}
    <div class="kpi nvalid"><div class="lbl">Não validadas</div><div class="val">${diaCounter.nao_validada||0}</div></div>
    <div class="kpi nsw"><div class="lbl">No Show</div><div class="val">${diaCounter.no_show}</div></div>
    <div class="kpi reag"><div class="lbl">Reagendadas</div><div class="val">${diaCounter.reagendada}</div></div>
  </div>`;

  const msValidaHtml = cfg.comValidada
    ? `<span class="ms-item c-valid">Validadas <b>${mt.validada||0}</b></span>` : '';
  html += `<div class="month-strip">
    <span class="ms-title">${rotuloTotal}</span>
    <span class="ms-item c-plan">${lblPlan} <b>${mt.planned}</b></span>
    <span class="ms-item c-done">Feitas <b>${mt.done}</b></span>
    ${msValidaHtml}
    <span class="ms-item c-nvalid">Não validadas <b>${mt.nao_validada||0}</b></span>
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
          <span class="tc-sub">${lblPlanAbrev} · <span class="c-done">${cd.done}</span> feitas${cfg.comValidada ? ' · <span class=\"c-valid\">' + (cd.validada||0) + '</span> valid' : ''} · <span class="c-nvalid">${cd.nao_validada||0}</span> não valid · <span class="c-nsw">${cd.no_show}</span> NS · <span class="c-reag">${cd.reagendada}</span> reag</span>
        </div>
        <div class="tc-row">
          <span class="tc-lbl">${periodo ? 'Total período' : 'Total mês'}</span>
          <span class="tc-big">${cm.planned}</span>
          <span class="tc-sub">${lblPlanAbrev} · <span class="c-done">${cm.done}</span> feitas${cfg.comValidada ? ' · <span class=\"c-valid\">' + (cm.validada||0) + '</span> valid' : ''} · <span class="c-nvalid">${cm.nao_validada||0}</span> não valid · <span class="c-nsw">${cm.no_show}</span> NS · <span class="c-reag">${cm.reagendada}</span> reag</span>
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
    let jaSecaoLider = false;
    linhasPorPessoa(data, periodo).forEach((c, i) => {
      if (c.lideranca && !jaSecaoLider) {
        jaSecaoLider = true;
        html += `<tr class="sec-lider"><td colspan="${nCols}">Liderança</td></tr>`;
      }
      const cid = cfg.idPrefix + '-' + i;
      const nomeCel = cfg.comCriador
        ? `<span class="cl-wrap"><span class="cl-toggle" data-cr="${cid}" id="${cid}-t">▸ criador</span>${c.name}</span>`
        : `<span class="cl-wrap"><span class="cl-toggle" data-cr="${cid}" id="${cid}-t">▸ detalhes</span>${c.name}${c.lideranca ? ' <span class="cargo-lider">' + c.lideranca + '</span>' : ''}</span>`;
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
        negHtml += `<div class="neg-box"><div class="nb-title">Negócios do dia ${dSelStr}/${mesStr} (${nd.length}) — clique para abrir no Pipedrive</div>
          <div class="flt-bar">Filtrar por status: ${filtroStatusHtml()}</div>`;
        if (nd.length) {
          negHtml += `<table class="neg-tbl"><colgroup><col class="c-hora"><col class="c-id"><col><col class="c-status"><col class="c-status"></colgroup><tr><th>Hora</th><th>ID</th><th>Negócio</th><th>Status</th><th>Situação</th></tr>`;
          for (const n of nd.slice().sort(porNome)) {
            negHtml += `<tr data-st="${n.status}"><td class="neg-hora">${n.hora || '--:--'}</td>
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
        const nm = periodo ? negociosPeriodo(periodo, c.name) : (c.negocios || []);
        negHtml += `<div class="neg-box"><div class="nb-title">Negócios ${periodo ? 'do período ' + periodo.rotulo : 'do mês'} (${nm.length})</div>
          <div class="flt-bar">Filtrar por status: ${filtroStatusHtml()}</div>`;
        if (nm.length) {
          negHtml += `<table class="neg-tbl"><colgroup><col class="c-hora"><col class="c-id"><col><col class="c-status"><col class="c-status"></colgroup><tr><th></th><th>ID</th><th>Negócio</th><th>Status</th><th>Situação</th></tr>`;
          for (const n of nm.slice().sort(porNome)) {
            negHtml += `<tr data-st="${n.status}"><td class="neg-hora"></td><td><a href="${n.url}" target="_blank" rel="noopener">#${n.id}</a></td>
              <td><a href="${n.url}" target="_blank" rel="noopener">${n.title}</a></td>
              <td>${statusBadge(n.status)}</td>
              <td>${dealBadge(n.status_negocio)}</td></tr>`;
          }
          negHtml += `</table>`;
        } else {
          negHtml += `<div class="muted" style="font-size:12px">Nenhum negócio ${periodo ? 'no período' : 'no mês'}.</div>`;
        }
        negHtml += `</div>`;
      }
      html += `<tr class="creator-row" id="${cid}" style="display:none"><td colspan="${nCols}">
        <div class="creator-wrap">${blocos}</div>${negHtml}</td></tr>`;
    });

    html += `<tr class="foot"><td class="closer l">TOTAL</td><td class="team l"></td>`;
    for (const d of tresDias) html += quatro(getDia(data.days, d.n) || zero);
    html += quatro(mt, true) + `</tr>`;
    const legendaValid = (cfg.comValidada ? ' · V = validadas' : '') + ' · NV = não validadas (campo "Reunião Validada?" = Não)';
    html += `</tbody></table></div>
      <div class="muted" style="font-size:11px;margin-top:8px">P = ${lblPlan.toLowerCase()} · F = feitas${legendaValid} · NS = no-show · R = reagendadas</div></div>`;

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
    <table><tr>${priv ? '<th style="width:24px"></th>' : ''}<th class="l">Dia</th><th>Planejadas</th><th>Feitas</th>${cfg.comValidada ? '<th>Validadas</th>' : ''}<th>Não validadas</th><th>No Show</th><th>Reagendadas</th></tr>`;

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
      let sub = `<table class="dd-tbl"><tr><th>Hora</th><th>${cfg.label}</th><th>Time</th><th>ID</th><th>Negócio</th><th>Status ${filtroStatusHtml()}</th></tr>`;
      for (const it of itens.slice().sort(porNome)) {
        sub += `<tr data-st="${it.status}"><td class="neg-hora">${it.hora || '--:--'}</td>
          <td>${it.closer}</td><td class="muted">${it.time}</td>
          <td><a href="${it.url}" target="_blank" rel="noopener">#${it.id}</a></td>
          <td><a href="${it.url}" target="_blank" rel="noopener">${it.title}</a></td>
          <td>${statusBadge(it.status)}</td></tr>`;
      }
      sub += `</table>`;
      const colspan = (cfg.comValidada ? 7 : 6) + 1; // arrow + Dia + colunas
      html += `<tr class="dd-detail" id="${rid}" style="display:none"><td colspan="${colspan}"><div class="dd-box">${sub}</div></td></tr>`;
    }
  }
  const totLead = priv ? '<td></td>' : '';
  html += `<tr class="total">${totLead}<td class="l">TOTAL</td>${cols(mt, cfg.comValidada)}</tr></table></div></details>`;
  grfPrepara(cfg.idPrefix, cfg, data, periodo);
  html += grfHtmlBase(cfg.idPrefix);

  if (data.nao_encontrados && data.nao_encontrados.length) {
    html += `<div class="warn">⚠ Sem correspondência no Pipedrive: ${data.nao_encontrados.join(', ')}</div>`;
  }

  $(cfg.rootId).innerHTML = html;
  ligaCriador();
  ligaDiaADia();
  grfMonta(cfg.idPrefix);
  aplicaFiltroStatus();
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
  const box = document.createElement('div');
  box.id = 'blk-ligacoes';
  $('root-sdr').appendChild(box);
  carregaLigacoesSdr(data, box);
}

// Bloco "Ligações dos SDRs": ligação normal (call) x Ligação/MicroSIP (call + assunto padrão), no mesmo recorte dos blocos de cima
async function carregaLigacoesSdr(data, box) {
  box.innerHTML = '<div class="muted" style="margin-top:14px">Buscando ligações…</div>';
  try {
    const p = new URLSearchParams({ month: $('f-mes').value, team: $('f-time').value, sdr: $('f-closer').value });
    const res = await fetch('/api/ligacoes_sdr?' + p.toString(), { headers: authHeaders() });
    const d = await res.json();
    if (d.error) { box.innerHTML = '<div class="warn" style="margin-top:14px">Ligações: ' + d.error + '</div>'; return; }
    const nDias = new Date(d.year, d.month, 0).getDate();
    const deVal = $('f-de').value, ateVal = $('f-ate').value;
    const mesStr = d.year + '-' + String(d.month).padStart(2, '0');
    let ini, fim, rot, comPeriodo = false;
    if (deVal && ateVal && deVal <= ateVal && deVal.slice(0, 7) === mesStr && ateVal.slice(0, 7) === mesStr) {
      comPeriodo = true;
      ini = parseInt(deVal.slice(8, 10), 10); fim = parseInt(ateVal.slice(8, 10), 10);
      rot = 'Período ' + deVal.slice(8, 10) + '/' + deVal.slice(5, 7) + ' a ' + ateVal.slice(8, 10) + '/' + ateVal.slice(5, 7);
    } else {
      ini = fim = Math.min(diaSelecionado() || 1, nDias);
      rot = 'Dia ' + String(ini).padStart(2, '0') + '/' + String(d.month).padStart(2, '0');
    }
    const soma = (dias, a, b) => { let n = 0, m = 0; for (let k = a; k <= b; k++) { const x = dias[k]; if (x) { n += x.n; m += x.m; } } return [n, m]; };
    const linhas = Object.keys(d.pessoas).sort().map(nome => {
      const dias = d.pessoas[nome].days;
      const [n, m] = soma(dias, ini, fim), [nm, mm] = soma(dias, 1, nDias);
      return { nome, time: d.pessoas[nome].time, n, m, nm, mm };
    });
    const tot = linhas.reduce((t, l) => ({ n: t.n + l.n, m: t.m + l.m, nm: t.nm + l.nm, mm: t.mm + l.mm }), { n: 0, m: 0, nm: 0, mm: 0 });
    // destaques do topo: cards do dia/período e faixa do total (período ou mês)
    const kp = $('root-sdr').querySelector('.kpis');
    if (kp) kp.insertAdjacentHTML('beforeend',
      `<div class="kpi"><div class="lbl">Ligações</div><div class="val">${tot.n}</div></div>
       <div class="kpi"><div class="lbl">Ligação/MicroSIP</div><div class="val">${tot.m}</div></div>`);
    const ms = $('root-sdr').querySelector('.month-strip');
    if (ms) ms.insertAdjacentHTML('beforeend',
      `<span class="ms-item">Ligações <b>${comPeriodo ? tot.n : tot.nm}</b></span>
       <span class="ms-item">Ligação/MicroSIP <b>${comPeriodo ? tot.m : tot.mm}</b></span>`);
    box.innerHTML = `<div class="neg-box" style="margin-top:14px"><div class="nb-title">Ligações dos SDRs — ${rot}</div>
      <div class="muted" style="margin-bottom:8px">Ligação = atividade call feita (AT1) registrada pelo SDR · Ligação/MicroSIP = call feita com o assunto padrão "Ligação efetuada via Voip do Brasil" (AT3).</div>
      <table><tr><th class="l">SDR</th><th class="l">Time</th><th>Ligação</th><th>Ligação/MicroSIP</th><th>Total</th></tr>
      ${linhas.map(l => `<tr><td class="l">${l.nome}</td><td class="l">${l.time}</td><td>${l.n}</td><td>${l.m}</td><td><b>${l.n + l.m}</b></td></tr>`).join('')}
      <tr><td class="l"><b>Total</b></td><td></td><td><b>${tot.n}</b></td><td><b>${tot.m}</b></td><td><b>${tot.n + tot.m}</b></td></tr></table></div>`;
  } catch (e) {
    box.innerHTML = '<div class="warn" style="margin-top:14px">Falha ao buscar ligações: ' + e + '</div>';
  }
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

// ---- login (obrigatorio) ----
function limpaSessao() {
  TOKEN = null; USUARIO = null; PAPEL = null;
  ['dash_token', 'dash_user', 'dash_papel'].forEach(k => sessionStorage.removeItem(k));
}
function exigeLogin(expirou) {
  limpaSessao();
  $('loginErro').textContent = expirou ? 'Sessão encerrada. Entre novamente.' : '';
  $('in-user').value = ''; $('in-pass').value = '';
  $('loginCancel').style.display = 'none';
  $('loginModal').classList.add('show', 'obrig');
  $('in-user').focus();
}
function abreLogin() { exigeLogin(false); }

async function fazLogin() {
  const usuario = $('in-user').value.trim();
  const senha = $('in-pass').value;
  $('loginErro').textContent = '';
  try {
    const res = await _fetchOrig('/api/login', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({usuario, senha}),
    });
    const d = await res.json();
    if (!res.ok) { $('loginErro').textContent = d.error || 'Falha no login'; return; }
    sessionStorage.setItem('dash_token', d.token);
    sessionStorage.setItem('dash_user', d.usuario);
    sessionStorage.setItem('dash_papel', d.papel || '');
    location.reload();   // recarrega ja logado, com o time certo do papel
  } catch (e) {
    $('loginErro').textContent = 'Erro de conexão';
  }
}

function logout() {
  limpaSessao();
  location.reload();
}

function atualizaAuthUI() {
  const rot = {admin: 'admin', sniper: 'Sniper', olympus: 'Olympus'}[PAPEL] || '';
  $('authWho').textContent = TOKEN ? ('● ' + (USUARIO || 'conectado') + (rot ? ' · ' + rot : '')) : '';
  $('btnAuth').textContent = 'Sair';
  $('tab-auditoria').style.display = TOKEN ? '' : 'none';
  $('tab-taxas').style.display = TOKEN ? '' : 'none';
  // Distribuicao e so do admin (o servidor tambem bloqueia)
  $('tab-distribuicao').style.display = (TOKEN && PAPEL === 'admin') ? '' : 'none';
}

$('btnAuth').addEventListener('click', () => { TOKEN ? logout() : abreLogin(); });
$('loginOk').addEventListener('click', fazLogin);
$('in-pass').addEventListener('keydown', e => { if (e.key === 'Enter') fazLogin(); });

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

  // ---- regras da fila (resumo, recolhido) ----
  html += `<div class="nb-title" id="dist-regras-toggle" style="cursor:pointer"><span class="aud-arrow" id="dist-regras-arw">▸</span> Regras da fila</div>
    <div id="dist-regras-body" style="display:none" class="muted">
      <ul style="margin:6px 0 14px 18px;line-height:1.55">
        <li>A fila escolhe o closer com menos <b>reuniões atuais hoje</b> abaixo da meta. Quando todos estão na meta, o negócio vai por sorteio.</li>
        <li><b>Meta 0</b>: a pessoa recebe crédito de negócios reatribuídos, mas nunca entra na fila. O cargo precisa conter "Closer" para ser reconhecida.</li>
        <li><b>Recebidas hoje</b> é só histórico (nunca diminui no dia, zera na virada). Quem vale para a fila e para o teto da meta é <b>Reuniões atuais hoje</b>, que sobe e desce com devoluções e trocas de dono.</li>
        <li><b>Vezes na fila</b>: peso na fila (vazio vale 1; com 2, passa duas vezes por ciclo).</li>
        <li>Ninguém pode ter duas reuniões em horários que se sobrepõem (duração padrão 60 min). A escala é checada no horário da <b>reunião</b>, não no da distribuição (entrada e saída inclusive).</li>
        <li>Negócio redistribuído não volta a quem já o teve hoje. <b>Alterado = Sim</b>: o negócio saiu do closer e a linha deixa de contar crédito; o crédito fica com o novo proprietário.</li>
      </ul></div>`;

  // ---- resumo por colaborador ----
  const STATUS_FILA = {
    na_fila: ['st-feita', 'Na fila'],
    na_meta: ['st-planejada', 'Na meta'],
    sem_meta: ['st-reagendada', 'Meta 0 · só crédito'],
    cargo_invalido: ['st-vencida', 'Cargo sem "Closer"'],
  };
  html += `<div class="nb-title" style="margin-top:6px">Resumo por colaborador</div>
    <table class="aud-tbl"><tr><th class="l">Nome</th><th class="l">Cargo</th><th class="l">Fila</th>
      <th>Meta diária</th><th>Reuniões atuais hoje</th><th class="barcell"></th><th>Falta p/ meta</th>
      <th>Recebidas hoje <span class="muted">(histórico)</span></th><th>Vezes na fila</th><th>Alterados hoje</th><th class="l">Para quem foi</th></tr>`;
  const resumo = resResumo.resumo || [];
  for (const r of resumo) {
    const pct = r.qtd_reunioes ? Math.min(100, Math.round((r.reunioes_atuais_hoje / r.qtd_reunioes) * 100)) : 0;
    const [cls, rot] = STATUS_FILA[r.status_fila] || ['st-planejada', '—'];
    html += `<tr><td class="l">${r.nome}</td><td class="l muted">${r.cargo}</td>
      <td class="l"><span class="status-badge ${cls}">${rot}</span></td>
      <td class="qtd">${r.qtd_reunioes}</td>
      <td class="qtd">${r.reunioes_atuais_hoje}</td>
      <td class="barcell"><div class="aud-bar" style="width:${pct}%"></div></td>
      <td class="qtd">${r.qtd_reunioes > 0 ? r.falta_para_meta : '—'}</td>
      <td class="qtd muted">${r.recebidas_hoje}</td>
      <td class="qtd">${r.vezes_na_fila}</td>
      <td class="qtd">${r.alterados_hoje || 0}</td>
      <td class="l">${(r.alterados_para || []).map(x => x.nome + (x.qtd > 1 ? ' (' + x.qtd + ')' : '')).join(', ') || '<span class="muted">—</span>'}</td></tr>`;
  }
  if (!resumo.length) {
    html += `<tr><td colspan="12" class="aud-empty">Sem dados no resumo.</td></tr>`;
  }
  const t = resResumo.total || {};
  if (resumo.length) {
    html += `<tr class="total"><td class="l">TOTAL</td><td></td>
      <td class="l">${t.na_fila || 0} na fila</td>
      <td class="qtd">${t.qtd_reunioes || 0}</td>
      <td class="qtd">${t.reunioes_atuais_hoje || 0}</td>
      <td></td><td></td>
      <td class="qtd">${t.recebidas_hoje || 0}</td>
      <td></td>
      <td class="qtd">${t.alterados_hoje || 0}</td><td></td></tr>`;
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
      <table class="neg-tbl"><colgroup><col style="width:140px"><col style="width:70px"><col><col><col><col style="width:50px"><col><col><col><col><col></colgroup>
      <tr><th>Data/Hora</th><th>Deal</th><th>Colaborador</th><th>Funil</th><th>Reunião</th><th>Do dia</th><th>Status</th><th>Alterado</th><th>Para quem foi</th><th>Outro dia / creditada</th><th>Alertas</th></tr>`;
    for (const l of log) {
      const situacao = l.alterado
        ? `<span class="status-badge st-reagendada">Sim</span>`
        : `<span class="muted">Não</span>`;
      const paraQuem = l.alterado
        ? `<b>${l.novo_proprietario || '—'}</b>`
        : `<span class="muted">—</span>`;
      const outroDia = l.agendada_outro_dia
        ? `<span class="status-badge st-reagendada">${l.outro_dia_valor && l.outro_dia_valor.toLowerCase() !== 'sim' ? l.outro_dia_valor : 'Sim'}</span>`
          + (l.creditada_em ? `<div class="muted" style="font-size:10px">creditada em ${l.creditada_em}</div>` : '')
        : (l.creditada_em ? `<span class="muted" style="font-size:10px">creditada em ${l.creditada_em}</span>` : `<span class="muted">—</span>`);
      const reuniao = l.reuniao_data
        ? `${l.reuniao_data.slice(0, 5)}${l.reuniao_hora ? ' ' + l.reuniao_hora : ''}<div class="muted" style="font-size:10px">${l.duracao_min || 60} min</div>`
        : `<span class="muted">—</span>`;
      const alertas = [];
      if (l.choque) alertas.push(`<span class="status-badge st-vencida" title="Outra reunião do mesmo closer se sobrepõe a esta">Choque de horário</span>`);
      if (l.fora_escala === true) alertas.push(`<span class="status-badge st-reagendada" title="Horário da reunião fora do turno do closer na escala comercial">Fora da escala</span>`);
      html += `<tr><td class="neg-hora">${l.data_hora}</td>
        <td><a href="${l.url}" target="_blank" rel="noopener">#${l.deal_id}</a></td>
        <td>${l.colaborador}</td>
        <td class="muted">${l.funil}</td>
        <td>${reuniao}</td>
        <td class="qtd">${l.reunioes_do_dia == null ? '—' : l.reunioes_do_dia}</td>
        <td>${statusBadge(l.status_reuniao)}</td>
        <td>${situacao}</td>
        <td>${paraQuem}</td>
        <td>${outroDia}</td>
        <td>${alertas.join(' ') || '<span class="muted">—</span>'}</td></tr>`;
    }
    if (!log.length) {
      html += `<tr><td colspan="11" class="aud-empty">Sem registros no log.</td></tr>`;
    }
    html += `</table></div>`;
  }

  $('dist-resultado').innerHTML = html;

  const toggR = document.getElementById('dist-regras-toggle');
  if (toggR) {
    toggR.addEventListener('click', () => {
      const body = document.getElementById('dist-regras-body');
      const arw = document.getElementById('dist-regras-arw');
      const aberto = body.style.display !== 'none';
      body.style.display = aberto ? 'none' : '';
      arw.textContent = aberto ? '▸' : '▾';
    });
  }
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
// dias liberados (ex.: sabados trabalhados): reunioes criadas nesses dias contam como dentro da escala, qualquer horario.
// Ficam salvos neste navegador; nao e preciso mexer no codigo.
const LIB_KEY = 'taxas_dias_liberados';
function lerLiberados() { try { return JSON.parse(localStorage.getItem(LIB_KEY) || '[]').filter(x => /^\d{4}-\d{2}-\d{2}$/.test(x)); } catch (e) { return []; } }
let TAXAS_LIBERADOS = lerLiberados();
function salvaLiberados() { try { localStorage.setItem(LIB_KEY, JSON.stringify(TAXAS_LIBERADOS)); } catch (e) {} }
function taxasAddLiberado() {
  const v = ($('lib-novo') || {}).value;
  if (!v || TAXAS_LIBERADOS.includes(v)) return;
  TAXAS_LIBERADOS = TAXAS_LIBERADOS.concat([v]).sort(); salvaLiberados(); buscaTaxasAba(true);
}
function taxasRemLiberado(v) { TAXAS_LIBERADOS = TAXAS_LIBERADOS.filter(x => x !== v); salvaLiberados(); buscaTaxasAba(true); }
const fmtDia = v => { const d = new Date(v + 'T12:00:00'); return v.slice(8, 10) + '/' + v.slice(5, 7) + ' ' + ['dom','seg','ter','qua','qui','sex','sáb'][d.getDay()]; };

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
    if (TAXAS_LIBERADOS.length) u += '&liberados=' + TAXAS_LIBERADOS.join(',');
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
      a.avaliadas = (a.avaliadas || 0) + (s.avaliadas || 0);
      a.dias_liberados = (a.dias_liberados || 0) + (s.dias_liberados || 0);
      a.escala_semana = a.escala_semana || s.escala_semana;
      a.fora_da_escala = (a.fora_da_escala || 0) + (s.fora_da_escala || 0);
      a.motivos = a.motivos || {}; a.detalhe = a.detalhe || {};
      for (const k in (s.motivos || {})) { a.motivos[k] = (a.motivos[k] || 0) + s.motivos[k]; a.detalhe[k] = (a.detalhe[k] || []).concat((s.detalhe || {})[k] || []); }
      a.exemplos = (a.exemplos || []).concat(s.exemplos || []);
      a.entrada = a.entrada || s.entrada; a.saida = a.saida || s.saida;
    }
  }
  const sdrs = Object.values(porNome);
  let tm = 0, tf = 0, ta = 0;
  for (const s of sdrs) {
    if (s.erro) continue;
    s.pct_fora_escala = s.avaliadas ? Math.round(s.fora_da_escala / s.avaliadas * 1000) / 10 : 0;
    tm += s.total_mes || 0; tf += s.fora_da_escala || 0; ta += s.avaliadas || 0;
  }
  const f = v => v.slice(8, 10) + '/' + v.slice(5, 7) + '/' + v.slice(0, 4);
  return {
    sdrs, escala_configurada: res.every(r => r.escala_configurada), erro_escala: (res.find(r => r.erro_escala) || {}).erro_escala || null,
    diagnostico: (() => { const d = { etapas: {}, funis_sem_escala: {}, subareas_da_escala: [] };
      for (const r of res) { const x = r.diagnostico || {};
        for (const k in (x.funis_sem_escala || {})) d.funis_sem_escala[k] = (d.funis_sem_escala[k] || 0) + x.funis_sem_escala[k];
        d.subareas_da_escala = x.subareas_da_escala || d.subareas_da_escala; }
      return d; })(),
    total: { total_mes: tm, avaliadas: ta, fora_da_escala: tf, pct_fora_escala: ta ? Math.round(tf / ta * 1000) / 10 : 0 },
    month_label: f(de) + ' a ' + f(ate),
  };
}

let TAXAS_PEDIDO = 0;
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
  const chave = mes + '|' + (usaRange ? de + '|' + ate : '') + '|' + TAXAS_LIBERADOS.join(',');
  if (!forcar && TAXAS_CARREGADA_MES === chave) return;
  $('taxas-resultado').innerHTML = '<div class="muted">Buscando no Pipedrive… (pode levar alguns segundos)</div>';
  try {
    const mesesNS = [mes];   // no-show: sempre o MES todo do filtro Mes (De/Ate nao se aplica)
    const pEscala = buscaEscalaPeriodo(mes, usaRange ? de : '', usaRange ? ate : '');
    const pResto = Promise.all([
      fetch('/api/dashboard?month=' + mes, { headers: authHeaders() }).then(r => r.json()),
      Promise.all(mesesNS.map(m => fetch('/api/dashboard_sdr?month=' + m, { headers: authHeaders() })
        .then(r => r.json()).then(d => ({ mes: m, d })).catch(e => ({ mes: m, d: { error: String(e) } })))),
      ...EV_SDRS.map(sdr => {
        const p = new URLSearchParams({ sdr, desde: EV_DESDE });
        return fetch('/api/evolucao_sdr?' + p.toString(), { headers: authHeaders() }).then(r => r.json());
      }),
    ]);
    const meuPedido = ++TAXAS_PEDIDO;
    // fase 1: mostra a tabela de fora da escala assim que ela chega, sem esperar o resto
    const resEscala = await pEscala;
    if (meuPedido !== TAXAS_PEDIDO) return;
    renderTaxasAba(resEscala, null, null, null, null, mes);
    // fase 2: conversao por closer, taxa de agendamento etc.
    const [resDash, resNS, ...resEvolucoes] = await pResto;
    if (meuPedido !== TAXAS_PEDIDO) return;
    TAXAS_CARREGADA_MES = chave;
    renderTaxasAba(resEscala, resDash, resEvolucoes, resNS, null, mes);
  } catch (e) {
    $('taxas-resultado').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  }
}

function renderTaxasAba(resEscala, resDash, resEvolucoes, resNS, rangeNS, mesNS) {
  let html = '';

  // ---- 1) reunioes agendadas fora da escala (metrica principal, nova) ----
  html += `<div class="nb-title">Reuniões agendadas fora da escala — ${resEscala.month_label || ''}</div>`;
  if (resEscala.error || resEscala.erro) {
    html += `<div class="warn">Erro: ${resEscala.error || resEscala.erro}</div>`;
  } else {
    if (!resEscala.escala_configurada) {
      const motivoEsc = resEscala.erro_escala
        ? `Não consegui carregar a escala comercial: <b>${resEscala.erro_escala}</b>. Confira a aba da escala na planilha (ESCALA_COMERCIAL_CSV_URL).`
        : 'A escala comercial está vazia ou não configurada (ESCALA_COMERCIAL_CSV_URL).';
      html += `<div class="warn" style="margin-bottom:8px">${motivoEsc} O total de reuniões aparece, mas "fora da escala" fica zerado até isso ser corrigido.</div>`;
    }
    html += `<div class="panel" style="margin:8px 0 12px;padding:10px 12px">
      <div style="font-size:12px;font-weight:700;margin-bottom:6px">Dias liberados (ex.: sábados trabalhados)</div>
      <div class="muted" style="font-size:12px;margin-bottom:8px">Reuniões criadas nesses dias são desconsideradas (não entram em avaliadas nem em fora da escala), sem olhar a escala. Sábados e domingos que não estiverem aqui, e sem escala na planilha, contam como <b>fora da escala</b>.</div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <input type="date" id="lib-novo" style="padding:4px 6px">
        <button class="grf-btn" onclick="taxasAddLiberado()">Adicionar dia</button>
        ${TAXAS_LIBERADOS.length ? TAXAS_LIBERADOS.map(d => `<span class="grf-chip on" style="cursor:default">${fmtDia(d)} <a href="#" onclick="taxasRemLiberado('${d}');return false" style="margin-left:4px;text-decoration:none" title="Remover">✕</a></span>`).join(' ') : '<span class="muted" style="font-size:12px">nenhum dia liberado</span>'}
      </div></div>`;
    html += `<div class="muted" style="margin-bottom:8px">Conta, por SDR, quantas reuniões FEITAS e VALIDADAS no período ela mesma criou FORA do horário de trabalho dela na escala comercial (antes da entrada, depois da saída ou no fim de semana). O período é o do filtro "De" e "Até" do cabeçalho (ou o mês inteiro), pelo dia em que a reunião foi realizada, independente de quando o lead foi criado ou aplicado.</div>`;
    const ROT_MOT = { criada_por_outro: 'Criada por outra pessoa', sem_escala: 'Sem linha de escala no dia', dia_liberado: 'Dia liberado (desconsiderado)' };
    const motivosHtml = s => {
      const m = s.motivos || {}, d = s.detalhe || {};
      const resumo = Object.keys(ROT_MOT).filter(k => m[k]).map(k => `${ROT_MOT[k]}: <b>${m[k]}</b>`).join(' · ');
      if (!resumo) return '<span class="muted">—</span>';
      const lista = Object.keys(ROT_MOT).filter(k => m[k]).map(k =>
        `<div style="margin-top:4px"><b>${ROT_MOT[k]} (${m[k]})</b>: ` + (d[k] || []).map(e =>
          `<a href="${e.url}" target="_blank" rel="noopener" title="${e.titulo} — criada ${e.data_hora_criacao}">#${e.deal_id}</a>${e.extra ? ' <span class="muted">(' + e.extra + ')</span>' : ''}`).join(', ')
          + (m[k] > (d[k] || []).length ? ' …' : '') + '</div>').join('');
      return `<details><summary style="cursor:pointer">${resumo}</summary>${lista}</details>`;
    };
    html += `<table class="aud-tbl"><tr><th class="l">SDR</th><th class="l">Time</th><th class="l">Entrada</th><th class="l">Saída</th>
      <th>Validadas (M6)</th><th>Avaliadas</th><th>Fora da escala</th><th class="l" title="Reuniões validadas que ficaram fora da conta de fora da escala, e o motivo">Não avaliadas — por quê</th><th class="l">Negócios fora da escala</th></tr>`;
    const sdrsEscala = (resEscala.sdrs || []).slice().sort((a,b) => (!!a.lideranca - !!b.lideranca) || ((b.total_mes||0) - (a.total_mes||0)));
    for (const s of sdrsEscala) {
      if (s.erro) {
        html += `<tr><td class="l">${s.nome}</td><td class="l muted">${s.time||''}</td>
          <td class="l muted" colspan="7">${s.erro}</td></tr>`;
        continue;
      }
      const lista = (s.exemplos || []).map(e =>
        `<a href="${e.url}" target="_blank" rel="noopener" title="${e.titulo}">#${e.deal_id}</a> <span class="muted">(criada ${e.data_hora_criacao})</span>`
      ).join('<br>');
      const exemplos = lista
        ? `<details><summary style="cursor:pointer">Ver ${(s.exemplos || []).length} negócio${(s.exemplos || []).length > 1 ? 's' : ''}</summary><div style="margin-top:4px;font-size:12px;line-height:1.6">${lista}</div></details>`
        : '<span class="muted">—</span>';
      const escSem = (s.escala_semana || []).length
        ? `<details style="font-size:11px;font-weight:400"><summary style="cursor:pointer" class="muted">escala da semana</summary>${s.escala_semana.join('<br>')}</details>` : '';
      html += `<tr><td class="l">${s.nome}${s.lideranca ? ' <span class="cargo-lider">' + s.lideranca + '</span>' : ''}${escSem}</td><td class="l muted">${s.time||''}</td>
        <td class="l muted">${s.entrada || '—'}</td>
        <td class="l muted">${s.saida || '—'}</td>
        <td class="qtd">${s.total_mes}</td>
        <td class="qtd">${s.avaliadas || 0}</td>
        <td class="qtd">${s.fora_da_escala}<div class="muted" style="font-size:11px">${s.pct_fora_escala}%</div></td>
        <td class="l" style="font-size:12px">${motivosHtml(s)}</td>
        <td class="l" style="font-size:12px">${exemplos}</td></tr>`;
    }
    if (!sdrsEscala.length) {
      html += `<tr><td colspan="9" class="aud-empty">Nenhum SDR encontrado no mês.</td></tr>`;
    }
    const t = resEscala.total || {};
    html += `<tr class="total"><td class="l">TOTAL</td><td></td><td></td><td></td>
      <td class="qtd">${t.total_mes||0}</td>
      <td class="qtd">${t.avaliadas||0}</td>
      <td class="qtd">${t.fora_da_escala||0}<div class="muted" style="font-size:11px">${t.pct_fora_escala||0}%</div></td>
      <td></td><td></td></tr>`;
    html += `</table>`;
    html += `<div class="muted" style="margin-top:8px;font-size:12px">Validadas (M6) = o mesmo número da aba Reuniões - SDRs. <b>Versão de teste (não é a OP2 oficial):</b> a escala usada é a da própria SDR (nome + dia da semana + time dela), sem olhar o funil do negócio. Só entram na conta as <b>avaliadas</b>: feitas e validadas no período, criadas pela própria SDR e com escala no dia (fim de semana sem escala conta como fora; reuniões criadas em dias liberados são desconsideradas). A % é fora ÷ avaliadas. Clique em "Não avaliadas — por quê" para ver os negócios de cada motivo.</div>`;
    const dg = resEscala.diagnostico;
    if (dg && Object.keys(dg.funis_sem_escala || {}).length) {
      html += `<div class="muted" style="margin-top:4px;font-size:12px">Funis sem escala: ${Object.entries(dg.funis_sem_escala).map(([k, v]) => k + ' (' + v + ')').join(', ')} · Subáreas na planilha de escala: ${(dg.subareas_da_escala || []).join(', ') || '—'}</div>`;
    }
  }

  // fase 1: so a tabela de fora da escala (rapida); o resto chega depois e re-renderiza
  if (resDash === null) {
    html += '<div class="muted" style="margin-top:18px">Carregando conversão por closer e taxa de agendamento…</div>';
    $('taxas-resultado').innerHTML = html;
    return;
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

  html += taxaNoShowSemanal(resNS, rangeNS, mesNS);

  $('taxas-resultado').innerHTML = html;
}

// ---- Taxa de No-show por SDR, por semana (seg a dom) ----
// taxa = no-show / (feitas + no-show): das reunioes que deveriam acontecer, quantas o lead faltou.
// Reagendadas ficam fora (nao tiveram desfecho). Respeita Mes ou De/Ate do cabecalho.
function taxaNoShowSemanal(resNS, rangeNS, mes) {
  const [my, mm] = mes.split('-').map(Number);
  let html = `<div class="nb-title" style="margin-top:22px">Taxa de No-show por SDR — mês todo (${String(mm).padStart(2, '0')}/${my})</div>`;
  const erro = (resNS || []).find(r => !r.d || r.d.error || r.d.erro);
  if (!resNS || !resNS.length || erro) {
    return html + `<div class="warn">Erro ao buscar os no-shows${erro && erro.d ? ': ' + (erro.d.error || erro.d.erro) : ''}</div>`;
  }
  const iso = (y, m, d) => y + '-' + String(m).padStart(2, '0') + '-' + String(d).padStart(2, '0');
  // sempre o MES inteiro (nao depende de De/Ate): do dia 1 ao ultimo dia
  const de = iso(my, mm, 1);
  const ate = iso(my, mm, new Date(my, mm, 0).getDate());
  // semanas (segunda a domingo) recortadas no mes
  const semanas = [];
  const dd = s => new Date(s + 'T12:00:00');
  const fmtD = dt => dt.toISOString().slice(0, 10);
  let cur = dd(de);
  const fimP = dd(ate);
  while (cur <= fimP) {
    const dow = (cur.getDay() + 6) % 7;                      // 0 = segunda
    const dom = new Date(cur.getTime() + (6 - dow) * 864e5);
    const fim = dom > fimP ? fimP : dom;
    semanas.push({ ini: fmtD(cur), fim: fmtD(fim) });
    cur = new Date(fim.getTime() + 864e5);
  }
  const rot = s => s.slice(8, 10) + '/' + s.slice(5, 7);
  // pessoa -> semana -> {ns, validadas}
  const pessoas = {};
  for (const { mes: m, d } of resNS) {
    for (const p of (d.por_closer || [])) {
      const o = pessoas[p.name] || (pessoas[p.name] = { name: p.name, time: p.time, lider: p.lideranca, sem: semanas.map(() => ({ ns: 0, f: 0 })), itens: [] });
      for (const nd of (p.negocios_dia || [])) {
        const data = iso(Number(m.slice(0, 4)), Number(m.slice(5, 7)), nd.dia);
        const i = semanas.findIndex(w => data >= w.ini && data <= w.fim);
        for (const it of (nd.itens || [])) {
          const st = it.status === 'Validada' ? 'val' : (it.status === 'No Show' ? 'ns' : '');
          if (st) o.itens.push({ id: it.id, title: it.title, url: it.url, hora: it.hora, data, st, vl: it.validacao || '', sem: i });
        }
      }
      for (const it of (p.days || [])) {
        const data = iso(Number(m.slice(0, 4)), Number(m.slice(5, 7)), it.dia);
        const i = semanas.findIndex(w => data >= w.ini && data <= w.fim);
        if (i < 0) continue;
        const c = it.counter || {};
        o.sem[i].ns += c.no_show || 0; o.sem[i].f += c.validada || 0;
      }
    }
  }
  const lista = Object.values(pessoas).sort((a, b) => (!!a.lider - !!b.lider) || a.name.localeCompare(b.name));
  const pct = (ns, base) => base ? (ns / base * 100).toFixed(1).replace('.', ',') + '%' : '—';
  const nome = p => `${p.name}${p.lider ? ' <span class="cargo-lider">' + p.lider + '</span>' : ''}`;
  NS_D = { lista, semanas, mes };
  // celula clicavel: p = indice da pessoa (-1 = time todo), k = val | ns | tot, w = indice da semana (-1 = mes todo)
  const cl = (txt, pi, k, w, bold) => `<td class="qtd nsk" data-np="${pi}" data-nk="${k}" data-nw="${w}" style="cursor:pointer">${bold ? '<b>' + txt + '</b>' : txt}</td>`;
  html += `<div class="muted" style="margin-bottom:8px">No-show ÷ (validadas + no-show) de cada SDR (NS1), no mês todo. Reagendadas ficam fora (não tiveram desfecho). Clique em um número ou no nome do SDR para ver os negócios (IDs e link do Pipedrive) e exportar.</div>`;
  // tabela principal: mes todo, uma coluna por numero
  html += `<table class="aud-tbl"><tr><th class="l">SDR</th><th class="l">Time</th><th>Validadas</th><th>No-show</th><th>Validadas + No-show</th><th>Taxa de no-show</th></tr>`;
  const tot = semanas.map(() => ({ ns: 0, f: 0 }));
  let gns = 0, gf = 0;
  lista.forEach((p, pi) => {
    let ns = 0, f = 0;
    p.sem.forEach((x, i) => { ns += x.ns; f += x.f; tot[i].ns += x.ns; tot[i].f += x.f; });
    gns += ns; gf += f;
    html += `<tr><td class="l nsk" data-np="${pi}" data-nk="tot" data-nw="-1" style="cursor:pointer">${nome(p)}</td><td class="l muted">${p.time || ''}</td>
      ${cl(f, pi, 'val', -1)}${cl(ns, pi, 'ns', -1)}${cl(f + ns, pi, 'tot', -1)}${cl(pct(ns, f + ns), pi, 'tot', -1, true)}</tr>`;
  });
  if (!lista.length) {
    html += `<tr><td colspan="6" class="aud-empty">Nenhum SDR no período.</td></tr>`;
  } else {
    html += `<tr class="total"><td class="l nsk" data-np="-1" data-nk="tot" data-nw="-1" style="cursor:pointer">TOTAL</td><td></td>${cl(gf, -1, 'val', -1)}${cl(gns, -1, 'ns', -1)}${cl(gf + gns, -1, 'tot', -1)}${cl(pct(gns, gf + gns), -1, 'tot', -1, true)}</tr>`;
  }
  html += `</table>`;
  html += `<div class="mx-lista" id="ns-lista"></div>`;
  // detalhe semana a semana (recolhido): uma linha por SDR e semana, cada numero na sua coluna
  if (lista.length) {
    const linha = (x, ini, fim, pi, wi) => `<td>${rot(ini)} a ${rot(fim)}</td>${cl(x.f, pi, 'val', wi)}${cl(x.ns, pi, 'ns', wi)}${cl(x.f + x.ns, pi, 'tot', wi)}${cl(pct(x.ns, x.f + x.ns), pi, 'tot', wi, true)}`;
    html += `<details style="margin-top:8px"><summary style="cursor:pointer" class="muted">Ver semana a semana</summary>
      <table class="aud-tbl" style="margin-top:6px"><tr><th class="l">SDR</th><th class="l">Semana</th><th>Validadas</th><th>No-show</th><th>Validadas + No-show</th><th>Taxa de no-show</th></tr>`;
    lista.forEach((p, pi) => {
      const ativas = semanas.map((w, i) => ({ w, wi: i, x: p.sem[i] })).filter(o => o.x.f + o.x.ns > 0);
      if (!ativas.length) { html += `<tr><td class="l">${nome(p)}</td><td colspan="5" class="muted">sem reuniões no mês</td></tr>`; return; }
      ativas.forEach((o, k) => {
        html += `<tr>${k === 0 ? `<td class="l" rowspan="${ativas.length}">${nome(p)}</td>` : ''}${linha(o.x, o.w.ini, o.w.fim, pi, o.wi)}</tr>`;
      });
    });
    semanas.forEach((w, i) => {
      if (tot[i].f + tot[i].ns > 0)
        html += `<tr class="total">${i === 0 || !(tot.slice(0, i).some(t => t.f + t.ns > 0)) ? '<td class="l">TOTAL DO TIME</td>' : '<td></td>'}${linha(tot[i], w.ini, w.fim, -1, i)}</tr>`;
    });
    html += `</table></details>`;
  }
  return html;
}

let NS_D = { lista: [], semanas: [], mes: '' };
let NS_SEL = null;   // {p, k, w}
const NS_K = { val: 'validadas', ns: 'no-show', tot: 'validadas + no-show' };
const nsDH = n => n.data.slice(8, 10) + '/' + n.data.slice(5, 7) + (n.hora ? ' ' + n.hora : '');

function nsItens(sel) {
  const out = [];
  NS_D.lista.forEach((p, i) => {
    if (sel.p !== -1 && sel.p !== i) return;
    p.itens.forEach(it => {
      if (sel.w !== -1 && it.sem !== sel.w) return;
      if (sel.k !== 'tot' && it.st !== sel.k) return;
      out.push({ ...it, sdr: p.name });
    });
  });
  return out.sort((a, b) => (a.data + a.hora).localeCompare(b.data + b.hora) || a.id - b.id);
}

function nsMostra() {
  const box = $('ns-lista'); if (!box || !NS_SEL) return;
  const itens = nsItens(NS_SEL);
  const qSdr = NS_SEL.p === -1 ? 'Todos os SDRs' : NS_D.lista[NS_SEL.p].name;
  const w = NS_SEL.w === -1 ? 'mês todo' : (s => s.ini.slice(8, 10) + '/' + s.ini.slice(5, 7) + ' a ' + s.fim.slice(8, 10) + '/' + s.fim.slice(5, 7))(NS_D.semanas[NS_SEL.w]);
  const rot = NS_K[NS_SEL.k] + ' · ' + w;
  const ids = itens.map(n => n.id).join(', ');
  box.innerHTML = `<details open class="mx-det"><summary><b>${qSdr} · ${rot}</b> · ${itens.length} ${itens.length === 1 ? 'reunião' : 'reuniões'} <span class="muted">(clique para recolher / abrir os IDs)</span></summary>
    <div class="cab"><button class="grf-btn" id="ns-copia">Copiar IDs</button><button class="grf-btn" id="ns-xlsx">Exportar Excel</button></div>
    <div class="rol"><table><tr><th>ID</th><th class="hide-m">Negócio</th><th>Data / hora</th><th>SDR</th><th>Status</th><th>Reunião Validada?</th></tr>${
      itens.map(n => `<tr><td><a href="${n.url}" target="_blank" rel="noopener">#${n.id}</a></td><td class="hide-m">${n.title || ''}</td><td>${nsDH(n)}</td><td>${n.sdr}</td><td>${n.st === 'ns' ? 'No-show' : 'Validada'}</td><td>${audVRot(n.vl)}</td></tr>`).join('')
      || '<tr><td colspan="6" class="aud-empty">Nenhum negócio.</td></tr>'}</table></div></details>`;
  $('ns-copia').addEventListener('click', () => {
    const b = $('ns-copia');
    const ok = () => { b.textContent = 'Copiado!'; setTimeout(() => { b.textContent = 'Copiar IDs'; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(ids).then(ok, () => {}); else ok();
  });
  $('ns-xlsx').addEventListener('click', () => nsExporta(itens, qSdr, rot));
}

function nsExporta(itens, qSdr, rot) {
  const slug = t => String(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_|_$/g, '').toLowerCase();
  const nome = `noshow_${NS_D.mes}_${slug(qSdr)}_${slug(rot)}`;
  const linhas = [['ID', 'Negócio', 'Data da reunião', 'Hora', 'SDR', 'Status', 'Reunião Validada?', 'Link Pipedrive']]
    .concat(itens.map(n => [n.id, n.title || '', n.data, n.hora || '', n.sdr, n.st === 'ns' ? 'No-show' : 'Validada', audVRot(n.vl), n.url]));
  if (window.XLSX) {
    const ws = XLSX.utils.aoa_to_sheet(linhas);
    ws['!cols'] = [{ wch: 10 }, { wch: 45 }, { wch: 14 }, { wch: 8 }, { wch: 22 }, { wch: 12 }, { wch: 16 }, { wch: 48 }];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'No-show');
    XLSX.writeFile(wb, nome + '.xlsx');
    return;
  }
  const csv = '\ufeff' + linhas.map(l => l.map(v => '"' + String(v).replace(/"/g, '""') + '"').join(';')).join('\r\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  a.download = nome + '.csv';
  document.body.appendChild(a); a.click(); a.remove();
}

document.addEventListener('click', ev => {
  const el = ev.target.closest('#taxas-resultado [data-nk]');
  if (!el) return;
  NS_SEL = { p: Number(el.dataset.np), k: el.dataset.nk, w: Number(el.dataset.nw) };
  nsMostra();
});

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

// ---- Auditoria SDR: matriz Closer x quem agendou (reunioes validadas do mes, closer = dono do negocio) ----
// linhas (descendo) = closers; colunas (no topo) = SDRs/lideranca que agendaram
let AUD_M = null;      // {sdrs, closers, cel}
let AUD_SEL = { s: null, c: null };   // SDR (coluna) e/ou closer (linha) escolhidos; -1 = todos

function audNomeEmDuas(n) {
  const p = String(n).trim().split(/\s+/);
  return p.length > 1 ? `${p[0]}<span class="th-sub">${p.slice(1).join(' ')}</span>` : n;
}

let AUD_MODO = 'todas';   // filtro da página inteira: todas | sim | vazio | nao | validadas (Sim + vazio)
let AUD_DATA = null;
function audModo(m) { AUD_MODO = (AUD_MODO === m && m !== 'todas') ? 'todas' : m; if (AUD_DATA) renderAuditoria(AUD_DATA); }
const audPassaF = st => AUD_MODO === 'todas' || (AUD_MODO === 'validadas' ? (st === 'sim' || st === 'vazio') : st === AUD_MODO);
function audFiltraValidacao(lista) {
  return (lista || []).map(x => {
    const itens = (x.itens || []).filter(it => audPassaF(it.st));
    const c = { vol: itens.length, sim: 0, vazio: 0, nao: 0 };
    itens.forEach(it => { if (c[it.st] !== undefined) c[it.st]++; });
    return { closer: x.closer, ...c, itens };
  }).filter(x => x.vol > 0).sort((a, b) => b.vol - a.vol || a.closer.localeCompare(b.closer));
}
function audFiltraMotivos(lista) {
  return (lista || []).map(m => {
    const itens = (m.itens || []).filter(it => audPassaF(it.st));
    return { motivo: m.motivo, qtd: itens.length, itens };
  }).filter(m => m.qtd > 0).sort((a, b) => b.qtd - a.qtd || a.motivo.localeCompare(b.motivo));
}

let AUD_V = { lista: [], sel: null };   // sel = {c: índice do closer (-1 = todos), k: 'vol'|'sim'|'val'|'nao'|'vazio'}
const AUD_V_NOME = { vol: 'todas as reuniões feitas', sim: 'validadas (Sim)', val: 'validadas (Sim + vazio)', nao: 'não validadas (Não)', vazio: 'sem informação (vazio)' };
const audVPassa = (it, k) => k === 'vol' || (k === 'val' ? (it.st === 'sim' || it.st === 'vazio') : it.st === k);
const audDH = n => n.data ? n.data.slice(8, 10) + '/' + n.data.slice(5, 7) + (n.hora ? ' ' + n.hora : '') : '';
const audVRot = st => ({ sim: 'Sim', vazio: 'Vazio', nao: 'Não' }[st] || '—');

function audTabelaValidacao(lista) {
  lista = audFiltraValidacao(lista);
  AUD_V = { lista, sel: null };
  const p = (a, b) => b ? (a / b * 100).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%' : '—';
  const n = v => (v || 0).toLocaleString('pt-BR');
  const T = lista.reduce((t, x) => ({ vol: t.vol + x.vol, sim: t.sim + x.sim, vazio: t.vazio + x.vazio, nao: t.nao + x.nao }), { vol: 0, sim: 0, vazio: 0, nao: 0 });
  const celula = (txt, c, k, bold) => `<td class="n vk" data-vc="${c}" data-vk="${k}" style="cursor:pointer">${bold ? '<b>' + txt + '</b>' : txt}</td>`;
  const linha = (x, nome, c, cls) => {
    const base = x.sim + x.vazio + x.nao;
    return `<tr class="${cls}"><td class="vk" data-vc="${c}" data-vk="vol" style="cursor:pointer">${nome}</td>${celula(n(x.vol), c, 'vol')}${celula(n(x.sim), c, 'sim')}${celula(n(x.sim + x.vazio), c, 'val')}${celula(n(x.nao), c, 'nao')}${celula(n(x.vazio), c, 'vazio')}${celula(p(x.sim + x.vazio, base), c, 'val', true)}${celula(p(x.sim, base), c, 'sim', true)}</tr>`;
  };
  return `<div class="kpi-head" style="margin-top:22px">Validação das reuniões</div>
    <div class="muted" style="margin:4px 0 10px;font-size:12px">Só reuniões feitas · campo “Reunião Validada?” do negócio, vale para todas as reuniões dele · taxas sobre o volume de reuniões · clique em um número ou no nome do closer para ver os negócios (IDs e link do Pipedrive) e exportar.</div>
    <div class="mx-wrap"><table class="mx val-tab" id="aud-val"><tr><th class="l">Closer</th><th>Volume de reuniões</th><th>Validadas (Sim)</th><th>Validadas (Sim + vazio)</th><th>Não validadas (Não)</th><th>Sem informação (vazio)</th><th>Taxa de qualificação (Sim + vazio)</th><th>Taxa de qualificação (Sim)</th></tr>${
      lista.length ? lista.map((x, i) => linha(x, x.closer, i, '')).join('') + linha(T, 'Total', -1, 'tot')
        : '<tr><td colspan="8" class="aud-empty">Nenhuma reunião feita no mês.</td></tr>'}</table></div>
    <div class="mx-lista" id="aud-val-lista"></div>`;
}

function audValMostra() {
  const box = $('aud-val-lista'); if (!box || !AUD_V.sel) return;
  const { c, k } = AUD_V.sel;
  const itens = [];
  AUD_V.lista.forEach((x, i) => { if (c === -1 || c === i) x.itens.forEach(it => { if (audVPassa(it, k)) itens.push({ ...it, closer: x.closer }); }); });
  const qClo = c === -1 ? 'Todos os closers' : AUD_V.lista[c].closer;
  const rot = AUD_V_NOME[k];
  const ids = itens.map(n => n.id).join(', ');
  box.innerHTML = `<details open class="mx-det"><summary><b>${qClo} · ${rot}</b> · ${itens.length} ${itens.length === 1 ? 'reunião' : 'reuniões'} <span class="muted">(clique para recolher / abrir os IDs)</span></summary>
    <div class="cab"><button class="grf-btn" id="aud-val-copia">Copiar IDs</button><button class="grf-btn" id="aud-val-xlsx">Exportar Excel</button></div>
    <div class="rol"><table><tr><th>ID</th><th class="hide-m">Negócio</th><th>Closer</th><th>Data</th><th>Reunião Validada?</th></tr>${
      itens.map(n => `<tr><td><a href="${n.url}" target="_blank" rel="noopener">#${n.id}</a></td><td class="hide-m">${n.title || ''}</td><td>${n.closer}</td><td>${audDH(n)}</td><td>${audVRot(n.st)}</td></tr>`).join('')
      || '<tr><td colspan="5" class="aud-empty">Nenhum negócio.</td></tr>'}</table></div></details>`;
  $('aud-val-copia').addEventListener('click', () => {
    const b = $('aud-val-copia');
    const ok = () => { b.textContent = 'Copiado!'; setTimeout(() => { b.textContent = 'Copiar IDs'; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(ids).then(ok, () => {}); else ok();
  });
  $('aud-val-xlsx').addEventListener('click', () => audExportaValidacao(itens, qClo, rot));
}

function audExportaValidacao(itens, qClo, rot) {
  const slug = t => String(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_|_$/g, '').toLowerCase();
  const nome = `validacao_${$('f-mes').value}_${slug(qClo)}_${slug(rot)}`;
  const linhas = [['ID', 'Negócio', 'Closer', 'Data da reunião', 'Hora', 'Reunião Validada?', 'Link Pipedrive']]
    .concat(itens.map(n => [n.id, n.title || '', n.closer, n.data || '', n.hora || '', audVRot(n.st), n.url]));
  if (window.XLSX) {
    const ws = XLSX.utils.aoa_to_sheet(linhas);
    ws['!cols'] = [{ wch: 10 }, { wch: 45 }, { wch: 22 }, { wch: 14 }, { wch: 8 }, { wch: 18 }, { wch: 48 }];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Validação');
    XLSX.writeFile(wb, nome + '.xlsx');
    return;
  }
  const csv = '\ufeff' + linhas.map(l => l.map(v => '"' + String(v).replace(/"/g, '""') + '"').join(';')).join('\r\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  a.download = nome + '.csv';
  document.body.appendChild(a); a.click(); a.remove();
}

$('root-aud').addEventListener('click', ev => {
  const el = ev.target.closest('#aud-val [data-vk]');
  if (!el) return;
  AUD_V.sel = { c: Number(el.dataset.vc), k: el.dataset.vk };
  audValMostra();
});

let AUD_M2 = { lista: [], sel: null };   // motivos de perda; sel = {m: índice do motivo, -1 = todos}
const audDMes = s => s ? s.slice(8, 10) + '/' + s.slice(5, 7) : '';

function audTabelaMotivos(lista) {
  lista = audFiltraMotivos(lista);
  AUD_M2 = { lista, sel: null };
  const tot = lista.reduce((a, x) => a + x.qtd, 0);
  const max = lista.length ? lista[0].qtd : 1;
  const p = v => tot ? (v / tot * 100).toLocaleString('pt-BR', { maximumFractionDigits: 1 }) + '%' : '—';
  const linha = (x, i) => `<tr class="mk" data-mk="${i}" style="cursor:pointer"><td class="l">${x.motivo}</td><td>${x.qtd.toLocaleString('pt-BR')}</td><td>${p(x.qtd)}</td><td class="l" style="width:34%"><div style="height:7px;border-radius:4px;background:#2f4b6e;width:${(x.qtd / max * 100).toFixed(0)}%"></div></td></tr>`;
  return `<div class="kpi-head" style="margin-top:22px">Motivos de perda</div>
    <div class="muted" style="margin:4px 0 10px;font-size:12px">Negócios <b>perdidos</b> com reunião feita no mês (P1: motivo como está no Pipedrive) · cada negócio conta uma vez · clique em um motivo para ver os negócios (IDs e link do Pipedrive) e exportar.</div>
    <div class="mx-wrap"><table class="mx val-tab" id="aud-mot"><tr><th class="l">Motivo</th><th>Negócios</th><th>%</th><th></th></tr>${
      lista.length ? lista.map(linha).join('') + `<tr class="tot mk" data-mk="-1" style="cursor:pointer"><td class="l">Total</td><td>${tot.toLocaleString('pt-BR')}</td><td>100%</td><td></td></tr>`
        : '<tr><td colspan="4" class="aud-empty">Nenhum negócio perdido com reunião feita no mês.</td></tr>'}</table></div>
    <div class="mx-lista" id="aud-mot-lista"></div>`;
}

function audMotivoMostra() {
  const box = $('aud-mot-lista'); if (!box || !AUD_M2.sel) return;
  const m = AUD_M2.sel.m;
  const itens = [];
  AUD_M2.lista.forEach((x, i) => { if (m === -1 || m === i) x.itens.forEach(it => itens.push({ ...it, motivo: x.motivo })); });
  const rot = m === -1 ? 'Todos os motivos' : AUD_M2.lista[m].motivo;
  const ids = itens.map(n => n.id).join(', ');
  box.innerHTML = `<details open class="mx-det"><summary><b>${rot}</b> · ${itens.length} ${itens.length === 1 ? 'negócio' : 'negócios'} <span class="muted">(clique para recolher / abrir os IDs)</span></summary>
    <div class="cab"><button class="grf-btn" id="aud-mot-copia">Copiar IDs</button><button class="grf-btn" id="aud-mot-xlsx">Exportar Excel</button></div>
    <div class="rol"><table><tr><th>ID</th><th class="hide-m">Negócio</th><th>Motivo</th><th>Closer</th><th>Agendada por</th><th>Reunião</th><th>Reunião Validada?</th><th>Perdido em</th></tr>${
      itens.map(n => `<tr><td><a href="${n.url}" target="_blank" rel="noopener">#${n.id}</a></td><td class="hide-m">${n.title || ''}</td><td>${n.motivo}</td><td>${n.closer}</td><td>${n.sdr}</td><td>${audDMes(n.data)}${n.hora ? ' ' + n.hora : ''}</td><td>${audVRot(n.st)}</td><td>${audDMes(n.perdido_em)}</td></tr>`).join('')
      || '<tr><td colspan="8" class="aud-empty">Nenhum negócio.</td></tr>'}</table></div></details>`;
  $('aud-mot-copia').addEventListener('click', () => {
    const b = $('aud-mot-copia');
    const ok = () => { b.textContent = 'Copiado!'; setTimeout(() => { b.textContent = 'Copiar IDs'; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(ids).then(ok, () => {}); else ok();
  });
  $('aud-mot-xlsx').addEventListener('click', () => audExportaMotivos(itens, rot));
}

function audExportaMotivos(itens, rot) {
  const slug = t => String(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_|_$/g, '').toLowerCase();
  const nome = `motivos_perda_${$('f-mes').value}_${slug(rot)}`;
  const linhas = [['ID', 'Negócio', 'Motivo de perda', 'Closer', 'Agendada por', 'Data da reunião', 'Hora', 'Reunião Validada?', 'Perdido em', 'Link Pipedrive']]
    .concat(itens.map(n => [n.id, n.title || '', n.motivo, n.closer, n.sdr, n.data || '', n.hora || '', audVRot(n.st), n.perdido_em || '', n.url]));
  if (window.XLSX) {
    const ws = XLSX.utils.aoa_to_sheet(linhas);
    ws['!cols'] = [{ wch: 10 }, { wch: 45 }, { wch: 34 }, { wch: 22 }, { wch: 22 }, { wch: 14 }, { wch: 8 }, { wch: 16 }, { wch: 12 }, { wch: 48 }];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Motivos de perda');
    XLSX.writeFile(wb, nome + '.xlsx');
    return;
  }
  const csv = '\ufeff' + linhas.map(l => l.map(v => '"' + String(v).replace(/"/g, '""') + '"').join(';')).join('\r\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  a.download = nome + '.csv';
  document.body.appendChild(a); a.click(); a.remove();
}

$('root-aud').addEventListener('click', ev => {
  const el = ev.target.closest('#aud-mot [data-mk]');
  if (!el) return;
  AUD_M2.sel = { m: Number(el.dataset.mk) };
  audMotivoMostra();
});

function renderAuditoria(data) {
  AUD_DATA = data;
  const filtra = l => {
    const closers = (l.closers || []).map(c => {
      const negocios = (c.negocios || []).filter(n => audPassaF(n.st));
      return { closer: c.closer, qtd: negocios.length, negocios };
    }).filter(c => c.qtd > 0);
    return { ...l, closers, total: closers.reduce((a, c) => a + c.qtd, 0) };
  };
  data = { ...data, sdrs: (data.sdrs || []).map(filtra), liderancas: (data.liderancas || []).map(filtra), outros: (data.outros || []).map(filtra) };
  const sdrs = []
    .concat((data.sdrs || []).slice().sort((a, b) => b.total - a.total).map(s => ({ nome: s.nome, cargo: '', total: s.total, closers: s.closers })))
    .concat((data.liderancas || []).slice().sort((a, b) => b.total - a.total).map(s => ({ nome: s.nome, cargo: s.label, total: s.total, closers: s.closers })))
    .concat((data.outros || []).map(s => ({ nome: s.nome, cargo: s.label || '', total: s.total, closers: s.closers })));
  const totCloser = {};
  sdrs.forEach(l => l.closers.forEach(c => { totCloser[c.closer] = (totCloser[c.closer] || 0) + c.qtd; }));
  const closers = Object.keys(totCloser).sort((a, b) => totCloser[b] - totCloser[a] || a.localeCompare(b));
  const cel = {};   // "i|j" (i = SDR, j = closer) -> negocios
  sdrs.forEach((l, i) => l.closers.forEach(c => { cel[i + '|' + closers.indexOf(c.closer)] = c.negocios || []; }));
  AUD_M = { sdrs, closers, cel };
  AUD_SEL = { s: null, c: null };

  let html = `<div class="kpi-head">Closer × quem agendou · ${data.month_label}</div>`;
  const VT = (AUD_DATA.validacao || []).reduce((t, x) => ({ vol: t.vol + x.vol, sim: t.sim + x.sim, vazio: t.vazio + x.vazio, nao: t.nao + x.nao }), { vol: 0, sim: 0, vazio: 0, nao: 0 });
  const chip = (k, nome, n) => `<button class="tab${AUD_MODO === k ? ' active' : ''}" onclick="audModo('${k}')">${nome} <b>${n.toLocaleString('pt-BR')}</b></button>`;
  html += `<div class="muted" style="margin:6px 0 4px;font-size:12px">Filtro da página inteira · <b>Reunião Validada?</b> (clique de novo para desfazer)</div>
    <div style="margin:0 0 10px;display:flex;flex-wrap:wrap;gap:6px">${chip('todas', 'Todas', VT.vol)}${chip('sim', 'Sim', VT.sim)}${chip('vazio', 'Vazio', VT.vazio)}${chip('nao', 'Não', VT.nao)}${chip('validadas', 'Validadas (Sim + vazio)', VT.sim + VT.vazio)}</div>`;
  const NOME_F = { todas: 'todas as reuniões feitas', sim: 'só “Reunião Validada?” = Sim', vazio: 'só “Reunião Validada?” vazio', nao: 'só “Reunião Validada?” = Não', validadas: 'só validadas (Sim + vazio)' }[AUD_MODO];
  html += `<div class="muted" style="margin:4px 0 10px;font-size:12px">Reuniões feitas do closer, agrupadas por quem criou a reunião · <b>${NOME_F}</b> no mês · linha = closer da reunião · coluna = quem criou a reunião (SDR/liderança) · clique em um número, no nome do closer ou no nome do SDR para ver os negócios (IDs do Pipedrive). A tabela de validação e os motivos de perda abaixo seguem o mesmo filtro.</div>`;
  if (!sdrs.length) {
    $('root-aud').innerHTML = html + '<div class="aud-empty">Nenhum SDR encontrado no mês.</div>' + audTabelaValidacao(data.validacao || []) + audTabelaMotivos(data.motivos || []);
    return;
  }
  const max = Math.max(1, ...sdrs.flatMap(l => l.closers.map(c => c.qtd)));
  const heat = v => `background:rgba(255,200,0,${(0.14 + 0.72 * v / max).toFixed(2)})`;
  html += `<div class="mx-wrap"><table class="mx" id="aud-mx"><tr><th class="l" data-limpa="1">Closer \\ agendada por</th>`;
  sdrs.forEach((l, i) => { html += `<th data-s="${i}">${audNomeEmDuas(l.nome)}${l.cargo ? '<span class="th-sub">' + l.cargo + '</span>' : ''}</th>`; });
  html += `<th class="t" data-todos="1">Total</th></tr>`;
  closers.forEach((cn, j) => {
    html += `<tr><td class="l" data-c="${j}">${cn}</td>`;
    sdrs.forEach((l, i) => {
      const n = (cel[i + '|' + j] || []).length;
      html += n ? `<td class="c" data-s="${i}" data-c="${j}" style="${heat(n)}">${n}</td>` : `<td class="z">·</td>`;
    });
    html += `<td class="t" data-c="${j}">${totCloser[cn]}</td></tr>`;
  });
  const gt = sdrs.reduce((a, l) => a + l.total, 0);
  html += `<tr class="tot"><td class="l" data-todos="1">Total</td>`;
  sdrs.forEach((l, i) => { html += `<td data-s="${i}" style="cursor:pointer">${l.total}</td>`; });
  html += `<td data-todos="1" style="cursor:pointer">${gt}</td></tr></table></div>`;
  html += `<div class="mx-lista" id="aud-lista"></div>`;
  html += audTabelaValidacao(data.validacao || []) + audTabelaMotivos(data.motivos || []);
  $('root-aud').innerHTML = html;

  $('aud-mx').addEventListener('click', ev => {
    const el = ev.target.closest('[data-s],[data-c],[data-todos],[data-limpa]');
    if (!el) return;
    if (el.hasAttribute('data-limpa')) { AUD_SEL = { s: null, c: null }; }
    else if (el.hasAttribute('data-todos')) { AUD_SEL = { s: -1, c: -1 }; }
    else {
      AUD_SEL = { s: el.hasAttribute('data-s') ? Number(el.dataset.s) : null, c: el.hasAttribute('data-c') ? Number(el.dataset.c) : null };
    }
    audMostraLista();
  });
}

function audMostraLista() {
  const box = $('aud-lista');
  document.querySelectorAll('#aud-mx .sel').forEach(e => e.classList.remove('sel'));
  const { s, c } = AUD_SEL;
  if (s === null && c === null) { box.innerHTML = ''; return; }
  const M = AUD_M;
  const sdrSel = (s === null || s === -1) ? M.sdrs.map((_, i) => i) : [s];
  const cloSel = (c === null || c === -1) ? M.closers.map((_, j) => j) : [c];
  const itens = [];
  for (const i of sdrSel) for (const j of cloSel)
    for (const n of (M.cel[i + '|' + j] || [])) itens.push({ ...n, sdr: M.sdrs[i].nome, closer: M.closers[j] });
  itens.sort((a, b) => a.closer.localeCompare(b.closer) || a.sdr.localeCompare(b.sdr) || a.id - b.id);
  // destaque na matriz: a celula escolhida, ou o nome da linha / da coluna
  document.querySelectorAll('#aud-mx [data-s],#aud-mx [data-c]').forEach(e => {
    const es = e.hasAttribute('data-s') ? Number(e.dataset.s) : null, ec = e.hasAttribute('data-c') ? Number(e.dataset.c) : null;
    const nomeLinha = e.tagName === 'TD' && e.classList.contains('l'), nomeColuna = e.tagName === 'TH';
    if (s !== null && s !== -1 && c !== null && c !== -1) { if (es === s && ec === c) e.classList.add('sel'); }
    else if (c !== null && c !== -1 && s === null) { if (nomeLinha && ec === c) e.classList.add('sel'); }
    else if (s !== null && s !== -1 && c === null) { if (nomeColuna && es === s) e.classList.add('sel'); }
  });
  const qSdr = (s === null || s === -1) ? 'todos os SDRs' : M.sdrs[s].nome;
  const qClo = (c === null || c === -1) ? 'todos os closers' : M.closers[c];
  const ids = itens.map(n => n.id).join(', ');
  box.innerHTML = `<details open class="mx-det"><summary><b>${qClo} ← ${qSdr}</b> · ${itens.length} ${itens.length === 1 ? 'reunião' : 'reuniões'} <span class="muted">(clique para recolher / abrir os IDs)</span></summary>
    <div class="cab"><button class="grf-btn" id="aud-copia">Copiar IDs</button><button class="grf-btn" id="aud-xlsx">Exportar Excel</button></div>
    <div class="rol"><table><tr><th>ID</th><th class="hide-m">Negócio</th><th>Data / hora</th><th>Closer</th><th>Agendada por</th><th>Reunião Validada?</th></tr>${
      itens.map(n => `<tr><td><a href="${n.url}" target="_blank" rel="noopener">#${n.id}</a></td><td class="hide-m">${n.title || ''}</td><td>${audDH(n)}</td><td>${n.closer}</td><td>${n.sdr}</td><td>${audVRot(n.st)}</td></tr>`).join('')
      || '<tr><td colspan="6" class="aud-empty">Nenhum negócio.</td></tr>'}</table></div></details>`;
  $('aud-copia').addEventListener('click', () => {
    const b = $('aud-copia');
    const ok = () => { b.textContent = 'Copiado!'; setTimeout(() => { b.textContent = 'Copiar IDs'; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(ids).then(ok, () => {}); else ok();
  });
  $('aud-xlsx').addEventListener('click', () => audExportaExcel(itens, qClo, qSdr));
  box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// exporta a lista que esta na tela (.xlsx; se a biblioteca nao carregou, cai para CSV que o Excel abre)
function audExportaExcel(itens, qClo, qSdr) {
  const slug = t => String(t).normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-zA-Z0-9]+/g, '_').replace(/^_|_$/g, '').toLowerCase();
  const nome = `auditoria_${$('f-mes').value}_${slug(qClo)}_${slug(qSdr)}`;
  const linhas = [['ID', 'Negócio', 'Data da reunião', 'Hora', 'Closer', 'Agendada por', 'Reunião Validada?', 'Link Pipedrive']]
    .concat(itens.map(n => [n.id, n.title || '', n.data || '', n.hora || '', n.closer, n.sdr, audVRot(n.st), n.url]));
  if (window.XLSX) {
    const ws = XLSX.utils.aoa_to_sheet(linhas);
    ws['!cols'] = [{ wch: 10 }, { wch: 45 }, { wch: 14 }, { wch: 8 }, { wch: 22 }, { wch: 22 }, { wch: 16 }, { wch: 48 }];
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Reuniões validadas');
    XLSX.writeFile(wb, nome + '.xlsx');
    return;
  }
  const csv = '\ufeff' + linhas.map(l => l.map(v => '"' + String(v).replace(/"/g, '""') + '"').join(';')).join('\r\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  a.download = nome + '.csv';
  document.body.appendChild(a); a.click(); a.remove();
}

// quando muda o mes, invalida a auditoria carregada
$('f-mes').addEventListener('change', () => { AUD_CARREGADA_MES = null; if (ABA === 'auditoria') carregaAuditoria(true); });

atualizaAuthUI();
init();
</script>
</body>
</html>
"""
