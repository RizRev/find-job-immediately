"""
JobSpy + Telegram notifier — dijalankan otomatis via GitHub Actions.

Cara kerja:
1. Scrape lowongan terbaru pakai JobSpy.
2. Bandingkan dengan seen_jobs.json (lowongan yang sudah pernah dikirim).
3. Kirim notifikasi Telegram HANYA untuk lowongan baru.
4. Update seen_jobs.json (nanti di-commit balik ke repo oleh workflow).
"""

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from jobspy import scrape_jobs

load_dotenv()  # baca file .env kalau ada (local dev). Di GitHub Actions, .env gak ada — otomatis skip, tetap pakai secrets.

# --- Ubah sesuai kebutuhan ---
SEARCH_TERMS = ["frontend", "next", "react", "vue", "javascript", "full stack developer", "backend developer", "react developer"]
LOCATION = "Jakarta, Indonesia"
LINKEDIN_RESULTS = 50    # LinkedIn paling ketat rate-limitnya, jaga di bawah ~10 halaman
OTHER_RESULTS = 100      # Indeed & Google jauh lebih longgar
HOURS_OLD = 12 + 2       # run tiap 12 jam, tambah buffer 2 jam biar gak ada yang kelewat
SEEN_FILE = Path("seen_jobs.json")
# -------------------------------

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def load_seen() -> set[str]:
    if SEEN_FILE.exists():
        return set(json.loads(SEEN_FILE.read_text()))
    return set()


def save_seen(seen: set[str]) -> None:
    SEEN_FILE.write_text(json.dumps(sorted(seen), indent=2))


def send_telegram(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    resp = requests.post(
        url,
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        },
        timeout=15,
    )
    resp.raise_for_status()


def scrape_site(site: str, term: str):
    """Scrape satu situs untuk satu search term. Return DataFrame kosong kalau gagal (misal kena 429)."""
    import pandas as pd

    results_wanted = LINKEDIN_RESULTS if site == "linkedin" else OTHER_RESULTS
    try:
        df = scrape_jobs(
            site_name=[site],
            search_term=term,
            google_search_term=f"{term} jobs near {LOCATION} since last 12 hours",
            location=LOCATION,
            results_wanted=results_wanted,
            hours_old=HOURS_OLD,
            country_indeed="Indonesia",
            linkedin_fetch_description=False,
        )
        print(f"[OK] {site:10s} | '{term}' -> {len(df)} hasil")
        return df
    except Exception as e:
        print(f"[WARN] Gagal scrape {site} untuk '{term}': {e}")
        return pd.DataFrame()


def main() -> None:
    seen = load_seen()
    all_jobs = []

    for term in SEARCH_TERMS:
        for site in ["indeed", "linkedin", "google"]:
            all_jobs.append(scrape_site(site, term))

    import pandas as pd

    combined = pd.concat(all_jobs, ignore_index=True)
    if combined.empty:
        print("Semua situs gagal atau tidak ada hasil. Cek log di atas.")
        return
    combined = combined.drop_duplicates(subset=["job_url"])

    print("\n--- Breakdown per situs (setelah dedupe) ---")
    print(combined["site"].value_counts().to_string())
    print("---\n")

    new_jobs = combined[~combined["job_url"].isin(seen)]

    print(f"Total lowongan ditemukan: {len(combined)}")
    print(f"Lowongan baru: {len(new_jobs)}")

    for _, job in new_jobs.iterrows():
        title = job.get("title", "N/A")
        company = job.get("company", "N/A")
        loc = job.get("location", "N/A")
        url = job.get("job_url", "")
        site = job.get("site", "")

        message = (
            f"🆕 <b>{title}</b>\n"
            f"🏢 {company}\n"
            f"📍 {loc}\n"
            f"🔗 <a href='{url}'>Lihat lowongan ({site})</a>"
        )
        send_telegram(message)
        seen.add(url)

    save_seen(seen)

    if len(new_jobs) == 0:
        print("Tidak ada lowongan baru hari ini.")


if __name__ == "__main__":
    main()