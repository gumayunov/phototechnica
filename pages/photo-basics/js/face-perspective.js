  // Face perspective demo
  (function(){
    var cv=$('faceCv'); if(!cv) return;
    var ctx=cv.getContext('2d'), W=cv.width, H=cv.height, img=ctx.createImageData(W,H);
    var FLS=[14,18,24,35,50,85,135,200];
    var TYPES={14:'сверхширокий, 0.5× телефона',18:'сверхширокий',24:'широкий, 1× телефона / селфи',35:'широкий-нормальный',50:'нормальный',85:'портретник',135:'длинный портретник',200:'телеобъектив'};
    // primitives: ellipsoids [cx,cy,cz, rx,ry,rz, kind]
    var P=[
      [0,0,0, .075,.105,.095,'head'],
      [0,-.012,.084, .015,.032,.03,'nose'],
      [.077,.002,-.006, .013,.032,.022,'ear'],[-.077,.002,-.006, .013,.032,.022,'ear'],
      [.031,.024,.073, .0125,.0125,.0125,'eye'],[-.031,.024,.073, .0125,.0125,.0125,'eye'],
      [0,-.15,-.01, .045,.07,.045,'neck'],
      [0,-.27,-.03, .21,.08,.11,'body']
    ];
    var L=[-.45,.55,.7], ll=Math.hypot(L[0],L[1],L[2]); L=[L[0]/ll,L[1]/ll,L[2]/ll];
    function color(kind,p,n){
      if(kind==='eye'){ var dx=p[0]-(p[0]>0?.031:-.031), dy=p[1]-.024; return (dx*dx+dy*dy<.0055*.0055)?[40,30,25]:[245,245,240]; }
      if(kind==='body') return [70,110,170];
      if(kind==='head'){
        if(p[1]>.05 || p[2]<-.035 || (p[1]>.02 && Math.abs(p[0])>.062)) return [92,58,34];
        if(p[1]>-.066 && p[1]<-.054 && Math.abs(p[0])<.024 && p[2]>0) return [190,90,90];
        if(p[1]>.043 && p[1]<.05 && Math.abs(p[0])>.015 && Math.abs(p[0])<.05 && p[2]>0) return [92,58,34];
      }
      return [236,190,160];
    }
    function render(fmm){
      var f=fmm/1000, D=f*0.50/0.036;
      var hw=0.024/2/f, hh=0.036/2/f, d=img.data;
      for(var j=0;j<H;j++){ for(var i=0;i<W;i++){
        var dx=((i+.5)/W*2-1)*hw, dy=(1-(j+.5)/H*2)*hh, dz=-1;
        var best=1e9, bp=-1;
        for(var k=0;k<P.length;k++){
          var e=P[k];
          var ox=(0-e[0])/e[3], oy=(0-e[1])/e[4], oz=(D-e[2])/e[5];
          var vx=dx/e[3], vy=dy/e[4], vz=dz/e[5];
          var a=vx*vx+vy*vy+vz*vz, b=2*(ox*vx+oy*vy+oz*vz), c=ox*ox+oy*oy+oz*oz-1, disc=b*b-4*a*c;
          if(disc<0) continue;
          var tt=(-b-Math.sqrt(disc))/(2*a);
          if(tt>0&&tt<best){best=tt;bp=k;}
        }
        var o=(j*W+i)*4;
        if(bp<0){ var g=225-j*.15; d[o]=g-25;d[o+1]=g-10;d[o+2]=g;d[o+3]=255; continue; }
        var e=P[bp], px=dx*best, py=dy*best, pz=D+dz*best;
        var nx=(px-e[0])/(e[3]*e[3]), ny=(py-e[1])/(e[4]*e[4]), nz=(pz-e[2])/(e[5]*e[5]), nl=Math.hypot(nx,ny,nz);
        nx/=nl;ny/=nl;nz/=nl;
        var lam=Math.max(0,nx*L[0]+ny*L[1]+nz*L[2]), sh=.38+.68*lam;
        var c0=color(e[6],[px,py,pz],[nx,ny,nz]);
        d[o]=Math.min(255,c0[0]*sh);d[o+1]=Math.min(255,c0[1]*sh);d[o+2]=Math.min(255,c0[2]*sh);d[o+3]=255;
      }}
      ctx.putImageData(img,0,0);
      return D;
    }
    function upd(){
      var fmm=FLS[$('faceR').value], D=render(fmm);
      $('faceO').textContent=fmm+' мм';
      $('faceD').textContent=D<1?Math.round(D*100)+' см':D.toFixed(1).replace('.',',')+' м';
      $('faceX').textContent='≈ '+Math.round(fmm/1.5)+' мм на объективе';
      var big=((D+.006)/(D-.114)-1)*100;
      $('faceN').textContent=Math.round(big)+' %';
      $('faceT').textContent=TYPES[fmm];
    }
    $('faceR').addEventListener('input',upd); upd();
  })();

