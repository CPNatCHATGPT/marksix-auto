import re, datetime as dt, requests, pandas as pd, pathlib, json

BASE = "https://lottery.hk/en/mark-six/results/{}"

def year_rows(y):
    html = requests.get(BASE.format(y), timeout=10).text
    issues = re.findall(r'draw-number">(\d{2}/\d{3})', html)
    dates  = re.findall(r'draw-date">(\d{2}/\d{2}/\d{4})', html)
    balls  = [int(b) for b in re.findall(r'ball-number">(\d{1,2})', html)]
    rows = []
    for i, (iss, d) in enumerate(zip(issues, dates)):
        nums = balls[i*7:i*7+7]
        rows.append({
            "issue": iss,
            "date": dt.datetime.strptime(d, "%d/%m/%Y"),
            **{f"n{k+1}": nums[k] for k in range(6)},
            "special": nums[6],
        })
    return rows

def main():
    rows, y = [], dt.date.today().year
    while len(rows) < 200:
        rows += year_rows(y)
        y -= 1
    import pandas as pd
    df = pd.DataFrame(rows).sort_values("date", ascending=False).head(200)
    p = pathlib.Path("marksix_last_200.xlsx")
    df.to_excel(p, index=False)
    pathlib.Path("marksix_last_200.json").write_text(
        json.dumps(df.to_dict(orient="records"), ensure_ascii=False)
    )
    print("Generated", p, len(df), "rows")

if __name__ == "__main__":
    main()
