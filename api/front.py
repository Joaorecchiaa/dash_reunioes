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
<style>
  :root {
    --bg:#000000; --card:#0d0d0d; --card2:#161616; --border:#2a2a2a;
    --text:#f2f2f2; --muted:#9a9a9a;
    --gold:#FFD700; --gold-ink:#FFD700; --gold-soft:rgba(255,215,0,.12);
    --done:#37d399; --nsw:#f97066; --reag:#f5b544;
  }
  * { box-sizing:border-box; }
  body { font-family:'Segoe UI',Arial,sans-serif; background:var(--bg); color:var(--text); margin:0; padding:24px; }

  .brand { font-size:13px; font-weight:800; letter-spacing:3px; color:var(--gold-ink); text-transform:uppercase; margin-bottom:4px; }
  .brand::after { content:''; display:block; width:52px; height:3px; background:var(--gold); margin-top:5px; border-radius:2px; }
  h1 { font-size:24px; margin:12px 0 18px; font-weight:700; letter-spacing:1px; color:var(--text); }
  h1 .sep { color:var(--gold-ink); }

  .filters { display:flex; gap:12px; align-items:flex-end; flex-wrap:wrap; background:var(--card);
             border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:20px;
             box-shadow:none; }
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
  .updated { color:var(--muted); font-size:12px; margin-left:auto; align-self:center; text-align:right; }
  .auto { color:var(--gold-ink); font-size:11px; }

  .kpi-head { font-size:13px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; margin:0 0 8px; font-weight:600; }
  .kpis { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px; }
  .kpi { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:14px 20px; min-width:130px;
         box-shadow:none; }
  .kpi.plan { border-color:var(--gold); background:var(--gold-soft); }
  .kpi .lbl { font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; }
  .kpi .val { font-size:30px; font-weight:800; line-height:1.1; }
  .kpi.plan .val{color:var(--gold-ink);} .kpi.done .val{color:var(--done);}
  .kpi.nsw .val{color:var(--nsw);} .kpi.reag .val{color:var(--reag);}

  .month-strip { display:flex; gap:16px; flex-wrap:wrap; align-items:center; background:var(--card);
                 border:1px solid var(--border); border-left:4px solid var(--gold); border-radius:10px;
                 padding:10px 16px; margin-bottom:20px; font-size:13px; box-shadow:none; }
  .month-strip .ms-title { color:var(--gold-ink); text-transform:uppercase; letter-spacing:.5px; font-size:11px; font-weight:700; }
  .month-strip .ms-item b { font-weight:700; }

  /* cards de time */
  .team-cards { display:flex; gap:14px; flex-wrap:wrap; margin-bottom:22px; }
  .team-card { background:var(--card); border:1px solid var(--border); border-left:4px solid var(--gold);
               border-radius:12px; padding:14px 18px; min-width:290px; box-shadow:none; }
  .team-card .tc-name { font-size:15px; font-weight:800; letter-spacing:1px; color:var(--gold-ink); margin-bottom:10px; }
  .team-card .tc-row { display:flex; align-items:baseline; gap:10px; padding:5px 0; font-size:13px; flex-wrap:wrap; }
  .team-card .tc-row + .tc-row { border-top:1px dashed var(--border); }
  .team-card .tc-lbl { font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px; min-width:78px; font-weight:700; }
  .team-card .tc-big { font-size:20px; font-weight:800; color:var(--gold-ink); }
  .team-card .tc-sub { color:var(--muted); }

  .panel { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; margin-bottom:20px;
           box-shadow:none; }
  .panel h2 { font-size:14px; margin:0 0 12px; color:var(--gold-ink); text-transform:uppercase; letter-spacing:.5px; font-weight:700; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th, td { padding:7px 10px; text-align:center; border-bottom:1px solid var(--border); }
  th { color:var(--muted); font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:.5px; }
  td.l, th.l { text-align:left; }
  tr.total td { font-weight:800; border-top:2px solid var(--gold); background:var(--gold-soft); color:var(--gold-ink); }
  tr.today td { background:var(--gold-soft); }
  .c-plan{color:var(--gold-ink); font-weight:800;} .c-done{color:var(--done);} .c-nsw{color:var(--nsw);} .c-reag{color:var(--reag);}
  .warn { color:var(--nsw); font-size:12px; margin-bottom:16px; }
  .muted { color:var(--muted); }

  .matrix-wrap { overflow-x:auto; }
  table.matrix { border-collapse:collapse; font-size:12px; white-space:nowrap; min-width:100%; }
  table.matrix th, table.matrix td { padding:8px 12px; border-bottom:1px solid var(--border); text-align:center; }
  table.matrix th.closer, table.matrix td.closer { position:sticky; left:0; background:var(--card); text-align:left; z-index:2; min-width:150px; font-weight:600; }
  table.matrix th.team, table.matrix td.team { text-align:left; color:var(--muted); }
  table.matrix td, table.matrix th { border-left:1px solid #1e1e1e; }
  table.matrix thead tr.grp th.grp-day, table.matrix thead tr.grp th.grp-tot {
    border-bottom:1px solid var(--border); border-left:1px solid var(--border);
    color:var(--gold-ink); font-size:11px; letter-spacing:.5px; background:var(--card2); }
  table.matrix thead tr.grp th.today { background:var(--gold-soft); }
  table.matrix tr.sub th { font-size:10px; padding:4px 8px; }
  table.matrix th.today, table.matrix td.today { background:var(--gold-soft); }
  table.matrix .mtot { border-left:2px solid var(--gold) !important; }
  table.matrix tr.foot td { border-top:2px solid var(--gold); background:var(--gold-soft); font-weight:800; }
  table.matrix tr.foot td.closer { background:var(--gold-soft); }
  table.matrix tbody tr:hover td, table.matrix tbody tr:hover td.closer { background:#1a1a1a; }

  /* drill-down por closer */
  table.matrix td.closer .cl-link { color:var(--gold); cursor:pointer; text-decoration:underline dotted;
                                    text-underline-offset:3px; user-select:none; }
  table.matrix td.closer .cl-link:hover { text-decoration:underline; }
  table.matrix td.closer .cl-arrow { color:var(--muted); font-size:10px; margin-right:4px; }
  tr.drill > td { background:#080808 !important; padding:0 !important; }
  .drill-box { padding:14px 18px; white-space:normal; }
  .drill-box h3 { font-size:12px; color:var(--gold); margin:0 0 10px; text-transform:uppercase; letter-spacing:.5px; }
  table.drill-tbl { width:100%; font-size:12px; border-collapse:collapse; }
  table.drill-tbl th { font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:.5px;
                       padding:5px 10px; border-bottom:1px solid var(--border); text-align:left; }
  table.drill-tbl td { padding:6px 10px; border-bottom:1px solid #1a1a1a; text-align:left; }
  table.drill-tbl a { color:var(--gold); text-decoration:none; }
  table.drill-tbl a:hover { text-decoration:underline; }
  table.drill-tbl tr:hover td { background:#111; }
  .badge { font-size:10px; padding:2px 9px; border-radius:999px; border:1px solid var(--border); white-space:nowrap; }
  .badge.feita { color:var(--done); border-color:var(--done); }
  .badge.no_show { color:var(--nsw); border-color:var(--nsw); }
  .badge.reagendada { color:var(--reag); border-color:var(--reag); }
  .badge.pendente { color:var(--muted); }

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
  <div class="brand">BOARD ACADEMY</div>
  <h1>REUNIÕES <span class="sep">-</span> CLOSERS</h1>

  <div class="filters">
    <div class="field"><label>Mês</label><select id="f-mes"></select></div>
    <div class="field"><label>Dia</label><select id="f-dia"></select></div>
    <div class="field"><label>Time</label><select id="f-time"></select></div>
    <div class="field"><label>Closer</label><select id="f-closer"></select></div>
    <button id="btn">Pesquisar</button>
    <div class="updated"><div id="updated"></div><div class="auto" id="auto"></div></div>
  </div>

  <div id="root"><div class="muted">Carregando filtros…</div></div>

<script>
const $ = id => document.getElementById(id);
const hoje = new Date();
const diaHojeNum = hoje.getDate();
let CURRENT_MONTH = null;
let REFRESH_MS = 1200000;
let LAST_DATA = null;

function opt(sel, arr, getV, getL) {
  sel.innerHTML = '';
  for (const item of arr) {
    const o = document.createElement('option');
    o.value = getV(item); o.textContent = getL(item);
    sel.appendChild(o);
  }
}

function ehDefaultAtual() {
  return $('f-mes').value === CURRENT_MONTH
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
  const d = await (await fetch('/api/init')).json();
  CURRENT_MONTH = d.current;
  REFRESH_MS = (d.refresh_seconds || 1200) * 1000;
  opt($('f-mes'), d.months, x=>x.value, x=>x.label);
  $('f-mes').value = d.current;
  opt($('f-time'), d.teams, x=>x, x=>x);
  preencheDias();
  await carregaClosers();
  buscar(false);
  setInterval(() => { if (ehDefaultAtual()) buscar(true); }, REFRESH_MS);
}

async function carregaClosers() {
  const d = await (await fetch('/api/closers?month=' + $('f-mes').value)).json();
  opt($('f-closer'), d.closers, x=>x, x=>x);
}

$('f-mes').addEventListener('change', async () => { preencheDias(); await carregaClosers(); });
// dia e so recorte visual: re-renderiza na hora, sem nova requisicao
$('f-dia').addEventListener('change', () => { if (LAST_DATA) render(LAST_DATA); });
$('btn').addEventListener('click', () => buscar(false));

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
    const res = await fetch('/api/dashboard?' + p.toString());
    const data = await res.json();
    if (data.error) $('root').innerHTML = '<div class="warn">Erro: ' + data.error + '</div>';
    else { LAST_DATA = data; render(data); }
  } catch (e) {
    if (!isAuto) $('root').innerHTML = '<div class="warn">Falha na requisição: ' + e + '</div>';
  } finally {
    $('btn').disabled = false;
  }
}

function cols(c) {
  return `<td class="c-plan">${c.planned}</td><td class="c-done">${c.done}</td>`
       + `<td class="c-nsw">${c.no_show}</td><td class="c-reag">${c.reagendada}</td>`;
}

function render(data) {
  $('updated').innerText = 'Atualizado: ' + new Date(data.generated_at).toLocaleString('pt-BR');
  $('auto').innerText = ehDefaultAtual() ? '● atualiza sozinho a cada ' + Math.round(REFRESH_MS/60000) + ' min' : '';
  const mt = data.month_total;
  const nDays = data.days.length;
  const dSel = Math.min(diaSelecionado() || 1, nDays);
  const dSelStr = String(dSel).padStart(2,'0');
  const mesStr = String(data.month).padStart(2,'0');
  const zero = {planned:0, done:0, no_show:0, reagendada:0};
  const getDia = (lista, n) => { const r = (lista||[]).find(x => x.dia === n); return r ? r.counter : null; };

  const tresDias = [];
  if (dSel - 1 >= 1)      tresDias.push({n: dSel-1, rot: 'Anterior'});
  tresDias.push({n: dSel, rot: 'Dia ' + dSelStr});
  if (dSel + 1 <= nDays)  tresDias.push({n: dSel+1, rot: 'Seguinte'});

  const quatro = c => `<td class="c-plan">${c.planned}</td><td class="c-done">${c.done}</td>`
                    + `<td class="c-nsw">${c.no_show}</td><td class="c-reag">${c.reagendada}</td>`;
  const subHead = extra => `<th class="c-plan${extra||''}">P</th><th class="c-done">F</th><th class="c-nsw">NS</th><th class="c-reag">R</th>`;

  const diaCounter = getDia(data.days, dSel) || zero;

  let html = '';

  html += `<div class="kpi-head">Dia ${dSelStr}/${mesStr}</div>`;
  html += `<div class="kpis">
    <div class="kpi plan"><div class="lbl">Planejadas</div><div class="val">${diaCounter.planned}</div></div>
    <div class="kpi done"><div class="lbl">Feitas</div><div class="val">${diaCounter.done}</div></div>
    <div class="kpi nsw"><div class="lbl">No Show</div><div class="val">${diaCounter.no_show}</div></div>
    <div class="kpi reag"><div class="lbl">Reagendadas</div><div class="val">${diaCounter.reagendada}</div></div>
  </div>`;

  html += `<div class="month-strip">
    <span class="ms-title">Total do mês — ${data.month_label}</span>
    <span class="ms-item c-plan">Planejadas <b>${mt.planned}</b></span>
    <span class="ms-item c-done">Feitas <b>${mt.done}</b></span>
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
          <span class="tc-sub">plan · <span class="c-done">${cd.done}</span> feitas · <span class="c-nsw">${cd.no_show}</span> NS · <span class="c-reag">${cd.reagendada}</span> reag</span>
        </div>
        <div class="tc-row">
          <span class="tc-lbl">Total mês</span>
          <span class="tc-big">${cm.planned}</span>
          <span class="tc-sub">plan · <span class="c-done">${cm.done}</span> feitas · <span class="c-nsw">${cm.no_show}</span> NS · <span class="c-reag">${cm.reagendada}</span> reag</span>
        </div>
      </div>`;
    }
    html += '</div>';
  }

  if (data.por_closer.length) {
    html += `<div class="panel"><h2>Por closer</h2><div class="matrix-wrap"><table class="matrix">`;
    html += `<thead><tr class="grp">
      <th class="closer l" rowspan="2">Closer</th><th class="team l" rowspan="2">Time</th>`;
    for (const d of tresDias) {
      const cls = (d.n === dSel) ? ' today' : '';
      html += `<th colspan="4" class="grp-day${cls}">${d.rot} <span class="muted">${String(d.n).padStart(2,'0')}</span></th>`;
    }
    html += `<th colspan="4" class="grp-tot mtot">Total do mês</th></tr>`;
    html += `<tr class="sub">`;
    for (const d of tresDias) html += subHead((d.n === dSel) ? ' today' : '');
    html += `<th class="c-plan mtot">P</th><th class="c-done">F</th><th class="c-nsw">NS</th><th class="c-reag">R</th>`;
    html += `</tr></thead><tbody>`;

    const nCols = 2 + tresDias.length * 4 + 4;
    data.por_closer.forEach((c, i) => {
      const cid = 'drill-' + i;
      html += `<tr><td class="closer l"><span class="cl-link" data-drill="${cid}"><span class="cl-arrow" id="${cid}-arw">&#9656;</span>${c.name}</span></td><td class="team l">${c.time}</td>`;
      for (const d of tresDias) html += quatro(getDia(c.days, d.n) || zero);
      const t = c.total;
      html += `<td class="c-plan mtot">${t.planned}</td><td class="c-done">${t.done}</td><td class="c-nsw">${t.no_show}</td><td class="c-reag">${t.reagendada}</td></tr>`;

      // linha oculta com as reunioes do closer
      let dhtml;
      if (c.meetings && c.meetings.length) {
        dhtml = `<h3>${c.meetings.length} reuniões — ${data.month_label}</h3>
          <table class="drill-tbl"><tr><th>Data</th><th>Negócio</th><th>Funil</th><th>Status</th></tr>`;
        for (const m of c.meetings) {
          const p = m.date.split('-');
          const dt = p[2] + '/' + p[1];
          const hr = m.hora ? ' ' + String(m.hora).slice(0,5) : '';
          dhtml += `<tr>
            <td>${dt}${hr}</td>
            <td><a href="${m.url}" target="_blank" rel="noopener">#${m.deal_id} — ${m.title}</a></td>
            <td class="muted">${m.pipeline}</td>
            <td><span class="badge ${m.status}">${m.status.replace('_',' ')}</span></td></tr>`;
        }
        dhtml += `</table>`;
      } else {
        dhtml = `<div class="muted">Nenhuma reunião no período.</div>`;
      }
      html += `<tr class="drill" id="${cid}" style="display:none"><td colspan="${nCols}"><div class="drill-box">${dhtml}</div></td></tr>`;
    });

    html += `<tr class="foot"><td class="closer l">TOTAL</td><td class="team l"></td>`;
    for (const d of tresDias) html += quatro(getDia(data.days, d.n) || zero);
    html += `<td class="c-plan mtot">${mt.planned}</td><td class="c-done">${mt.done}</td><td class="c-nsw">${mt.no_show}</td><td class="c-reag">${mt.reagendada}</td></tr>`;
    html += `</tbody></table></div>
      <div class="muted" style="font-size:11px;margin-top:8px">P = planejadas · F = feitas · NS = no-show · R = reagendadas</div></div>`;
  }

  html += `<details class="diaria"><summary>Dia a dia — todos os times (${data.month_label})</summary><div class="inner">
    <table><tr><th class="l">Dia</th><th>Planejado</th><th>Feitas</th><th>No Show</th><th>Reagendadas</th></tr>`;
  for (const row of data.days) {
    const cls = (row.dia === dSel) ? ' class="today"' : '';
    html += `<tr${cls}><td class="l">${String(row.dia).padStart(2,'0')}</td>${cols(row.counter)}</tr>`;
  }
  html += `<tr class="total"><td class="l">TOTAL</td>${cols(mt)}</tr></table></div></details>`;

  if (data.nao_encontrados && data.nao_encontrados.length) {
    html += `<div class="warn">⚠ Sem correspondência no Pipedrive: ${data.nao_encontrados.join(', ')}</div>`;
  }

  $('root').innerHTML = html;
  ligaDrills();
}

function ligaDrills() {
  document.querySelectorAll('.cl-link[data-drill]').forEach(el => {
    el.addEventListener('click', () => toggleDrill(el.getAttribute('data-drill')));
  });
}

function toggleDrill(id) {
  const el = document.getElementById(id);
  const arw = document.getElementById(id + '-arw');
  if (!el) return;
  const aberto = el.style.display !== 'none';
  el.style.display = aberto ? 'none' : 'table-row';
  if (arw) arw.innerHTML = aberto ? '&#9656;' : '&#9662;';
}

init();
</script>
</body>
</html>
"""
