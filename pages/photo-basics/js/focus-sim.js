  // Focus simulator
  (function(){
    var f=50, D=25, sMax=60, K=15, Fpx=160, SX=770, AX=150, A=55;
    var foc=$('fsFocus'), dist=$('fsDist');
    var pp=$('fsPetals');
    for(var k=0;k<14;k++){var e=document.createElementNS(ns,'ellipse');e.setAttribute('cy','-32');e.setAttribute('rx','8');e.setAttribute('ry','17');e.setAttribute('transform','rotate('+(k*360/14)+')');pp.appendChild(e);}
    $('fsPrevFlower').setAttribute('transform','translate(110,95)');
    function dOf(u){return 0.3*Math.pow(20/0.3,u/1000);} // metres
    function fmtM(m){return m>=10?Math.round(m)+' м':(m>=1?m.toFixed(1).replace('.',',').replace(',0','')+' м':Math.round(m*100)+' см');}
    function sOf(u){return f+(sMax-f)*Math.pow(u/10000,1.6);}
    function uOfS(s){return 10000*Math.pow(Math.max(0,(s-f)/(sMax-f)),1/1.6);}
    function vOf(dm){var d=dm*1000;return f*d/(d-f);}
    function rays(g,src,lensX,vpx){
      var h='';
      [-A,0,A].forEach(function(y0){
        var y1=AX+y0;
        h+= src==='inf' ? '<path d="M14,'+y1+' L'+lensX+','+y1+'"/>' : '<path d="M'+src+','+AX+' L'+lensX+','+y1+'"/>';
        var yS=AX+y0*(1-(SX-lensX)/vpx);
        h+='<path d="M'+lensX+','+y1+' L'+SX+','+yS.toFixed(1)+'"/>';
        if(lensX+vpx>SX) h+='<path d="M'+SX+','+yS.toFixed(1)+' L'+(lensX+vpx).toFixed(1)+','+AX+'" stroke-dasharray="4 4" opacity=".45"/>';
      });
      g.innerHTML=h;
      return Math.abs(A*(1-(SX-lensX)/vpx));
    }
    function verdict(c){return c<0.03?'резко ✓':(c<0.15?'почти резко':(c<0.6?'размыто':'сильно размыто'));}
    function upd(){
      var s=sOf(+foc.value), d=dOf(+dist.value), v=vOf(d);
      var spx=Fpx+K*(s-f), lensX=SX-spx;
      $('fsLens').setAttribute('transform','translate('+lensX+','+AX+')');
      $('fsF').setAttribute('transform','translate('+(lensX+Fpx)+','+AX+')');
      var xObj=610-(170+390*Math.log(d/0.3)/Math.log(20/0.3));
      $('fsFlower').setAttribute('transform','translate('+xObj+','+AX+')');
      var hInf=rays($('fsRaysInf'),'inf',lensX,Fpx);
      var hNear=rays($('fsRaysNear'),xObj,lensX,Fpx+K*(v-f));
      [['fsSpotInf',hInf],['fsSpotNear',hNear]].forEach(function(p){var r=$(p[0]),hh=Math.max(2,p[1]);r.setAttribute('y',AX-hh);r.setAttribute('height',2*hh);});
      $('fsDimL').setAttribute('x1',lensX);$('fsDimA').setAttribute('x1',lensX);$('fsDimA').setAttribute('x2',lensX);
      $('fsDimT').setAttribute('x',(lensX+SX)/2);
      $('fsDimT').textContent='от объектива до матрицы: '+s.toFixed(s-f<1?2:1).replace('.',',')+' мм';
      var fd = s-f<0.005 ? Infinity : f*s/(s-f)/1000;
      $('fsFocusO').textContent = fd===Infinity?'∞':(fd>200?'≈ ∞':'на '+fmtM(fd));
      $('fsExt').textContent = s-f<0.005 ? 'Объектив задвинут до упора: матрица ровно на фокусном расстоянии, 50 мм.' : 'Объектив выдвинут на '+(s-f).toFixed(s-f<1?2:1).replace('.',',')+' мм.';
      $('fsDistO').textContent=fmtM(d);
      $('fsV').textContent='Лучи от цветка сходятся в '+v.toFixed(v-f<1?2:1).replace('.',',')+' мм за линзой.';
      var cInf=D*(s-f)/f, cNear=D*Math.abs(s-v)/v;
      $('fsBgN').setAttribute('stdDeviation',Math.min(16,cInf*8).toFixed(2));
      $('fsFgN').setAttribute('stdDeviation',Math.min(16,cNear*8).toFixed(2));
      $('fsVerInf').textContent=verdict(cInf); $('fsVerNear').textContent=verdict(cNear);
    }
    foc.addEventListener('input',upd); dist.addEventListener('input',upd);
    $('fsInf').addEventListener('click',function(){foc.value=0;upd();});
    $('fsNear').addEventListener('click',function(){foc.value=Math.round(uOfS(vOf(dOf(+dist.value))));upd();});
    upd();
  })();

