import requests
import json
from datetime import datetime, timezone, timedelta
from functools import lru_cache

def formatEndDate(st):
    if st is None:
        return (None, None)
    dt = datetime.strptime(st, "%Y-%m-%dT%H:%M:%S.%f0%z")
    formatted = dt.strftime("%d.%m.%Y")

    # print days from today to date
    daysRemaining = (dt - datetime.now(timezone.utc)).days

    return (formatted, daysRemaining)


purl = "https://evinjeta.dars.si/selfcare/api/eshop/shopping-cart/validate"

json_dump = open("payload.txt", "r").read()
payload = json.loads(json_dump)


def get_headers():
    hdump = [x.split(":") for x in [t for t in open("headers.txt", "r")][1:]]
    headers = {h[0]: h[1].strip() for h in hdump}
    return headers

@lru_cache(maxsize=None)
def veljavnost(registrska: str):
    today = datetime.now()
    one_year_after = today + timedelta(days=365)
    payload["registrationNumber"] = registrska
    payload["registrationNumberAgain"] = registrska
    payload["vignetteValidityStart"] = today.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    payload["vignetteValidityEnd"] = one_year_after.strftime(
        "%Y-%m-%dT%H:%M:%S.%f0%z")
    r = requests.post(purl, json=payload, headers=get_headers(), verify=False)
    # print("\n"+r.text+"\n------------------\n\n\n")
    print(r.status_code, r.reason, r.url)
    return r.json()


def aux(registrska):
    registrska = registrska.upper().replace(" ", "").replace("-", "").strip()
    if len(registrska) > 8 or len(registrska) < 5 or not registrska.isalnum():
        return None
    if registrska == "FTEST":
        t = 1/0
    if registrska[:3] == "XXX":
      return None
    jdump = veljavnost(registrska)["vignetteValidationResult"]
    if "exemptedVehicles" in jdump and len(jdump["exemptedVehicles"]) > 0:
        return f'Oproščeno {jdump["exemptedVehicles"][0]["exemptionReasonId"]["text"]}'

    # for k, v in jdump.items():
    #     print(f"{k}: {v}")
    max_date = None
    for v in jdump["vignettes"]:
        print(v)
        date_1 = v["vignetteValidityStart"]
        date_2 = v["vignetteValidityEnd"]
        if max_date is None or date_2 > max_date:
            max_date = date_2
        # resp.append(f"Obstaja vinjeta veljavna od {formatEndDate(date_1)[0]} do {formatEndDate(date_2)[0]}, torej je veljavna še {formatEndDate(date_2)[1]} dni")
    return formatEndDate(max_date)[0]


if __name__ == "__main__":
    pass
