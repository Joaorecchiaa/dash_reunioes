import requests


class PipedriveClient:
    def __init__(self, domain, token):
        self.token = token
        self.base_v2 = f"https://{domain}/api/v2"
        self.base_v1 = f"https://{domain}/api/v1"

    def _get(self, base, path, params=None):
        params = dict(params or {})
        params["api_token"] = self.token
        resp = requests.get(f"{base}{path}", params=params, timeout=30)
        if resp.status_code != 200:
            print(f"[Pipedrive] {resp.status_code} em {path}: {resp.text[:300]}")
            resp.raise_for_status()
        return resp.json()

    def get_users_map(self):
        """{nome_minusculo: user_id} -- usado pra achar o owner_id de cada closer pelo nome."""
        data = self._get(self.base_v1, "/users")
        users = data.get("data") or []
        return {u["name"].strip().lower(): u["id"] for u in users}

    def get_pipelines_map(self):
        """{pipeline_id: nome} -- pra mostrar o nome do funil em vez do numero."""
        data = self._get(self.base_v2, "/pipelines")
        return {p["id"]: p["name"] for p in (data.get("data") or [])}

    def get_meeting_activities(self, owner_id, updated_since=None):
        """Pagina por cursor no v2/activities; mantem tipos meeting/no_show/reagendamento
        com deal_id preenchido (v2 nao filtra type/due_date, filtramos aqui)."""
        tipos = {"meeting", "no_show", "reagendamento"}
        activities = []
        cursor = None
        while True:
            params = {"owner_id": owner_id, "limit": 500}
            if updated_since:
                params["updated_since"] = updated_since
            if cursor:
                params["cursor"] = cursor
            data = self._get(self.base_v2, "/activities", params)
            for a in data.get("data") or []:
                if a.get("type") in tipos and a.get("deal_id"):
                    activities.append(a)
            cursor = (data.get("additional_data") or {}).get("next_cursor")
            if not cursor:
                break
        return activities

    def get_deals_info(self, deal_ids):
        """{deal_id: <objeto do negocio, cru>}, em lotes de 100.
        Mantem o objeto completo do negocio (nao so pipeline_id/title) para
        que campos customizados do negocio -- como "Reuniao Validada?" --
        fiquem disponiveis sem precisar de outra chamada."""
        deal_ids = [d for d in deal_ids if d]
        result = {}
        batch = []
        for deal_id in deal_ids:
            batch.append(str(deal_id))
            if len(batch) == 100:
                result.update(self._fetch_deal_batch(batch))
                batch = []
        if batch:
            result.update(self._fetch_deal_batch(batch))
        return result

    def _fetch_deal_batch(self, ids_batch):
        data = self._get(self.base_v2, "/deals", {"ids": ",".join(ids_batch), "limit": 100})
        out = {}
        for d in data.get("data") or []:
            if not d.get("title"):
                d["title"] = "Negocio " + str(d.get("id"))
            out[d["id"]] = d  # objeto completo: pipeline_id, title, custom_fields, etc.
        return out

    def get_activity_raw(self, activity_id):
        """Busca UMA activity crua (todos os campos), pra diagnostico de
        campos customizados."""
        data = self._get(self.base_v2, f"/activities/{activity_id}", {})
        return data.get("data")

    def get_deal_raw(self, deal_id):
        """Busca UM deal cru (todos os campos), pra diagnostico de campos
        customizados que podem estar no negocio em vez da atividade."""
        data = self._get(self.base_v2, f"/deals/{deal_id}", {})
        return data.get("data")

    def get_deal_field_options(self, field_key):
        """{option_id: label} das opcoes de um campo de selecao do NEGOCIO
        (ex.: campo "Reuniao Validada?"). A API devolve o valor do campo
        como o ID numerico da opcao escolhida -- precisa desse mapa pra
        traduzir pro texto (ex.: 411 -> "Sim").

        IMPORTANTE: o "id" longo do campo (hash tipo 7299bf17...) e na
        verdade o "key" do campo, nao o id numerico interno. Na API v1,
        /dealFields/{id} espera o id NUMERICO (nao o hash) -- por isso
        tem que usar a v2, onde o endpoint aceita o key/hash direto como
        "field_code": GET /v2/dealFields/{field_code}."""
        data = self._get(self.base_v2, f"/dealFields/{field_key}", {})
        campo = data.get("data") or {}
        opcoes = campo.get("options") or []
        return {o["id"]: o["label"] for o in opcoes}

    def get_deals_by_owner(self, owner_id, updated_since=None):
        """Todos os negocios (deals) cujo owner_id (Proprietario) e o
        informado, paginado. Usado pra achar leads recebidos por uma SDR
        (metrica de evolucao por horario)."""
        deals = []
        cursor = None
        while True:
            params = {"owner_id": owner_id, "limit": 100}
            if updated_since:
                params["updated_since"] = updated_since
            if cursor:
                params["cursor"] = cursor
            data = self._get(self.base_v2, "/deals", params)
            for d in data.get("data") or []:
                deals.append(d)
            cursor = (data.get("additional_data") or {}).get("next_cursor")
            if not cursor:
                break
        return deals
