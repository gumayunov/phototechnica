(function(){
  var SIMS={{gen:sims-json}};
  var CR={{gen:cr-json}};
  function $(i){return document.getElementById(i)}
  var scene='mill', a='provia', b='classic-chrome', cmp=false;
  var btns=$('simBtns');
  SIMS.forEach(function(s){
    var bt=document.createElement('button'); bt.type='button'; bt.textContent=s.name.replace(' (+Ye, +R, +G)','').replace(' / Стандарт','').replace(' / Яркий','').replace(' / Мягкий','').replace(' / Кино','');
    if(!s.xs) bt.className='na';
    bt.dataset.k=s.k;
    var timer=null;
    bt.addEventListener('click',function(e){ if(cmp&&e.shiftKey){b=s.k}else{a=s.k} upd(); });
    bt.addEventListener('contextmenu',function(e){ if(cmp){e.preventDefault(); b=s.k; upd();} });
    bt.addEventListener('touchstart',function(){ timer=setTimeout(function(){ if(cmp){b=s.k; timer='done'; upd();} },450); },{passive:true});
    bt.addEventListener('touchend',function(e){ if(timer==='done'){e.preventDefault();} else clearTimeout(timer); timer=null; });
    btns.appendChild(bt);
  });
  function sim(k){for(var i=0;i<SIMS.length;i++) if(SIMS[i].k===k) return SIMS[i];}
  function upd(){
    var sa=sim(a), sb=sim(b);
    $('imgA').src='img/'+scene+'-'+a+'.jpg'; $('imgA').alt=sa.name;
    $('imgB').src='img/'+scene+'-'+b+'.jpg'; $('imgB').alt=sb.name;
    $('vstage').style.aspectRatio = scene==='sheep' ? '16/9' : '3/2';
    $('imgB').hidden=!cmp; $('split').hidden=!cmp; $('tagB').hidden=!cmp; $('cmpRow').hidden=!cmp;
    $('tagA').textContent=sa.name+(sa.xs?'':' — нет на X-S10'); $('tagB').textContent=sb.name+(sb.xs?'':' — нет на X-S10');
    $('lblA').textContent=sa.name; $('lblB').textContent=sb.name;
    [].forEach.call(btns.children,function(x){x.classList.toggle('on',x.dataset.k===a); x.classList.toggle('b-on',cmp&&x.dataset.k===b);});
    $('vManual').textContent=sa.manual; $('vFilm').textContent=sa.film;
    $('vGood').textContent=sa.xs?sa.good:'—'; $('vTip').textContent=sa.tip;
    $('vCredit').innerHTML=CR[scene+'-'+a+'.jpg']||'';
  }
  function split(){var v=$('splitR').value; $('imgB').style.clipPath='inset(0 0 0 '+v+'%)'; $('split').style.left=v+'%';}
  $('splitR').addEventListener('input',split);
  $('cmpOn').addEventListener('change',function(){cmp=this.checked; upd(); split();});
  document.querySelectorAll('#sceneSeg button').forEach(function(x){x.addEventListener('click',function(){
    document.querySelectorAll('#sceneSeg button').forEach(function(y){y.setAttribute('aria-pressed','false')}); x.setAttribute('aria-pressed','true'); scene=x.dataset.s; upd();
  })});
  // drag on stage to move split
  var st=$('vstage'), drag=false;
  function setFromEvent(e){var r=st.getBoundingClientRect(), x=((e.touches?e.touches[0].clientX:e.clientX)-r.left)/r.width*100; $('splitR').value=Math.max(0,Math.min(100,x)); split();}
  st.addEventListener('mousedown',function(e){if(!cmp)return; drag=true; setFromEvent(e);});
  window.addEventListener('mousemove',function(e){if(drag) setFromEvent(e);});
  window.addEventListener('mouseup',function(){drag=false;});
  st.addEventListener('touchmove',function(e){if(cmp) setFromEvent(e);},{passive:true});
  upd(); split();
})();
