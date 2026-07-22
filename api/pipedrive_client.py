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
        """Pagina por cursor no v2/activities; mantem tipos meeting/no_show/nao_se_aplica
        com deal_id preenchido (v2 nao filtra type/due_date, filtramos aqui)."""
        tipos = {"meeting", "no_show", "nao_se_aplica"}
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
        """{deal_id: {"pipeline_id": int, "title": str}}, em lotes de 100."""
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
            out[d["id"]] = {
                "pipeline_id": d.get("pipeline_id"),
                "title": d.get("title") or f"Negocio {d.get('id')}",
            }
        return out
