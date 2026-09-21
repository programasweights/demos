"""Register a trained adapter as a public PAW program. Requires PAW_API_KEY or paw login."""
import argparse
import hashlib
import json
from pathlib import Path

import httpx
from programasweights import get_api_key


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    args = parser.parse_args()
    key = get_api_key()
    if not key:
        parser.error("Set PAW_API_KEY or run paw login before uploading.")
    path = args.checkpoint
    names = ["manifest.json", "adapter_config.json", "adapter_model.safetensors"]
    hashes = {}
    for name in names:
        digest = hashlib.sha256()
        with (path / name).open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        hashes[name] = digest.hexdigest()
    receipt = path / "upload.json"
    state = json.loads(receipt.read_text()) if receipt.exists() else dict(files=hashes)
    if state["files"] != hashes:
        raise ValueError("Adapter files changed since upload; use a new checkpoint directory.")
    if state.get("program_id"):
        print(state["program_id"])
        return
    with httpx.Client(base_url="https://programasweights.com/api/v1/", headers={"X-API-Key": key}, timeout=310) as client:
        def request(method, url, **kwargs):
            response = client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()

        status = None
        if state.get("upload_id"):
            response = client.get(f"program-imports/{state['upload_id']}")
            if response.status_code not in (404, 410):
                response.raise_for_status()
                status = response.json()
        if status is None:
            body = dict(manifest=json.loads((path / names[0]).read_text()), adapter_config=json.loads((path / names[1]).read_text()))
            status = request("POST", "program-imports", json=body)
            state["upload_id"] = status["upload_id"]
            receipt.write_text(json.dumps(state, indent=2) + "\n")
        url = f"program-imports/{state['upload_id']}"
        if status["status"] == "awaiting_upload":
            with (path / names[2]).open("rb") as weights:
                request("PUT", url + "/weights", content=weights, headers={"Content-Type": "application/octet-stream"})
        validated = request("POST", url + "/validate")
        registered = request("POST", url + "/register", json={"public": True})
        if validated["program_id"] != registered["program_id"]:
            raise ValueError("Registered ID differs from the validated program.")
        state["program_id"] = registered["program_id"]
        receipt.write_text(json.dumps(state, indent=2) + "\n")
        print(state["program_id"])


if __name__ == "__main__":
    main()
