# -*- coding: utf-8 -*-
"""_진도.json → index.html(메인), 용어집.html, assets/terms.js 재생성"""
import json, os, html, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "_진도.json"), encoding="utf-8"))
tracks = P["tracks"]; tmap = {t["key"]: t for t in tracks}
road = [t for t in tracks if t["topics"]]
days = sorted(P["days"], key=lambda d: (d["date"], d["day"]))
e = html.escape
WD = "월화수목금토일"
def wd(s): return WD[datetime.date.fromisoformat(s).weekday()]
def short(k): return tmap.get(k, {"name": k})["name"].split(" ")[0]
def md(s): d = datetime.date.fromisoformat(s); return f"{d.month}/{d.day:02d}"
cur = P.get("cycle", 1)
done = {(d.get("cycle", 1), d["track"], d.get("topic_no")): d for d in days if d["track"] != "review"}
def ndone(k): return sum(1 for (c, t, _) in done if c == cur and t == k)
total = sum(len(t["topics"]) for t in road); done_now = sum(ndone(t["key"]) for t in road)
terms = [dict(x, track=d["track"], date=md(d["date"]), path=d["path"]) for d in days for x in d.get("terms", [])]

# terms.js (공부 페이지 사이드바용)
open(os.path.join(ROOT, "assets", "terms.js"), "w", encoding="utf-8").write(
    "window.TERMS=" + json.dumps(terms, ensure_ascii=False) + ";")

# 다음 차례
rot = P.get("rotation", [t["key"] for t in road])
last = next((d for d in reversed(days) if d["track"] != "review"), None)
nk = rot[(rot.index(last["track"]) + 1) % len(rot)] if last else rot[0]
nt = tmap[nk]["topics"][ndone(nk) % len(tmap[nk]["topics"])]

HEAD = '''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{t}</title>
<link rel="stylesheet" href="assets/style.css"></head><body class="{c}"><div class="page full"><main>'''
JS = '''<script>(function(){var f="all",q=document.getElementById("q");
function ap(){var s=q.value.trim().toLowerCase();document.querySelectorAll("[data-track]").forEach(function(el){
el.style.display=((f==="all"||el.dataset.track===f)&&(!s||el.textContent.toLowerCase().indexOf(s)>=0))?"":"none";});}
document.querySelectorAll(".filters button").forEach(function(b){b.onclick=function(){
document.querySelectorAll(".filters button").forEach(function(x){x.classList.remove("on")});b.classList.add("on");f=b.dataset.f;ap();};});
q.oninput=ap;})();</script>'''
used = [t for t in tracks if any(d["track"] == t["key"] for d in days)]
def btns(): return '<button class="on" data-f="all">전체</button>' + "".join(
    f'<button data-f="{t["key"]}">{e(short(t["key"]))}</button>' for t in used)
TC = lambda k: f"--tc:var(--{k})"

