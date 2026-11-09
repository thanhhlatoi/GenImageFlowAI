"""Client 9router (proxy tuong thich OpenAI). Cau hinh bang .env (thu muc goc du an) hoac bien moi truong:

    ROUTER_URL    mac dinh http://192.168.1.84:20128/v1
    ROUTER_KEY    API key lay trong dashboard 9router (khong ghi vao code)
    ROUTER_MODEL  ten model/combo trong 9router (xem: python3 -m imgtool router)
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


def _load_env():
    """Doc .env o thu muc goc du an (khong ghi de bien moi truong da co)."""
    f = Path(__file__).resolve().parent.parent / ".env"
    if not f.exists():
        return
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip().removeprefix("export "), v.strip().strip("\"'"))


_load_env()
URL = os.environ.get("ROUTER_URL", "http://192.168.1.84:20128/v1").rstrip("/")


class RouterError(RuntimeError):
    pass


def _call(path, body=None, timeout=120):
    key = os.environ.get("ROUTER_KEY")
    if not key:
        raise RouterError("Chua dat ROUTER_KEY (export ROUTER_KEY=sk-... lay tu dashboard 9router)")
    req = urllib.request.Request(
        f"{URL}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RouterError(f"9router tra loi {e.code}: {e.read().decode(errors='replace')[:300]}")
    except urllib.error.URLError as e:
        raise RouterError(f"Khong ket noi duoc {URL}: {e.reason}")


def models():
    return [m["id"] for m in _call("/models").get("data", [])]


def chat(prompt, system=None, model=None, timeout=120):
    model = model or os.environ.get("ROUTER_MODEL")
    if not model:
        raise RouterError("Chua dat ROUTER_MODEL (xem danh sach: python3 -m imgtool router)")
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    data = _call("/chat/completions", {"model": model, "messages": msgs}, timeout)
    return data["choices"][0]["message"]["content"].strip()
