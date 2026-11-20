import json
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

WATCHLIST = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA",
    "MC.PA", "TTE.PA", "AIR.PA", "SAN.PA", "BNP.PA", "OR.PA",
]
LOOKBACK_DAYS = 7     # on relit 7 jours pour ne rien rater (week-ends, échecs)
KEEP_DAYS = 120       # historique conservé dans le fichier
OUT = Path("docs/data.json")


def num(v):
    try:
        v = float(v)
        return round(v, 2) if v > 0 else None
    except (TypeError, ValueError):
        return None


def fetch(ticker, since):
    df = yf.Ticker(ticker).upgrades_downgrades
    if df is None or df.empty:
        return []
    df = df.reset_index()
    df["GradeDate"] = pd.to_datetime(df["GradeDate"], utc=True)
    df = df[df["GradeDate"] >= since]
    return [{
        "date":   r["GradeDate"].strftime("%Y-%m-%d"),
        "ticker": ticker,
        "firm":   r.get("Firm") or "",
        "from":   r.get("FromGrade") or "",
        "to":     r.get("ToGrade") or "",
        "action": r.get("Action") or "",
        "target": num(r.get("currentPriceTarget")),
        "prior":  num(r.get("priorPriceTarget")),
    } for _, r in df.iterrows()]


def main():
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=LOOKBACK_DAYS)

    # Charger l'historique existant
    existing = []
    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8")).get("changes", [])
    merged = {f'{c["date"]}|{c["ticker"]}|{c["firm"]}': c for c in existing}

    # Ajouter les nouveautés
    for t in WATCHLIST:
        try:
            for c in fetch(t, since):
                merged[f'{c["date"]}|{c["ticker"]}|{c["firm"]}'] = c
        except Exception as e:
            print(f"[ERREUR] {t}: {e}")
        time.sleep(0.5)

    # Purger les données trop anciennes et trier
    cutoff = (now - timedelta(days=KEEP_DAYS)).strftime("%Y-%m-%d")
    changes = sorted(
        (c for c in merged.values() if c["date"] >= cutoff),
        key=lambda c: (c["date"], c["ticker"]), reverse=True,
    )

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(
        {"updated": now.isoformat(), "changes": changes},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(changes)} recommandations enregistrées.")


if __name__ == "__main__":
    main()
