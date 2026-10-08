/* 아침 개발공부 공통 스크립트 (자동 생성 페이지용) */
(function(){
  var B=document.body, ROOT=B.dataset.root||"", PATH=B.dataset.path||"";
  var T=window.TERMS||[], Q=window.QUIZ||[];
  var COLORS={dev:"var(--dev)",db:"var(--db)",server:"var(--server)",net:"var(--net)",sm:"var(--sm)",review:"var(--review)",eng:"var(--eng)"};
  var NAMES={dev:"개발",db:"DB",server:"서버",net:"네트워크",sm:"SM",review:"복습",eng:"기술영어",cert:"자격증"};
  function ls(k,v){try{ if(v===undefined) return localStorage.getItem(k); if(v===null) localStorage.removeItem(k); else localStorage.setItem(k,v);}catch(e){return null}}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
  function strip(s){var d=document.createElement("div");d.innerHTML=s;return d.textContent}

  /* 1) 셀프 체크 (알았음/헷갈림) — 보는 사람 기기에 저장 */
  function paintChk(c){var v=ls("chk:"+c.dataset.id); c.querySelectorAll("button").forEach(function(b){b.classList.toggle("on",b.dataset.v===v)});}
  document.querySelectorAll(".chk").forEach(function(c){
    c.querySelectorAll("button").forEach(function(b){b.onclick=function(){
      var k="chk:"+c.dataset.id; ls(k, ls(k)===b.dataset.v?null:b.dataset.v);
      document.querySelectorAll('.chk[data-id="'+c.dataset.id+'"]').forEach(paintChk);};});
    paintChk(c);
  });

  /* 2) 자격증 문제 풀기 */
  document.querySelectorAll(".cert").forEach(function(box){
    var ans=+box.dataset.answer, ex=box.querySelector(".explain");
    box.querySelectorAll(".choice").forEach(function(b,i){ b.onclick=function(){
      box.querySelectorAll(".choice").forEach(function(x,j){x.classList.toggle("right",j===ans);x.classList.toggle("wrong",j===i&&i!==ans);x.disabled=true;});
      ex.classList.add("show");
      if(!ls("chk:"+box.dataset.id)) ls("chk:"+box.dataset.id, i===ans?"ok":"hard");
      box.querySelectorAll(".chk").forEach(paintChk);
    };});
  });

  /* 3) 메인: 내 복습함 */
  var rb=document.getElementById("review-box");
  if(rb){
    var hard=Q.filter(function(q){return ls("chk:"+q.id)==="hard"}), okc=Q.filter(function(q){return ls("chk:"+q.id)==="ok"}).length;
    rb.innerHTML=hard.length?hard.slice().reverse().map(function(q){return '<a class="rq" href="'+esc(q.path)+'"><span class="m">'+esc(q.date)+' · '+(NAMES[q.track]||q.track)+'</span>'+esc(strip(q.q))+'</a>'}).join("")
      :'<div class="empty">아직 "헷갈림"으로 표시한 문제가 없어요. 퀴즈 정답 아래 버튼으로 표시하면 여기에 모입니다.</div>';
    var cnt=document.getElementById("review-count"); if(cnt) cnt.textContent="헷갈림 "+hard.length+" · 알았음 "+okc+" / 전체 "+Q.length;
  }

  /* 4) 상단 탭 (개발공부 / 커뮤니케이션 / 자격증 / 기술영어) */
  var tabs=document.querySelectorAll(".ptabs button"), panels=document.querySelectorAll(".panel");
  function openPanel(id,scroll){
    tabs.forEach(function(b){b.classList.toggle("on",b.dataset.p===id)});
    panels.forEach(function(p){p.classList.toggle("on",p.dataset.p===id)});
    B.dataset.panel=id;
    try{history.replaceState(null,"",id==="dev"?location.pathname:"#"+id)}catch(e){}
    if(scroll){var t=document.querySelector(".ptabs");window.scrollTo({top:t.getBoundingClientRect().top+window.scrollY-8,behavior:"smooth"})}
  }
  if(tabs.length){
    tabs.forEach(function(b){b.onclick=function(){openPanel(b.dataset.p,true)}});
    var h=location.hash.slice(1); openPanel(["comm","cert","eng"].indexOf(h)>=0?h:"dev",false);
    document.querySelectorAll(".hero .steps a").forEach(function(a){a.addEventListener("click",function(){openPanel("dev",false)})});
  }

  /* 5) 용어 사전 사이드바 + 본문 용어 툴팁 */
  var side=document.getElementById("side");
  var todays=[]; document.querySelectorAll("#today-terms dt").forEach(function(dt){
    todays.push({term:dt.textContent.trim(),desc:dt.nextElementSibling.textContent.trim(),track:dt.dataset.track||B.className.split(" ")[0],date:"오늘",path:PATH});});
  var all=T.filter(function(x){return x.path!==PATH}).concat(todays);
  if(side){
    var list=side.querySelector(".tlist"), q=side.querySelector(".search"), mode="today";
    var render=function(hl){
      var s=q.value.trim().toLowerCase(), src=(mode==="today"&&!s)?todays:all;
      var rows=src.filter(function(x){return !s||(x.term+" "+x.desc).toLowerCase().indexOf(s)>=0})
        .sort(function(a,b){return (mode==="today"&&!s)?0:a.term.localeCompare(b.term,"ko")});
      list.innerHTML=rows.length?rows.map(function(x){
        var link=x.path&&x.path!==PATH?'<a href="'+ROOT+esc(x.path)+'">'+esc(x.date)+' · '+(NAMES[x.track]||"")+'에서 배움 →</a>':'<span style="color:var(--sub)">오늘 배운 용어</span>';
        return '<div class="titem'+(hl===x.term?' hl':'')+'"><div class="k"><i style="background:'+(COLORS[x.track]||"var(--c)")+'"></i>'+esc(x.term)+'</div><div class="d">'+esc(x.desc)+'</div><div class="s">'+link+'</div></div>';
      }).join(""):'<div class="empty">검색 결과가 없습니다.</div>';
      if(hl){var el=list.querySelector(".hl"); if(el) el.scrollIntoView({block:"nearest"});}
    };
    side.querySelectorAll(".tabs button").forEach(function(b){b.onclick=function(){
      side.querySelectorAll(".tabs button").forEach(function(x){x.classList.remove("on")}); b.classList.add("on"); mode=b.dataset.m; render();};});
    q.oninput=function(){render()};
    side.querySelector(".tabs [data-m=all]").textContent="전체 "+all.length;
    side.querySelector(".tabs [data-m=today]").textContent="오늘 "+todays.length;
    render();
    var hd=side.querySelector(".card-h"), cl=document.createElement("button"); cl.className="close"; cl.textContent="닫기";
    cl.onclick=function(){side.classList.remove("open")}; hd.appendChild(cl);
    var bd=document.createElement("div"); bd.className="backdrop"; bd.onclick=cl.onclick; side.after(bd);
    var openTerm=function(k){q.value="";mode="all";side.querySelectorAll(".tabs button").forEach(function(b){b.classList.toggle("on",b.dataset.m==="all")});render(k);side.classList.add("open");};
    var main=document.querySelector("main"), done={};
    if(main){
      var walker=document.createTreeWalker(main,NodeFilter.SHOW_TEXT,{acceptNode:function(n){
        var p=n.parentElement; if(!p||p.closest("pre,code,.term,h1,summary,#today-terms,.hero,.ptabs,.topbar,.choice,.eng-item .en,.phr,.tr dt")) return NodeFilter.FILTER_REJECT;
        return n.nodeValue.trim()?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;}});
      var nodes=[]; while(walker.nextNode()) nodes.push(walker.currentNode);
      var pairs=[]; all.forEach(function(x){var m=x.term.match(/^(.*?)\s*\((.*)\)\s*$/);(m?[m[1],m[2]]:[x.term]).forEach(function(k){if(k.length>=2&&!/^[a-z ]+$/.test(k)) pairs.push([k,x]);});});
      pairs.sort(function(a,b){return b[0].length-a[0].length});
      nodes.forEach(function(n){ for(var i=0;i<pairs.length;i++){ var k=pairs[i][0],x=pairs[i][1]; if(done[x.term]) continue;
        var idx=n.nodeValue.indexOf(k); if(idx<0) continue; done[x.term]=1;
        var after=n.splitText(idx); after.splitText(k.length);
        var sp=document.createElement("span"); sp.className="term"; sp.dataset.tip=x.desc; sp.dataset.k=x.term; sp.textContent=k;
        after.parentNode.replaceChild(sp,after); sp.onclick=function(){openTerm(this.dataset.k)}; break; }});
    }
    var fab=document.querySelector(".fab"); if(fab) fab.onclick=function(){side.classList.toggle("open")};
    document.addEventListener("keydown",function(e){ if(e.key==="/"&&document.activeElement!==q){e.preventDefault();q.focus();} if(e.key==="Escape") side.classList.remove("open"); });
  }

  /* 6) 모바일: 개발공부 섹션 탭 */
  var grid=document.querySelector('.panel[data-p=dev] .grid')||document.querySelector("main .grid"), steps=document.querySelectorAll(".hero .steps a");
  if(grid&&steps.length){
    var secs=[]; steps.forEach(function(a){secs.push({id:a.getAttribute("href").slice(1),label:a.textContent.replace(/^[^\s]+\s*/,"")})});
    var cur=secs[0].id;
    [].forEach.call(grid.children,function(el){ if(el.id&&secs.some(function(s){return s.id===el.id})) cur=el.id; el.dataset.sec=cur; });
    var nav=document.createElement("nav"); nav.className="mnav";
    nav.innerHTML=secs.map(function(s,i){return '<button data-s="'+s.id+'"><b>'+(i+1)+'</b>'+s.label+'</button>'}).join("")+'<button data-t="1"><b>📖</b>용어</button>';
    document.body.appendChild(nav);
    var sn=document.createElement("div"); sn.className="secnav"; sn.innerHTML='<button data-d="-1">← 이전</button><button class="pri" data-d="1">다음 →</button>'; grid.after(sn);
    var ix=0, mq=window.matchMedia("(max-width:720px)");
    var show=function(i,scroll){ ix=Math.max(0,Math.min(secs.length-1,i));
      [].forEach.call(grid.children,function(el){el.classList.toggle("on",el.dataset.sec===secs[ix].id)});
      nav.querySelectorAll("[data-s]").forEach(function(b,j){b.classList.toggle("on",j===ix)});
      sn.children[0].disabled=ix===0;
      sn.children[1].textContent=ix===secs.length-1?"다른 탭 보기: 커뮤니케이션 →":"다음: "+secs[ix+1].label+" →";
      if(scroll) window.scrollTo({top:grid.getBoundingClientRect().top+window.scrollY-70,behavior:"smooth"}); };
    nav.onclick=function(e){var b=e.target.closest("button"); if(!b) return; if(b.dataset.t){side&&side.classList.toggle("open");return;}
      show(secs.findIndex(function(s){return s.id===b.dataset.s}),true);};
    sn.onclick=function(e){var b=e.target.closest("button"); if(!b) return; var d=+b.dataset.d;
      if(d>0&&ix===secs.length-1){ if(tabs.length) openPanel("comm",true); return;} show(ix+d,true);};
    var apply=function(){ B.classList.toggle("mtabs",mq.matches); if(mq.matches) show(ix,false); };
    mq.addEventListener?mq.addEventListener("change",apply):mq.addListener(apply); apply();
  }
})();

/* 복사 버튼 */
document.querySelectorAll(".copy").forEach(function(b){b.onclick=function(){
  var t=b.dataset.t, done=function(){b.textContent="복사됨";setTimeout(function(){b.textContent="복사"},1200)};
  try{ if(navigator.clipboard){navigator.clipboard.writeText(t).then(done,function(){prompt("복사하세요",t)});} else {prompt("복사하세요",t);} }catch(e){prompt("복사하세요",t)}
};});
