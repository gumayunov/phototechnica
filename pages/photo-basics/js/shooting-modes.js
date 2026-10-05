  // Shooting modes P/A/S/M for the exposure simulator (uses F, T, ISO, fR, tR, iR, sceneEV, update from exposure-sim.js)
  (function(){
    var seg=$('modeSeg'); if(!seg) return;
    var mode='M';
    var HINTS={
      M:'M — ты ставишь и диафрагму, и выдержку. Камера только показывает стрелкой, хватает ли света.',
      A:'A — ты выбираешь диафрагму, а «камера» сама подбирает выдержку под норму. Попробуй открыть диафрагму.',
      S:'S — ты выбираешь выдержку, а «камера» сама подбирает диафрагму. Попробуй заморозить мяч.',
      P:'P — «камера» подбирает обе. Ползунком диафрагмы можно сдвинуть пару: выдержка подстроится.'
    };
    function needEV(){ return sceneEV+Math.log2(ISO[iR.value]/100); } // log2(N²/t) для нормальной яркости
    function nearest(arr,v){ var best=0; arr.forEach(function(x,i){ if(Math.abs(Math.log2(x/v))<Math.abs(Math.log2(arr[best]/v))) best=i; }); return best; }
    function followShutter(){ var N=F[fR.value]; tR.value=nearest(T,N*N/Math.pow(2,needEV())); }
    function followAperture(){ fR.value=nearest(F,Math.sqrt(T[tR.value]*Math.pow(2,needEV()))); }
    function program(){
      // средняя диафрагма и выдержка не длиннее 1/60, если света хватает
      var best=null;
      F.forEach(function(N,i){
        var ti=nearest(T,N*N/Math.pow(2,needEV())), miss=Math.abs(Math.log2(N*N/T[ti])-needEV());
        var score=miss*4+Math.abs(i-4.5)+(T[ti]>1/60?3:0);
        if(!best||score<best.s) best={s:score,f:i,t:ti};
      });
      fR.value=best.f; tR.value=best.t;
    }
    function apply(src){
      if(mode==='A') followShutter();
      else if(mode==='S') followAperture();
      else if(mode==='P'){ if(src===fR) followShutter(); else program(); }
      fR.disabled=(mode==='S');
      tR.disabled=(mode==='A'||mode==='P');
      $('modeHint').textContent=HINTS[mode];
      update();
    }
    seg.querySelectorAll('button').forEach(function(b){
      b.addEventListener('click',function(){
        seg.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed','false')});
        b.setAttribute('aria-pressed','true'); mode=b.dataset.mode; apply(null);
      });
    });
    [fR,tR,iR].forEach(function(r){ r.addEventListener('input',function(){ apply(r); }); });
    document.querySelectorAll('#sceneSeg button').forEach(function(b){ b.addEventListener('click',function(){ apply(null); }); });
    $('autoIso').addEventListener('click',function(){ apply(null); });
    apply(null);
  })();
