"""HTTP client for a locally deployed mat-gram / SMI-TED MAX serve API.

Default base URL: ``http://127.0.0.1:8080`` (override with ``MATGRAM_API_URL``).

Docs: https://github.com/alix559/material-grammar/tree/main/max_ports
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import httpx

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

if load_dotenv is not None:
    _repo = Path(__file__).resolve().parents[1]
    if (_repo / ".env").is_file():
        load_dotenv(_repo / ".env", override=False)

DEFAULT_API_URL = "http://127.0.0.1:8080"
DEFAULT_TIMEOUT = float(os.environ.get("MATGRAM_TIMEOUT", "120"))

# Organic-ish SMILES candidates (space/comma separated in free text).
_SMILES_TOKEN = re.compile(
    r"(?<![A-Za-z0-9_/])("
    r"(?:Br|Cl|Si|Se|Na|Li|Mg|Zn|Fe|Cu|B|C|N|O|P|S|F|I|H|"
    r"[cnops]|[=#+\-\(\)\[\]\\/@%0-9]){2,}"
    r")(?![A-Za-z0-9_/])"
)

DEFAULT_SMILES = [
    "CCO",
    "c1ccccc1",
    "CC(=O)O",
    "CCN",
    "CC(C)O",
    "c1ccc(O)cc1",
    "CC(=O)Nc1ccc(O)cc1",
    "CCOC(=O)C",
    "CCCC",
    "c1ccncc1",
]

# Rough aqueous solubility labels (log10 mol/L) for parity demos when the
# serve API is in property mode and the user message has no labels.
ESOL_DEMO: dict[str, float] = {
    "CCO": -0.77,
    "c1ccccc1": -1.64,
    "CC(=O)O": 0.22,
    "CCN": 0.43,
    "CC(C)O": -0.39,
    "c1ccc(O)cc1": -0.04,
    "CCCC": -3.18,
    "c1ccncc1": 0.46,
}


class MatgramError(RuntimeError):
    """Raised when the mat-gram HTTP API is unreachable or returns an error."""


def api_base() -> str:
    return (os.environ.get("MATGRAM_API_URL") or DEFAULT_API_URL).rstrip("/")


def extract_smiles(message: str | None, *, min_count: int = 1) -> list[str]:
    """Pull SMILES strings from a free-text message, else fall back to defaults."""
    text = (message or "").strip()
    found: list[str] = []
    if text:
        for m in _SMILES_TOKEN.finditer(text):
            tok = m.group(1).strip(".,;:")
            if tok not in found and any(c.isalpha() for c in tok):
                found.append(tok)
    if len(found) >= min_count:
        return found
    return list(DEFAULT_SMILES)


def extract_labeled_pairs(message: str | None) -> list[tuple[str, float]]:
    """Parse ``SMILES:value`` or ``SMILES=value`` pairs from a message."""
    text = (message or "").strip()
    if not text:
        return []
    pairs: list[tuple[str, float]] = []
    for m in re.finditer(
        r"([A-Za-z0-9@+\-\[\]\(\)=#\\/%]+)\s*[:=]\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)",
        text,
    ):
        smiles, val = m.group(1), m.group(2)
        if any(c.isalpha() for c in smiles):
            pairs.append((smiles, float(val)))
    return pairs


def _raise_for_api(r: httpx.Response) -> dict[str, Any]:
    try:
        data = r.json()
    except Exception as exc:
        raise MatgramError(f"mat-gram returned non-JSON ({r.status_code})") from exc
    if r.status_code >= 400:
        detail = data.get("error") if isinstance(data, dict) else data
        raise MatgramError(f"mat-gram HTTP {r.status_code}: {detail}")
    if not isinstance(data, dict):
        raise MatgramError("mat-gram response must be a JSON object")
    return data


DEFAULT_WEIGHT_PATH = "./model_assets/ibm-research_materials.smi-ted"
DEFAULT_ESOL_CHECKPOINT = (
    "finetune_ckpts/esol/"
    "smi-ted-Light-Finetune_seed0_esol_epoch=3_valloss=0.7972.pt"
)


def status(*, base_url: str | None = None, timeout: float = DEFAULT_TIMEOUT) -> dict[str, Any]:
    url = f"{(base_url or api_base())}/status"
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.get(url)
            return _raise_for_api(r)
    except httpx.HTTPError as exc:
        raise MatgramError(f"mat-gram unreachable at {url}: {exc}") from exc


def load(
    *,
    weight_path: str | None = None,
    checkpoint: str | None = None,
    task: str | None = None,
    device: str = "cpu",
    base_url: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """POST /load — start MAX with pretrained weights or a finetune checkpoint."""
    url = f"{(base_url or api_base())}/load"
    body: dict[str, Any] = {"device": device}
    if weight_path:
        body["weight_path"] = weight_path
    if checkpoint:
        body["checkpoint"] = checkpoint
    if task:
        body["task"] = task
    try:
        with httpx.Client(timeout=max(timeout, 180.0)) as client:
            r = client.post(url, json=body)
            return _raise_for_api(r)
    except httpx.HTTPError as exc:
        raise MatgramError(f"mat-gram /load failed: {exc}") from exc


def stop(*, base_url: str | None = None, timeout: float = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """POST /stop — tear down the MAX serve subprocess."""
    url = f"{(base_url or api_base())}/stop"
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url)
            return _raise_for_api(r)
    except httpx.HTTPError as exc:
        raise MatgramError(f"mat-gram /stop failed: {exc}") from exc


def parse_load_request(message: str | None) -> dict[str, Any]:
    """Parse free text into a /load body.

    Examples:
      weight_path=./model_assets/ibm-research_materials.smi-ted
      checkpoint=finetune_ckpts/esol/foo.pt task=esol device=cpu
      pretrained | esol | stop
    """
    text = (message or "").strip()
    lower = text.lower()
    out: dict[str, Any] = {"device": "cpu"}

    m_dev = re.search(r"\bdevice\s*[:=]\s*(cpu|gpu)\b", text, re.I)
    if m_dev:
        out["device"] = m_dev.group(1).lower()

    m_wp = re.search(r"\bweight(?:_path)?\s*[:=]\s*(\S+)", text, re.I)
    m_ckpt = re.search(r"\bcheckpoint\s*[:=]\s*(\S+)", text, re.I)
    m_task = re.search(r"\btask\s*[:=]\s*(esol|bbbp|lipo)\b", text, re.I)

    if m_wp:
        out["weight_path"] = m_wp.group(1).strip("\"'")
    if m_ckpt:
        out["checkpoint"] = m_ckpt.group(1).strip("\"'")
    if m_task:
        out["task"] = m_task.group(1).lower()

    if "weight_path" not in out and "checkpoint" not in out:
        if re.search(r"\b(esol|bbbp|lipo)\b", lower):
            task = re.search(r"\b(esol|bbbp|lipo)\b", lower).group(1)
            out["task"] = task
            if task == "esol":
                out["checkpoint"] = DEFAULT_ESOL_CHECKPOINT
            else:
                out["checkpoint"] = f"finetune_ckpts/{task}/"
        elif re.search(r"\b(pretrained|embedding|smi-ted|default)\b", lower) or not text:
            out["weight_path"] = DEFAULT_WEIGHT_PATH

    return out


def embeddings(
    smiles: list[str] | str,
    *,
    base_url: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """POST /embeddings → ``{embeddings, predictions?, mode, task, model}``."""
    url = f"{(base_url or api_base())}/embeddings"
    payload = {"smiles": smiles}
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json=payload)
            return _raise_for_api(r)
    except httpx.HTTPError as exc:
        raise MatgramError(f"mat-gram /embeddings failed: {exc}") from exc


def decode(
    vectors: list[list[float]],
    *,
    base_url: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """POST /decode → ``{smiles, token_ids, model}``."""
    url = f"{(base_url or api_base())}/decode"
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json={"embeddings": vectors})
            return _raise_for_api(r)
    except httpx.HTTPError as exc:
        raise MatgramError(f"mat-gram /decode failed: {exc}") from exc


def roundtrip(
    smiles: list[str] | str,
    *,
    base_url: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """POST /roundtrip → encode then decode."""
    url = f"{(base_url or api_base())}/roundtrip"
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json={"smiles": smiles})
            return _raise_for_api(r)
    except httpx.HTTPError as exc:
        raise MatgramError(f"mat-gram /roundtrip failed: {exc}") from exc
