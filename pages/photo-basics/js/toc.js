  // Side TOC
  (function(){
    var list=$('tocList'); if(!list) return;
    var items=[], subs=[];
    document.querySelectorAll('.hero .chip').forEach(function(ch){
      var id=ch.getAttribute('href').slice(1), sec=document.getElementById(id); if(!sec) return;
      var dot=ch.querySelector('.dot'), acc=dot?dot.style.background:'';
      var num=(sec.querySelector('.sec-num')||{}).textContent||'';
      var li=document.createElement('li'); li.style.setProperty('--acc',acc);
      li.innerHTML='<a href="#'+id+'"><span class="n">'+num+'</span><span>'+ch.textContent.trim()+'</span></a>';
      var h3s=sec.querySelectorAll('h3'), sub=[];
      if(h3s.length){
        var ol=document.createElement('ol');
        h3s.forEach(function(h,k){
          if(!h.id) h.id=id+'-'+(k+1);
          var sli=document.createElement('li'); sli.innerHTML='<a href="#'+h.id+'">'+h.textContent.replace(/^\d+\.\s*/,'')+'</a>';
          ol.appendChild(sli); sub.push({el:h,li:sli});
        });
        li.appendChild(ol);
      }
      list.appendChild(li); items.push({el:sec,li:li,sub:sub});
    });
    var ext=document.createElement('li'); ext.innerHTML='<a href="{{url:fujisims}}" style="margin-top:10px;border-top:1px solid var(--line);border-radius:0;padding-top:12px"><span class="n">↗</span><span>Симуляции плёнки X-S10</span></a>'; list.appendChild(ext);
    var ticking=false;
    function onScroll(){
      ticking=false;
      var y=120, cur=null;
      items.forEach(function(it){ if(it.el.getBoundingClientRect().top<y) cur=it; });
      items.forEach(function(it){ it.li.classList.toggle('active',it===cur); });
      if(cur){
        var cs=null; cur.sub.forEach(function(s){ s.li.classList.remove('cur'); if(s.el.getBoundingClientRect().top<y) cs=s; });
        if(cs) cs.li.classList.add('cur');
        var a=cur.li.querySelector('a'), toc=$('toc');
        var r=a.getBoundingClientRect(), tr=toc.getBoundingClientRect();
        if(r.top<tr.top+30||r.bottom>tr.bottom-30) toc.scrollTop+=r.top-tr.top-60;
      }
    }
    window.addEventListener('scroll',function(){ if(!ticking){ticking=true;setTimeout(onScroll,60);} },{passive:true});
    onScroll();
  })();
