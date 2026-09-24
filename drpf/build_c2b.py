"""Rebuild the C2B non-speech clips from DEMAND using data/manifests/c2b_demand.csv.

Downloads the five 16 kHz scene archives from Zenodo record 1227121, checks
their SHA-256, extracts channel 01 and cuts each clip at the listed offset.

    python drpf/build_c2b.py
    python drpf/build_c2b.py --cache-dir D:/demand_cache
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import zipfile
from pathlib import Path
from urllib.request import Request, urlopen

import soundfile as sf

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "data" / "manifests" / "c2b_demand.csv"
ZENODO_FILES = "https://zenodo.org/records/1227121/files"
SAMPLE_RATE = 16000

SHA256 = {
    "DLIVING": "2b1726fe06e41551ce2397f2aaf3e4fb692c912d81914b04708df0bbb5252338",
    "OHALLWAY": "4d5ef858a05954f03340048131f60a2004b7b28afc65f7bd2301636a7002d6cb",
    "OOFFICE": "7570c952f621990d0d71b8398107d9a78066254f883a5569abec9c233ffda358",
    "PCAFETER": "89be7194b83cd583c4b12f4bf7c19e9cf0e612b95312e9f4aedc968cd811bcd5",
    "PRESTO": "cfd2e13998fac36aa5628070e08261deb7993dada302dc00a76aaf4e02ee4166",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_scene(scene: str, cache_dir: Path) -> Path:
    zip_path = cache_dir / f"{scene}_16k.zip"
    if not zip_path.exists() or zip_path.stat().st_size == 0:
        cache_dir.mkdir(parents=True, exist_ok=True)
        url = f"{ZENODO_FILES}/{scene}_16k.zip?download=1"
        print(f"download {url}")
        req = Request(url, headers={"User-Agent": "DRPF-rocling2026"})
        with urlopen(req, timeout=300) as resp:
            zip_path.write_bytes(resp.read())
    digest = sha256(zip_path)
    if digest != SHA256[scene]:
        raise SystemExit(f"{zip_path.name}: SHA-256 {digest} does not match {SHA256[scene]}")
    return zip_path


def extract_ch01(zip_path: Path, out_dir: Path) -> Path:
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".wav")]
        preferred = [n for n in names if "ch01" in Path(n).stem.lower()]
        if not preferred:
            raise SystemExit(f"No ch01 wav in {zip_path.name}")
        pick = sorted(preferred)[0]
        target = out_dir / Path(pick).name
        if not target.exists():
            out_dir.mkdir(parents=True, exist_ok=True)
            with zf.open(pick) as src, target.open("wb") as dst:
                dst.write(src.read())
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--cache-dir", type=Path, default=REPO_ROOT / ".cache" / "demand")
    args = parser.parse_args()

    with MANIFEST.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    sources: dict[str, tuple] = {}
    for row in rows:
        scene = row["source_scene"]
        if scene not in sources:
            ch01 = extract_ch01(fetch_scene(scene, args.cache_dir), args.cache_dir / scene)
            audio, sr = sf.read(str(ch01), always_2d=False)
            if sr != SAMPLE_RATE:
                raise SystemExit(f"{ch01}: expected {SAMPLE_RATE} Hz, got {sr}")
            if audio.ndim > 1:
                audio = audio[:, 0]
            sources[scene] = audio
        audio = sources[scene]
        start = round(float(row["start_sec"]) * SAMPLE_RATE)
        length = round(float(row["duration_sec"]) * SAMPLE_RATE)
        out = REPO_ROOT / row["audio_path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        sf.write(str(out), audio[start : start + length].astype("float32"), SAMPLE_RATE)

    print(f"wrote {len(rows)} clips under {REPO_ROOT / 'data' / 'c2b' / 'audio'}")


if __name__ == "__main__":
    main()