# ---------- 메인 ----------
latest = days[-1] if days else None
hero_today = ""
if latest:
    hero_today = f'''<a class="card" href="{e(latest["path"])}" style="display:block;color:inherit;border-left:6px solid var(--{latest["track"]})">
<div class="card-h" style="margin-bottom:6px"><span class="ic">📘</span>최근 공부<small>{latest["date"]} ({wd(latest["date"])}) · Day {latest["day"]}</small></div>
<div style="font-size:20px;font-weight:800">{e(latest["title"])}</div>
<div style="color:var(--sub);margin-top:4px">📌 {e(latest.get("one_liner",""))}</div></a>'''
nxt = f'''<div class="card" style="border-left:6px solid var(--{nk})">
<div class="card-h" style="margin-bottom:6px"><span class="ic">⏭️</span>다음 차례<small>"오늘 아침 브리핑해줘"</small></div>
<div style="font-size:20px;font-weight:800"><span style="color:var(--{nk})">{e(short(nk))}</span> · {e(nt)}</div>
<div style="color:var(--sub);margin-top:4px">빠진 날이 있어도 이 순서대로 이어집니다</div></div>'''
cards = "".join(f'''<a class="dcard" data-track="{d["track"]}" style="{TC(d["track"])}" href="{e(d["path"])}">
<div class="m"><b>{e(short(d["track"]))}</b> · Day {d["day"]} · {md(d["date"])} ({wd(d["date"])})</div>
<div class="t">{e(d["title"])}</div><div class="o">📌 {e(d.get("one_liner",""))}</div></a>''' for d in reversed(days))
trk = ""
for t in road:
    n = ndone(t["key"]); lis = ""
    for i, name in enumerate(t["topics"]):
        d = done.get((cur, t["key"], i + 1))
        if d: lis += f'<li class="done"><a href="{e(d["path"])}">✓ {e(name)}</a></li>'
        elif i == n: lis += f'<li class="next">→ {e(name)}</li>'
        else: lis += f"<li>{e(name)}</li>"
    trk += f'''<div class="trk" style="{TC(t["key"])}"><h4>{e(t["name"])}</h4>
<div style="font-size:12px;color:var(--sub)">{n}/{len(t["topics"])}</div><div class="bar"><i style="width:{n*100//len(t["topics"])}%"></i></div><ol>{lis}</ol></div>'''
index = HEAD.format(t="아침 개발공부", c="dev") + f'''
<section class="hero"><div class="chips"><span class="chip">SM 스킬업 루틴</span><span class="chip">하루 15분</span></div>
<h1>🌅 아침 개발공부</h1><p class="lead">개발 · DB · 서버 · 네트워크 · SM 실무를 순서대로 돌며 복습과 예습을 함께 합니다</p>
<div class="stats"><div class="stat"><b>{len(days)}일</b><span>누적 공부</span></div>
<div class="stat"><b>{done_now}/{total}</b><span>{cur}회차 진도</span></div>
<div class="stat"><b>{len(terms)}개</b><span>익힌 용어</span></div>
<div class="stat"><b>{cur}회차</b><span>{"기본기 다지기" if cur==1 else "심화·장애사례"}</span></div></div>
<div class="steps"><a href="용어집.html">📖 용어집 열기</a></div></section>
<div class="grid" style="margin-bottom:16px">{hero_today}{nxt}</div>
<section class="card" style="margin-bottom:16px"><div class="card-h"><span class="ic">📚</span>지난 공부</div>
<div class="filters">{btns()}<input id="q" class="search" placeholder="제목·한 줄 정리 검색"></div>
<div class="dgrid">{cards}</div></section>
<section class="card"><div class="card-h"><span class="ic">🗺️</span>{cur}회차 로드맵<small>✓ 완료 · → 다음 차례</small></div>
<div class="tracks">{trk}</div></section>
<p style="text-align:center;color:var(--sub);font-size:12.5px">마지막 갱신 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</main></div>{JS}</body></html>'''
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(index)

# ---------- 용어집 ----------
gc = "".join(f'''<div class="gcard" data-track="{x["track"]}" style="{TC(x["track"])}">
<div class="k">{e(x["term"])}</div><div class="d">{e(x["desc"])}</div>
<div class="s"><a href="{e(x["path"])}" style="color:var(--tc)">{x["date"]} · {e(short(x["track"]))}에서 배움 →</a></div></div>'''
    for x in sorted(terms, key=lambda x: x["term"].lower()))
gloss = HEAD.format(t="용어집 · 아침 개발공부", c="dev") + f'''
<div class="topbar"><a href="index.html">← 메인</a><span></span></div>
<section class="hero"><div class="chips"><span class="chip">가나다·ABC 순</span></div><h1>📖 용어집</h1>
<p class="lead">지금까지 공부한 용어 {len(terms)}개 · 카드 아래 링크로 배운 날 페이지로 이동</p></section>
<section class="card"><div class="filters">{btns()}<input id="q" class="search" placeholder="용어나 설명 검색 (예: 방화벽, 인덱스)" autofocus></div>
<div class="ggrid">{gc or '<div class="empty">아직 용어가 없습니다.</div>'}</div></section>
</main></div>{JS}</body></html>'''
open(os.path.join(ROOT, "용어집.html"), "w", encoding="utf-8").write(gloss)
print(f"갱신 완료: {len(days)}일, 용어 {len(terms)}개, 다음={nk}/{nt}")
