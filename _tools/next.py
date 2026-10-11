# -*- coding: utf-8 -*-
"""다음 공부 준비 정보만 짧게 출력한다 (토큰 절약용).
사용: python3 _tools/next.py [YYYY-MM-DD]   (생략하면 오늘, 한국시간)
출력: 오늘 트랙·주제·Day 번호, 다음 예습 주제, 복습 후보 문제(어제·7일 전·28일 전·이번 주), 이미 쓴 용어/명령어/테마 목록, 참고할 최근 파일"""
import json, glob, os, sys, datetime, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "_진도.json"), encoding="utf-8"))
tmap = {t["key"]: t for t in P["tracks"]}; rot = P.get("rotation", ["dev", "db", "server", "net", "sm"])
KST = datetime.timezone(datetime.timedelta(hours=9))
target = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else datetime.datetime.now(KST).date()
files = sorted(glob.glob(os.path.join(ROOT, "_data", "*.json")))
days = [dict(json.load(open(f, encoding="utf-8")), _file=os.path.basename(f)) for f in files]
days.sort(key=lambda d: (d["date"], d["day"]))
strip = lambda s: re.sub(r"<[^>]+>", "", s).replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
WD = "월화수목금토일"
print(f"## 대상 날짜: {target} ({WD[target.weekday()]})")
same = [d for d in days if d["date"] == target.isoformat()]
if same: print(f"!! 이미 있음: {', '.join(d['_file'] for d in same)} (재생성 요청이 아니면 만들지 말 것)")
prior = [d for d in days if d["date"] < target.isoformat() or d in same]
if target.weekday() >= 5:
    print("!! 주말 → 주간 복습 특집(track=review)")
last = next((d for d in reversed(prior) if d["track"] != "review"), None)
def nxt(after):
    k = rot[(rot.index(after) + 1) % len(rot)] if after else rot[0]
    n = sum(1 for d in prior if d["track"] == k)
    return k, n
k, n = nxt(last["track"] if last else None)
tps = tmap[k]["topics"]
print(f"## 오늘: track={k}({tmap[k]['name']}) topic_no={n % len(tps) + 1} cycle={n // len(tps) + 1} 주제='{tps[n % len(tps)]}' day={len(days) + (0 if same else 1)}")
k2 = rot[(rot.index(k) + 1) % len(rot)]; n2 = sum(1 for d in prior if d["track"] == k2)
print(f"## 다음 예습(next): track={k2} 주제='{tmap[k2]['topics'][n2 % len(tmap[k2]['topics'])]}'")
if prior:
    gap = sum(1 for i in range(1, (target - datetime.date.fromisoformat(prior[-1]["date"])).days) if (datetime.date.fromisoformat(prior[-1]["date"]) + datetime.timedelta(i)).weekday() < 5)
    if gap >= 3: print(f"!! 평일 {gap}일 공백 → 공백 복습 3문항 추가")
def show(label, d):
    if not d: return
    print(f"\n### 복습 후보 · {label}: {d['date']} {d['track']} '{d['title']}'")
    for i, q in enumerate(d.get("quiz", [])): print(f"- ref={d['date']}-q{i} | Q: {strip(q['q'])} | A: {strip(q['a'])}")
def near(delta):
    lim = (target - datetime.timedelta(delta)).isoformat(); c = [d for d in prior if d["date"] <= lim]
    return c[-1] if c else None
show("직전", prior[-1] if prior else None)
d7, d28 = near(7), near(28)
if d7 and (not prior or d7 is not prior[-1]): show("약 7일 전", d7)
if d28 and d28 is not d7: show("약 28일 전", d28)
if target.weekday() == 4:
    mon = (target - datetime.timedelta(4)).isoformat()
    for d in prior:
        if d["date"] >= mon and d is not prior[-1]: show("이번 주", d)
print("\n## 이미 쓴 용어:", ", ".join(t["term"] for d in days for t in d.get("terms", [])))
print("## 이미 쓴 명령어:", " | ".join(c["cmd"] for d in days for c in d.get("cheat", [])))
cm = [d.get("extras", {}).get("comm", {}).get("theme") for d in days if d.get("extras", {}).get("comm")]
print("## 최근 커뮤니케이션 테마:", " → ".join(cm[-5:]))
print("## 이번 주 케이스 스터디:", "있음" if any(d.get("case") and d["date"] >= (target - datetime.timedelta(target.weekday())).isoformat() for d in prior) else "없음 (금요일 또는 이번 주 마지막 공부일에 넣기)")
print("## 스키마 참고 파일:", "_data/" + days[-1]["_file"] if days else "없음")
