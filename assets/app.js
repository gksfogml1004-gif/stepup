/* 공부 페이지 공통 스크립트: 용어 사이드바 + 본문 용어 하이라이트 */
(function(){
  var T = (window.TERMS || []), ROOT = document.body.dataset.root || "", TODAY = document.body.dataset.path || "";
  var COLORS = {dev:"var(--dev)",db:"var(--db)",server:"var(--server)",net:"var(--net)",sm:"var(--sm)",review:"var(--review)"};
  var NAMES = {dev:"개발",db:"DB",server:"서버",net:"네트워크",sm:"SM",review:"복습"};
  // 오늘 페이지 용어는 페이지 안 <dl id="today-terms">가 기준 (아직 빌드 전이어도 보이게)
  var todays = [];
  document.querySelectorAll("#today-terms dt").forEach(function(dt){
    todays.push({term:dt.textContent.trim(), desc:dt.nextElementSibling.textContent.trim(), track:document.body.className.split(" ")[0], date:"오늘", path:TODAY});
  });
  var all = T.filter(function(x){return x.path!==TODAY}).concat(todays);
  function keys(t){ var m=t.match(/^(.*?)\s*\((.*)\)\s*$/); return m?[m[1],m[2]]:[t]; }
  function esc(s){return s.replace(/[&<>"]/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}

  var side = document.getElementById("side"); if(!side) return;
  var list = side.querySelector(".tlist"), q = side.querySelector(".search"), mode = "today";
  function render(hl){
    var s = q.value.trim().toLowerCase();
    var src = (mode==="today" && !s) ? todays : all;
    var rows = src.filter(function(x){return !s || (x.term+" "+x.desc).toLowerCase().indexOf(s)>=0})
      .sort(function(a,b){return mode==="today"&&!s?0:a.term.localeCompare(b.term,"ko")});
    list.innerHTML = rows.length ? rows.map(function(x){
      var link = x.path && x.path!==TODAY ? '<a href="'+ROOT+esc(x.path)+'">'+esc(x.date)+' · '+NAMES[x.track]+'에서 배움 →</a>' : '<span style="color:var(--sub)">오늘 배운 용어</span>';
      return '<div class="titem'+(hl===x.term?' hl':'')+'" data-k="'+esc(x.term)+'"><div class="k"><i style="background:'+COLORS[x.track]+'"></i>'+esc(x.term)+'</div><div class="d">'+esc(x.desc)+'</div><div class="s">'+link+'</div></div>';
    }).join("") : '<div class="empty">검색 결과가 없습니다.</div>';
    if(hl){ var el=list.querySelector(".hl"); if(el) el.scrollIntoView({block:"nearest"}); }
  }
  side.querySelectorAll(".tabs button").forEach(function(b){ b.onclick=function(){
    side.querySelectorAll(".tabs button").forEach(function(x){x.classList.remove("on")}); b.classList.add("on"); mode=b.dataset.m; render(); };});
  q.oninput=function(){render()};
  side.querySelector(".tabs [data-m=all]").textContent = "전체 "+all.length;
  side.querySelector(".tabs [data-m=today]").textContent = "오늘 "+todays.length;
  render();

  // 본문 용어 하이라이트 (용어별 첫 등장 1회, 코드 블록 제외)
  var main = document.querySelector("main"); if(!main) return;
  var done = {};
  var walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT, {acceptNode:function(n){
    var p=n.parentElement; if(!p||p.closest("pre,code,.term,h1,summary,#today-terms,.hero")) return NodeFilter.FILTER_REJECT;
    return n.nodeValue.trim()?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT;}});
  var nodes=[]; while(walker.nextNode()) nodes.push(walker.currentNode);
  var pairs=[]; all.forEach(function(x){keys(x.term).forEach(function(k){ if(k.length>=2) pairs.push([k,x]); });});
  pairs.sort(function(a,b){return b[0].length-a[0].length});
  nodes.forEach(function(n){
    for(var i=0;i<pairs.length;i++){
      var k=pairs[i][0], x=pairs[i][1]; if(done[x.term]) continue;
      var idx=n.nodeValue.indexOf(k); if(idx<0) continue;
      done[x.term]=1;
      var after=n.splitText(idx); after.splitText(k.length);
      var sp=document.createElement("span"); sp.className="term"; sp.dataset.tip=x.desc; sp.dataset.k=x.term; sp.textContent=k;
      after.parentNode.replaceChild(sp,after);
      sp.onclick=function(){ q.value=""; mode="all"; side.querySelectorAll(".tabs button").forEach(function(b){b.classList.toggle("on",b.dataset.m==="all")}); render(this.dataset.k); side.classList.add("open"); };
      break;
    }
  });
  var fab=document.querySelector(".fab"); if(fab) fab.onclick=function(){side.classList.toggle("open")};
  document.addEventListener("keydown",function(e){ if(e.key==="/"&&document.activeElement!==q){e.preventDefault();q.focus();} if(e.key==="Escape") side.classList.remove("open"); });
})();

/* 모바일: 섹션 탭 + 바텀시트 용어 사전 */
(function(){
  var grid=document.querySelector("main .grid"), steps=document.querySelectorAll(".hero .steps a"), side=document.getElementById("side");
  if(side){
    var h=side.querySelector(".card-h"), c=document.createElement("button"); c.className="close"; c.textContent="닫기";
    c.onclick=function(){side.classList.remove("open")}; h.appendChild(c);
    var bd=document.createElement("div"); bd.className="backdrop"; bd.onclick=c.onclick; side.after(bd);
  }
  if(!grid||!steps.length) return;
  var secs=[]; steps.forEach(function(a){secs.push({id:a.getAttribute("href").slice(1),label:a.textContent.replace(/^[^\s]+\s*/,"")})});
  var cur=secs[0].id;
  [].forEach.call(grid.children,function(el){ if(el.id&&secs.some(function(s){return s.id===el.id})) cur=el.id; el.dataset.sec=cur; });
  var nav=document.createElement("nav"); nav.className="mnav";
  nav.innerHTML=secs.map(function(s,i){return '<button data-s="'+s.id+'"><b>'+(i+1)+'</b>'+s.label+'</button>'}).join("")+'<button data-t="1"><b>📖</b>용어</button>';
  document.body.appendChild(nav);
  var sn=document.createElement("div"); sn.className="secnav"; sn.innerHTML='<button data-d="-1">← 이전</button><button class="pri" data-d="1">다음 →</button>'; grid.after(sn);
  var idx=0, mq=window.matchMedia("(max-width:720px)");
  function show(i,scroll){
    idx=Math.max(0,Math.min(secs.length-1,i));
    [].forEach.call(grid.children,function(el){el.classList.toggle("on",el.dataset.sec===secs[idx].id)});
    nav.querySelectorAll("[data-s]").forEach(function(b,j){b.classList.toggle("on",j===idx)});
    sn.children[0].disabled=idx===0;
    sn.children[1].textContent=idx===secs.length-1?"메인으로 →":"다음: "+secs[idx+1].label+" →";
    if(scroll) window.scrollTo({top:grid.getBoundingClientRect().top+window.scrollY-10,behavior:"smooth"});
  }
  nav.onclick=function(e){var b=e.target.closest("button"); if(!b) return;
    if(b.dataset.t){side.classList.toggle("open");return;}
    show(secs.findIndex(function(s){return s.id===b.dataset.s}),true);};
  sn.onclick=function(e){var b=e.target.closest("button"); if(!b) return; var d=+b.dataset.d;
    if(d>0&&idx===secs.length-1){location.href=(document.body.dataset.root||"")+"index.html";return;} show(idx+d,true);};
  function apply(){ document.body.classList.toggle("mtabs",mq.matches); if(mq.matches) show(idx,false); }
  mq.addEventListener?mq.addEventListener("change",apply):mq.addListener(apply); apply();
})();
