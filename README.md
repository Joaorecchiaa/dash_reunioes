# Dashboard de Reuniões — Closers (Board Academy)

Dashboard que lê as atividades de reunião do Pipedrive e mostra, por closer e por time,
quantas reuniões foram **planejadas**, **feitas**, deram **no-show** e foram **reagendadas** —
dia a dia e no total do mês.

## Como funciona

- **Fonte dos closers:** planilha de colaboradores (Google Sheets publicado em CSV).
  Colunas usadas: `Nome`, `Subarea` (time), `Cargo` (só quem começa com "Closer"),
  `Mês Referencia` e `Ano Referencia`. `MGM` é tratado como `OLYMPUS`.
  Times considerados: **SNIPER**, **OLYMPUS**, **ELITE**.
- **Fonte das reuniões:** Pipedrive API v2 (`/activities`), filtrando os tipos:
  - `meeting` → Reunião
  - `no_show` → No Show
  - `nao_se_aplica` → usado internamente como Reagendamento

  Só entram atividades com `deal_id` preenchido.
- **Regra de contagem:**
  - **Planejadas** = soma dos 3 tipos (toda reunião marcada, qualquer desfecho)
  - **Feitas** = `type = meeting` **e** `done = true`
  - **No Show** = `type = no_show`
  - **Reagendadas** = `type = nao_se_aplica`

Todas as chamadas ao Pipedrive são **GET** — o dashboard nunca altera nada no CRM.

## Estrutura

```
├── api/
│   ├── index.py             # Flask (API + servidor local)
│   └── pipedrive_client.py  # cliente da API do Pipedrive
├── public/
│   └── index.html           # front-end (estático)
├── vercel.json
├── requirements.txt
├── .env                     # NÃO versionado
└── .env.example
```

## Rodar localmente

1. Copie `.env.example` para `.env` e preencha as variáveis:

```
PIPEDRIVE_DOMAIN=boardacademy.pipedrive.com
PIPEDRIVE_API_TOKEN=seu_token
COLABORADORES_CSV_URL="https://docs.google.com/.../pub?gid=...&single=true&output=csv"
REFRESH_SECONDS=1200
```

2. Instale e rode:

```bash
pip install -r requirements.txt
python api/index.py
```

3. Abra http://localhost:5000

Rodando local, uma thread de fundo reconstrói o mês atual a cada 20 minutos.

## Deploy no Vercel

1. Suba o repositório no GitHub (confira que o `.env` **não** foi junto).
2. No Vercel: **Add New → Project → Import Git Repository**.
3. Em **Environment Variables**, cadastre:
   - `PIPEDRIVE_DOMAIN`
   - `PIPEDRIVE_API_TOKEN`
   - `COLABORADORES_CSV_URL`
   - `REFRESH_SECONDS` (opcional, padrão 1200)
4. **Deploy**.

### Diferenças no Vercel

O Vercel é **serverless**: não existe processo de fundo. A thread de refresh não roda lá —
quem mantém a tela atualizada é o próprio navegador, que refaz a chamada a cada 20 minutos
(só quando a visão é *mês atual + Time "Todos" + Closer "Todos"*).

**Timeout:** no plano Hobby a função é cortada em ~10s. Se a busca de todos os closers passar
disso, a saída é o plano Pro (60s) ou reduzir o número de closers por consulta usando o filtro.

**Acesso:** por padrão a URL do Vercel é pública. Como o dashboard expõe dados comerciais,
ative alguma proteção (Vercel Authentication / SSO) nas configurações do projeto.

## Manutenção

- **Novo closer / mudança de time:** basta atualizar a planilha de colaboradores. O dashboard
  lê o mês/ano de referência, então o histórico fica correto mês a mês.
- **Nome sem correspondência:** se o nome na planilha não bater com o usuário do Pipedrive,
  aparece um aviso no rodapé do dashboard listando quem não foi encontrado.
