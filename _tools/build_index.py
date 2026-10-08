# -*- coding: utf-8 -*-
"""_data/*.json(하루치 내용) → 날짜별 페이지, index.html, 용어집.html, today/, assets/data.js, _진도.json(days) 자동 생성.
매일은 _data/YYYY-MM-DD.json 하나만 추가하고 이 스크립트를 실행하면 된다."""
import json, os, html, datetime, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PJ = os.path.join(ROOT, "_진도.json")
P = json.load(open(PJ, encoding="utf-8"))
SITE = P.get("site_url", "").rstrip("/")
tracks = P["tracks"]; tmap = {t["key"]: t for t in tracks}
road = [t for t in tracks if t["topics"]]
e = html.escape
WD = "월화수목금토일"
def wd(s): return WD[datetime.date.fromisoformat(s).weekday()]
def md(s): d = datetime.date.fromisoformat(s); return f"{d.month}/{d.day:02d}"
def short(k): return {"eng": "기술영어"}.get(k) or tmap.get(k, {"name": k})["name"].split(" ")[0]
def w(path, s):
    full = os.path.join(ROOT, path); os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    open(full, "w", encoding="utf-8").write(s)

days = []
for f in sorted(glob.glob(os.path.join(ROOT, "_data", "*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    d.setdefault("path", f'{d["date"]}/아침공부.html'); d.setdefault("cycle", 1)
    days.append(d)
days.sort(key=lambda d: (d["date"], d["day"]))

def code(s):
    out = []
    for ln in s.split("\n"):
        t = ln.strip()
        out.append(f'<span class="c">{e(ln)}</span>' if (t == "#" or t.startswith(("# ", "-- ", "// ", "REM "))) else e(ln))
    return "\n".join(out)

def chk(qid): return f'<div class="chk" data-id="{e(qid)}"><button data-v="ok">✓ 알았음</button><button data-v="hard">? 헷갈림</button></div>'

def head(title, desc, root, og_img, url, color="#3b63e0"):
    img = f"{SITE}/{og_img}" if SITE else og_img
    return f'''<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<meta property="og:type" content="website"><meta property="og:site_name" content="아침 개발공부">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(img)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:url" content="{e(SITE + '/' + url if SITE else url)}"><meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="{color}"><link rel="manifest" href="{root}manifest.webmanifest">
<link rel="apple-touch-icon" href="{root}assets/icons/apple-touch-icon.png"><link rel="icon" type="image/png" href="{root}assets/icons/icon-192.png">
<link rel="stylesheet" href="{root}assets/style.css"></head>'''

TCOL = {"dev": "#3b63e0", "db": "#1f9d55", "server": "#e8590c", "net": "#7048e8", "sm": "#0c8599", "review": "#7a8394"}
SIDE = '''<aside class="side" id="side"><div class="card">
<div class="card-h"><span class="ic">📖</span>용어 사전<small>/ 키로 검색</small></div>
<div class="tabs"><button class="on" data-m="today">오늘</button><button data-m="all">전체</button></div>
<input class="search" placeholder="모르는 용어 검색"><div class="tlist"></div></div></aside>'''

def page(d, prev, nxt):
    tk, date, root = d["track"], d["date"], "../"
    c = d.get("concept", {})
    # 섹션 목록 (모바일 하단 탭에도 사용)
    secs = [("review", "복습"), ("concept", "개념"), ("lab", "실습"), ("work", "실무"), ("quiz", "퀴즈")]
    if d.get("case"): secs.append(("case", "케이스"))
    secs.append(("next", "예습"))
    circ = "①②③④⑤⑥⑦⑧"
    steps = "".join(f'<a href="#{i}">{circ[n]} {l}</a>' for n, (i, l) in enumerate(secs))
    # 복습
    rv = "".join(f'''<div class="tile"><div class="from">{e(r["from"])}</div><p>{r["q"]}</p>
<details><summary>정답</summary><div>{r["a"]}{chk(r["ref"]) if r.get("ref") else ""}</div></details></div>''' for r in d.get("review", []))
    # 개념
    st = c.get("steps", [])
    if len(st) == 3:
        parts = []
        for n, s in enumerate(st):
            parts.append(f'<div class="tile"><div class="tt"><span class="n">{n+1}</span>{s["t"]}</div>{s.get("d","")}'
                         + (f'<small>{s["small"]}</small>' if s.get("small") else "") + (f'<span class="doc">{s["doc"]}</span>' if s.get("doc") else "") + "</div>")
        flow = '<div class="flow">' + '<div class="arrow">→</div>'.join(parts) + "</div>"
    elif st:
        flow = f'<div class="tiles c{min(len(st),5)}">' + "".join(
            f'<div class="tile"><div class="tt"><span class="n">{n+1}</span>{s["t"]}</div>{s.get("d","")}'
            + (f'<small style="display:block;color:var(--sub);font-size:12.5px;margin-top:6px">{s["small"]}</small>' if s.get("small") else "")
            + (f'<span class="doc">{s["doc"]}</span>' if s.get("doc") else "") + "</div>" for n, s in enumerate(st)) + "</div>"
    else: flow = ""
    comp = ""
    if c.get("compare"):
        comp = (f'<p style="margin:16px 0 8px;font-weight:700">{c.get("compare_title","")}</p>' if c.get("compare_title") else "") + \
            f'<div class="tiles c{min(len(c["compare"]),3)}">' + "".join(
            f'<div class="tile {x.get("kind","")}"><div class="tt">{x["t"]}</div>{x["d"]}</div>' for x in c["compare"]) + "</div>"
    dp = c.get("deep", [])
    deep = ('<details class="deep"><summary>🔬 심화 — 더 깊이 보기 (+5분)</summary><div>' + "".join(f'<div class="deep-item"><b class="dt">{x["t"]}</b>{x.get("d","")}' + (f"<pre><code>{code(x['code'])}</code></pre>" if x.get("code") else "") + "</div>" for x in dp) + "</div></details>") if dp else ""
    concept = f'''<section class="card span2" id="concept"><div class="card-h"><span class="ic">💡</span>개념 — {c.get("title","")}</div>
{c.get("intro","")}{flow}{f'<div class="info">{c["info"]}</div>' if c.get("info") else ""}{comp}{c.get("extra","")}{deep}</section>'''
    # 실습
    labs = ""
    for n, l in enumerate(d.get("lab", [])):
        body = (f'<ul class="checks">' + "".join(f"<li>{i}</li>" for i in l["items"]) + "</ul>") if l.get("items") else ""
        body += f"<pre><code>{code(l['code'])}</code></pre>" if l.get("code") else ""
        body += f'<div class="lbl2">▶ 이렇게 나오면</div><pre class="out"><code>{e(l["output"])}</code></pre>' if l.get("output") else ""
        body += ('<div class="lbl2">🔎 결과 읽는 법</div><ul class="reads">' + "".join(f"<li>{r}</li>" for r in l["read"]) + "</ul>") if l.get("read") else ""
        body += l.get("html", "")
        labs += f'''<section class="card"{' id="lab"' if n == 0 else ''}><div class="card-h"><span class="ic">{l.get("icon","🧪")}</span>{l["title"]}</div>{body}{f'<div class="tip">{l["tip"]}</div>' if l.get("tip") else ""}</section>'''
    wk = d.get("work", {})
    ms = d.get("mistakes", [])
    mist = (f'''<section class="card" id="work"><div class="card-h"><span class="ic">⚠️</span>흔한 실수<small>현장에서 실제로 자주 나오는 것</small></div><ul class="mist">{"".join(f"<li><b class='dt'>{m['t']}</b>{m['d']}</li>" for m in ms)}</ul></section>''') if ms else ""
    work = mist + f'''<section class="card"{"" if ms else ' id="work"'}><div class="card-h"><span class="ic">🧾</span>{wk.get("title","실무 팁 (SM 관점)")}</div>
<ul class="checks">{"".join(f"<li>{i}</li>" for i in wk.get("items", []))}</ul></section>'''
    qz = "".join(f'''<div class="tile"><p><b>Q{n+1}.</b> {q["q"]}</p><details><summary>정답</summary><div>{q["a"]}{chk(f"{date}-q{n}")}</div></details></div>'''
                 for n, q in enumerate(d.get("quiz", [])))
    quiz = f'''<section class="card" id="quiz"><div class="card-h"><span class="ic">✏️</span>오늘의 퀴즈<small>정답 확인 후 알았음/헷갈림 표시</small></div><div class="qlist">{qz}</div></section>'''
    case = ""
    if d.get("case"):
        k = d["case"]
        tl = "".join(f'<li><b>{s["t"]}</b>{s.get("d","")}' + (f"<pre><code>{code(s['code'])}</code></pre>" if s.get("code") else "") + "</li>" for s in k["steps"])
        case = f'''<section class="card span2" id="case"><div class="card-h"><span class="ic">🚨</span>장애 케이스 스터디 — {k["title"]}<small>가상의 일반 사례</small></div>
<div class="tiles c2"><div><div class="say bad"><span class="lbl">증상</span>{k["symptom"]}</div><ol class="timeline">{tl}</ol></div>
<div><p style="font-weight:800;margin:10px 0 6px">📝 장애보고서에는 이렇게</p><div class="report">{k["report"]}</div>{f'<div class="tip">{k["tip"]}</div>' if k.get("tip") else ""}</div></div></section>'''
    nx = d.get("next", {})
    nxt_card = f'''<section class="card" id="next"><div class="card-h"><span class="ic">🔭</span>다음 예습 · <span style="color:var(--{nx.get("track","dev")})">{e(short(nx.get("track","dev")))}</span></div>
<p style="font-size:17px;font-weight:800;margin-bottom:6px">{nx.get("title","")}</p><p style="color:var(--sub)">미리 생각해 보기: {nx.get("question","")}</p>
{f'<div class="tip">{nx["tip"]}</div>' if nx.get("tip") else ""}</section>
<section class="card summary"><div><small>오늘 한 줄 정리</small>📌 {e(d["one_liner"])}</div></section>'''
    dev = f'''<div class="panel" data-p="dev"><div class="grid">
<section class="card span2" id="review"><div class="card-h"><span class="ic">🔁</span>워밍업 복습<small>{d.get("review_note","")}</small></div><div class="tiles c3">{rv}</div></section>
{concept}{labs}{work}{quiz}{case}{nxt_card}</div></div>'''
    # 부가 탭
    x = d.get("extras", {})
    cm = x.get("comm")
    comm = ""
    if cm:
        cases = cm.get("cases") or [{"title": cm.get("title",""), "situation": cm["situation"], "bad": cm["bad"], "good": cm["good"]}]
        cc = "".join(f'''<section class="card"><div class="card-h"><span class="ic">💬</span>{k["title"]}<span class="lvq">상황 {n+1}</span></div>
<p class="situ">📍 {k["situation"]}</p><div class="say bad"><span class="lbl">아쉬운 예</span>{k["bad"]}</div><div class="say good"><span class="lbl">이렇게 바꿔 보기</span>{k["good"]}</div></section>''' for n, k in enumerate(cases))
        ph = "".join(f'<div class="phr"><span>{e(t)}</span><button class="copy" data-t="{e(t)}">복사</button></div>' for t in cm.get("phrases", []))
        comm = f'''<div class="panel" data-p="comm"><div class="grid">{cc}
<section class="card"><div class="card-h"><span class="ic">🎯</span>{e(cm["theme"])}의 공통 원칙</div><ul class="checks">{"".join(f"<li>{i}</li>" for i in cm["points"])}</ul>
<p style="font-weight:800;margin:14px 0 6px">오늘의 틀</p><pre><code>{code(cm["template"])}</code></pre></section>
{f'<section class="card span2"><div class="card-h"><span class="ic">📋</span>바로 쓰는 문장<small>복사해서 그대로 쓰세요</small></div>{ph}</section>' if ph else ""}
</div></div>'''
    ct = x.get("cert")
    cert = ""
    if ct:
        qs = ct.get("questions") or [ct]
        qh = "".join(f'''<section class="card cert" data-answer="{q["answer"]}" data-id="{date}-c{n}"><div class="card-h"><span class="ic">✍️</span>문제 {n+1}<span class="lvq">{e(q.get("level",""))}</span></div>
<p class="qtext">{q["q"]}</p><div class="choices">{"".join(f'<button class="choice"><b>{i+1}</b>{ch}</button>' for i, ch in enumerate(q["choices"]))}</div>
<div class="explain"><b>정답 {q["answer"]+1}번.</b> {q["explain"]}{chk(f"{date}-c{n}")}</div></section>''' for n, q in enumerate(qs))
        cert = f'''<div class="panel" data-p="cert"><div class="grid">
<section class="card"><div class="card-h"><span class="ic">🎓</span>{e(ct["exam"])}<small>{e(ct["subject"])}</small></div><div class="summary-box">{ct.get("summary","")}</div>
<div class="tip" style="font-size:13px">출제 경향을 참고해 만든 연습 문제예요. 시험 일정·제도는 공식 사이트에서 확인하세요.</div>{f'<div class="info">{ct["tip"]}</div>' if ct.get("tip") else ""}</section>
{qh}</div></div>'''
    en = x.get("eng")
    eng = ""
    if en:
        rd = en.get("reading")
        rdh = f'''<section class="card span2"><div class="card-h"><span class="ic">📄</span>독해 연습 — {rd["title"]}<small>먼저 스스로 읽고 해석을 펼쳐 보세요</small></div>
<pre><code>{e(rd["text"])}</code></pre><details><summary>한 줄씩 해석 보기</summary><div><dl class="tr">{"".join(f"<dt>{e(l['en'])}</dt><dd>{l['ko']}</dd>" for l in rd["lines"])}</dl></div></details>
{f'<div class="tip">{rd["note"]}</div>' if rd.get("note") else ""}</section>''' if rd else ""
        eng = f'''<div class="panel" data-p="eng"><div class="grid">
<section class="card span2"><div class="card-h"><span class="ic">🌐</span>오늘의 기술 영어<small>로그·문서·에러 메시지에서 자주 보는 표현</small></div>
<div class="tiles c3">{"".join(f'<div class="tile eng-item"><div class="en">{e(i["en"])}</div><div class="ko">{e(i["ko"])}</div><div class="where">📍 {e(i["where"])}</div><div class="ex">{e(i["ex"])}<i>{e(i["ex_ko"])}</i></div></div>' for i in en["items"])}</div>
{f'<div class="tip">{en["tip"]}</div>' if en.get("tip") else ""}</section>{rdh}</div></div>'''
    terms = "".join(f'<dt>{e(t["term"])}</dt><dd>{e(t["desc"])}</dd>' for t in d.get("terms", []))
    if en: terms += "".join(f'<dt data-track="eng">{e(i["en"])}</dt><dd>{e(i["ko"])} — {e(i["where"])}</dd>' for i in en["items"])
    pv = f'<a href="../{e(prev["path"])}">‹ {md(prev["date"])}</a>' if prev else ""
    nv = f'<a href="../{e(nxt["path"])}">{md(nxt["date"])} ›</a>' if nxt else ""
    title = f'{md(date)} {short(tk)} · {d["title"]}'
    desc = f'📌 {d["one_liner"]} — 개발 15분 + 커뮤니케이션 · 자격증 · 기술영어'
    return head(title, desc, root, f"assets/og/{tk}.png", d["path"], TCOL.get(tk, "#3b63e0")) + f'''
<body class="{tk}" data-root="{root}" data-path="{e(d["path"])}"><div class="page"><main>
<div class="topbar"><a href="../index.html">← 메인</a><span class="daynav">{pv}{nv}</span><span class="daynav"><a href="../치트시트.html">📋 치트시트</a><a href="../용어집.html">📖 용어집</a></span></div>
<section class="hero"><div class="chips"><span class="chip">{e(short(tk))}</span><span class="chip">Day {d["day"]}</span><span class="chip">{md(date)} ({wd(date)})</span><span class="chip">⏱ {d.get("minutes",15)}분</span>{f'<span class="chip lv">{e(d["level"])}</span>' if d.get("level") else ""}</div>
<h1>{e(d["title"])}</h1><p class="lead">{d.get("lead","")}</p><div class="steps">{steps}</div></section>
<div class="ptabs"><button data-p="dev">📘 개발공부</button>{'<button data-p="comm">💬 커뮤니케이션</button>' if cm else ""}{'<button data-p="cert">🎓 자격증</button>' if ct else ""}{'<button data-p="eng">🌐 기술영어</button>' if en else ""}</div>
{dev}{comm}{cert}{eng}<dl id="today-terms" hidden>{terms}</dl></main>{SIDE}</div>
<button class="fab">📖 용어</button><script src="../assets/data.js"></script><script src="../assets/app.js"></script></body></html>'''

for i, d in enumerate(days):
    w(d["path"], page(d, days[i-1] if i else None, days[i+1] if i + 1 < len(days) else None))

# 공통 데이터 (용어 + 퀴즈)
terms = [dict(t, track=d["track"], date=md(d["date"]), path=d["path"]) for d in days for t in d.get("terms", [])]
terms += [{"term": i["en"], "desc": f'{i["ko"]} — {i["where"]}', "track": "eng", "date": md(d["date"]), "path": d["path"] + "#eng"}
          for d in days for i in d.get("extras", {}).get("eng", {}).get("items", [])]
quiz = [{"id": f'{d["date"]}-q{n}', "q": q["q"], "path": d["path"], "date": md(d["date"]), "track": d["track"]} for d in days for n, q in enumerate(d.get("quiz", []))]
quiz += [{"id": f'{d["date"]}-c{n}', "q": q["q"], "path": d["path"] + "#cert", "date": md(d["date"]), "track": "cert"}
         for d in days if d.get("extras", {}).get("cert") for n, q in enumerate(d["extras"]["cert"].get("questions") or [d["extras"]["cert"]])]
w("assets/data.js", "window.TERMS=" + json.dumps(terms, ensure_ascii=False) + ";\nwindow.QUIZ=" + json.dumps(quiz, ensure_ascii=False) + ";")

# _진도.json days 동기화 (복습 문제 고를 때 참고용)
P["days"] = [{k: d[k] for k in ("date", "day", "cycle", "track", "topic_no", "title", "one_liner", "path") if k in d} | {"quiz": d.get("quiz", []), "terms": d.get("terms", [])} for d in days]
if days: P["cycle"] = days[-1].get("cycle", 1)
json.dump(P, open(PJ, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

cur = P.get("cycle", 1)
done = {(d.get("cycle", 1), d["track"], d.get("topic_no")): d for d in days if d["track"] != "review"}
def ndone(k): return sum(1 for (c, t, _) in done if c == cur and t == k)
total = sum(len(t["topics"]) for t in road); done_now = sum(ndone(t["key"]) for t in road)
rot = P.get("rotation", [t["key"] for t in road])
last = next((d for d in reversed(days) if d["track"] != "review"), None)
nk = rot[(rot.index(last["track"]) + 1) % len(rot)] if last else rot[0]
nt = tmap[nk]["topics"][ndone(nk) % len(tmap[nk]["topics"])]
JS = '''<script>(function(){var f="all",q=document.getElementById("q");
function ap(){var s=q.value.trim().toLowerCase();document.querySelectorAll("[data-track]").forEach(function(el){
el.style.display=((f==="all"||el.dataset.track===f)&&(!s||el.textContent.toLowerCase().indexOf(s)>=0))?"":"none";});}
document.querySelectorAll(".filters button").forEach(function(b){b.onclick=function(){
document.querySelectorAll(".filters button").forEach(function(x){x.classList.remove("on")});b.classList.add("on");f=b.dataset.f;ap();};});
q.oninput=ap;})();</script>'''
used = [k for k in [t["key"] for t in tracks] + ["eng"] if any(x["track"] == k for x in terms) or any(d["track"] == k for d in days)]
def btns(keys): return '<button class="on" data-f="all">전체</button>' + "".join(f'<button data-f="{k}">{e(short(k))}</button>' for k in keys)
TC = lambda k: f"--tc:var(--{k})"
latest = days[-1] if days else None

# today/ (항상 최신 공부로 이동 + 링크 미리보기)
if latest:
    w("today/index.html", head(f'오늘의 공부 · {md(latest["date"])} {short(latest["track"])} · {latest["title"]}', f'📌 {latest["one_liner"]} — 개발 15분 + 커뮤니케이션 · 자격증 · 기술영어',
        "../", f'assets/og/{latest["track"]}.png', "today/") + f'''<body><p style="padding:20px">오늘의 공부로 이동 중… <a href="../{e(latest["path"])}">바로 가기</a></p>
<script>location.replace("../{latest["path"]}"+location.hash)</script></body></html>''')

hero_today = f'''<a class="card" href="{e(latest["path"])}" style="display:block;color:inherit;border-left:6px solid var(--{latest["track"]})">
<div class="card-h" style="margin-bottom:6px"><span class="ic">📘</span>최근 공부<small>{latest["date"]} ({wd(latest["date"])}) · Day {latest["day"]}</small></div>
<div style="font-size:20px;font-weight:800">{e(latest["title"])}</div><div style="color:var(--sub);margin-top:4px">📌 {e(latest["one_liner"])}</div>
<div style="margin-top:10px;font-size:13px;color:var(--sub)">💬 커뮤니케이션 · 🎓 자격증 · 🌐 기술영어 탭 포함</div></a>''' if latest else ""
nxt = f'''<div class="card" style="border-left:6px solid var(--{nk})"><div class="card-h" style="margin-bottom:6px"><span class="ic">⏭️</span>다음 차례</div>
<div style="font-size:20px;font-weight:800"><span style="color:var(--{nk})">{e(short(nk))}</span> · {e(nt)}</div>
<div style="color:var(--sub);margin-top:4px">빠진 날이 있어도 이 순서대로 이어집니다</div></div>'''
cards = "".join(f'''<a class="dcard" data-track="{d["track"]}" style="{TC(d["track"])}" href="{e(d["path"])}">
<div class="m"><b>{e(short(d["track"]))}</b> · Day {d["day"]} · {md(d["date"])} ({wd(d["date"])}){f' · {e(d["level"])}' if d.get("level") else ""}</div>
<div class="t">{e(d["title"])}</div><div class="o">📌 {e(d["one_liner"])}</div></a>''' for d in reversed(days))
trk = ""
for t in road:
    n = ndone(t["key"]); lis = ""
    for i, name in enumerate(t["topics"]):
        d = done.get((cur, t["key"], i + 1))
        lis += f'<li class="done"><a href="{e(d["path"])}">✓ {e(name)}</a></li>' if d else (f'<li class="next">→ {e(name)}</li>' if i == n else f"<li>{e(name)}</li>")
    trk += f'''<div class="trk" style="{TC(t["key"])}"><h4>{e(t["name"])}</h4><div style="font-size:12px;color:var(--sub)">{n}/{len(t["topics"])}</div>
<div class="bar"><i style="width:{n*100//len(t["topics"])}%"></i></div><ol>{lis}</ol></div>'''
nterms = len(terms)
index = head("아침 개발공부 — 하루 15분 SM 스킬업", "개발 · DB · 서버 · 네트워크 · SM 실무를 매일 15분씩. 커뮤니케이션 · 자격증 · 기술영어까지.", "", "assets/og/main.png", "") + f'''
<body class="dev" data-root=""><div class="page full"><main>
<section class="hero"><div class="chips"><span class="chip">SM 스킬업 루틴</span><span class="chip">하루 15분</span><span class="chip">💬 🎓 🌐 탭 포함</span></div>
<h1>🌅 아침 개발공부</h1><p class="lead">개발 · DB · 서버 · 네트워크 · SM 실무를 순서대로 돌며 복습과 예습을 함께 합니다</p>
<div class="stats"><div class="stat"><b>{len(days)}일</b><span>누적 공부</span></div><div class="stat"><b>{done_now}/{total}</b><span>{cur}회차 진도</span></div>
<div class="stat"><b>{nterms}개</b><span>용어·표현</span></div><div class="stat"><b>{len(quiz)}문제</b><span>퀴즈·자격증</span></div></div>
<div class="steps"><a href="today/">☀️ 오늘 공부 바로가기</a><a href="용어집.html">📖 용어집</a><a href="치트시트.html">📋 명령어 치트시트</a></div></section>
<div class="grid" style="margin-bottom:16px">{hero_today}{nxt}</div>
<section class="card" style="margin-bottom:16px;--c:var(--warn)"><div class="card-h"><span class="ic">🔖</span>내 복습함<small id="review-count"></small></div>
<div id="review-box"></div><div class="meta" style="font-size:12.5px;color:var(--sub);margin-top:6px">이 기기에만 저장돼요. 다른 사람과 기록이 섞이지 않습니다.</div></section>
<section class="card" style="margin-bottom:16px"><div class="card-h"><span class="ic">📚</span>지난 공부</div>
<div class="filters">{btns([t["key"] for t in road if any(d["track"]==t["key"] for d in days)])}<input id="q" class="search" placeholder="제목·한 줄 정리 검색"></div>
<div class="dgrid">{cards}</div></section>
<section class="card"><div class="card-h"><span class="ic">🗺️</span>{cur}회차 로드맵<small>✓ 완료 · → 다음 차례</small></div><div class="tracks">{trk}</div></section>
<p style="text-align:center;color:var(--sub);font-size:12.5px">마지막 갱신 {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</main></div>{JS}<script src="assets/data.js"></script><script src="assets/app.js"></script></body></html>'''
w("index.html", index)

gc = "".join(f'''<div class="gcard" data-track="{x["track"]}" style="{TC(x["track"])}"><div class="k">{e(x["term"])}</div><div class="d">{e(x["desc"])}</div>
<div class="s"><a href="{e(x["path"])}" style="color:var(--tc)">{x["date"]} · {e(short(x["track"]))}에서 배움 →</a></div></div>''' for x in sorted(terms, key=lambda x: x["term"].lower()))
w("용어집.html", head("용어집 · 아침 개발공부", f"지금까지 공부한 용어·영어 표현 {nterms}개", "", "assets/og/main.png", "용어집.html") + f'''
<body class="dev" data-root=""><div class="page full"><main><div class="topbar"><a href="index.html">← 메인</a><span></span></div>
<section class="hero"><div class="chips"><span class="chip">가나다·ABC 순</span></div><h1>📖 용어집</h1>
<p class="lead">지금까지 공부한 용어·기술영어 표현 {nterms}개 · 카드 아래 링크로 배운 날로 이동</p></section>
<section class="card"><div class="filters">{btns(used)}<input id="q" class="search" placeholder="용어나 설명 검색 (예: 방화벽, rollback)"></div>
<div class="ggrid">{gc or '<div class="empty">아직 용어가 없습니다.</div>'}</div></section></main></div>{JS}</body></html>''')

cheats = [dict(c, track=d["track"], date=md(d["date"]), path=d["path"]) for d in days for c in d.get("cheat", [])]
groups = ""
for t in road:
    items = [c for c in cheats if c["track"] == t["key"]]
    if not items: continue
    groups += f'<h3 style="margin:18px 0 10px;color:var(--{t["key"]})">{e(t["name"])} <small style="color:var(--sub);font-weight:500">{len(items)}개</small></h3><div class="ggrid">' + "".join(
        f'''<div class="gcard" data-track="{c["track"]}" style="{TC(c["track"])}"><div class="row"><code>{e(c["cmd"])}</code><button class="copy" data-t="{e(c["cmd"])}">복사</button></div>
<div class="d">{e(c["desc"])}</div><div class="s"><a href="{e(c["path"])}" style="color:var(--tc)">{c["date"]}에서 배움 →</a></div></div>''' for c in items) + "</div>"
w("치트시트.html", head("명령어 치트시트 · 아침 개발공부", f"지금까지 나온 명령어·쿼리 {len(cheats)}개", "", "assets/og/main.png", "치트시트.html") + f'''
<body class="dev" data-root=""><div class="page full"><main><div class="topbar"><a href="index.html">← 메인</a><a href="용어집.html">📖 용어집</a></div>
<section class="hero"><div class="chips"><span class="chip">매일 자동 누적</span></div><h1>📋 명령어 치트시트</h1>
<p class="lead">공부하면서 나온 명령어·쿼리 {len(cheats)}개 · 업무 중에 찾아 쓰세요 (&lt;IP&gt; 같은 부분은 바꿔서)</p></section>
<section class="card cheat"><div class="filters">{btns([t["key"] for t in road if any(c["track"]==t["key"] for c in cheats)])}<input id="q" class="search" placeholder="명령어나 설명 검색 (예: 포트, 디스크, git)"></div>
{groups or '<div class="empty">아직 없습니다.</div>'}</section></main></div>{JS}<script src="assets/app.js"></script></body></html>''')
w("manifest.webmanifest", json.dumps({"name": "아침 개발공부", "short_name": "아침공부", "start_url": "/today/", "scope": "/", "display": "standalone",
    "background_color": "#eef2f7", "theme_color": "#3b63e0",
    "icons": [{"src": "/assets/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "/assets/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False, indent=2))
print(f"갱신 완료: {len(days)}일, 용어 {nterms}개, 퀴즈 {len(quiz)}개, 다음={nk}/{nt}")
