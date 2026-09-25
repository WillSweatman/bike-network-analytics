import httpx
import pandas as pd

BANK_HOLIDAYS_URL = "https://www.gov.uk/bank-holidays.json"
DIVISION = "england-and-wales"


def fetch_bank_holidays(division: str = DIVISION) -> pd.DataFrame:
    """Live GOV.UK bank holidays, for dates beyond the committed CSV snapshot used in training."""
    response = httpx.get(BANK_HOLIDAYS_URL, timeout=15)
    response.raise_for_status()
    events = response.json()[division]["events"]
    df = pd.DataFrame(events)
    df["date"] = pd.to_datetime(df["date"])
    return df.rename(columns={"title": "bank_holiday_name"})[["date", "bank_holiday_name"]]
