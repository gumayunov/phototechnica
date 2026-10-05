  // Simulator
  var F=[1.4,2,2.8,4,5.6,8,11,16,22];
  var T=[1/4000,1/2000,1/1000,1/500,1/250,1/125,1/60,1/30,1/15,1/8,1/4,1/2,1];
  var TL=['1/4000','1/2000','1/1000','1/500','1/250','1/125','1/60','1/30','1/15','1/8','1/4','1/2','1 с'];
  var ISO=[100,200,400,800,1600,3200,6400,12800];
  var sceneEV=12;
  var fR=document.getElementById('fR'), tR=document.getElementById('tR'), iR=document.getElementById('iR');
  var svg=document.getElementById('simSvg');
  function $(id){return document.getElementById(id)}
  function verdictText(d){
    if(d>2.5) return ['Сильный пересвет — всё белое','var(--t)'];
    if(d>1.2) return ['Пересвет','var(--t)'];
    if(d>0.5) return ['Чуть светловато','var(--muted)'];
    if(d>=-0.5) return ['Норма ✓','var(--iso)'];
    if(d>=-1.2) return ['Чуть темновато','var(--muted)'];
    if(d>=-2.5) return ['Недосвет','var(--f)'];
    return ['Сильный недосвет — почти чёрный','var(--f)'];
  }
  function update(){
    var N=F[fR.value], t=T[tR.value], iso=ISO[iR.value];
    var settingsEV=Math.log2(N*N/t)-Math.log2(iso/100);
    var d=sceneEV-settingsEV; // >0 overexposed
    $('fO').textContent='f/'+N; $('tO').textContent=TL[tR.value]; $('iO').textContent=iso;
    // brightness
    var b=Math.pow(2,d*0.6);
    var contrast = d>1 ? 1+ (d-1)*0.15 : 1;
    svg.style.filter='brightness('+b.toFixed(3)+') contrast('+contrast.toFixed(2)+')';
    // bg blur
    var blur=Math.max(0,9*1.4/N-0.5);
    $('bgBlurN').setAttribute('stdDeviation',blur.toFixed(2));
    // motion blur: ball moves ~1500 px/s
    var mb=Math.min(70,1500*t/2.2);
    $('motionN').setAttribute('stdDeviation',mb.toFixed(2)+' 0');
    // noise
    var stops=Math.log2(iso/100);
    var nOp=stops<=0?0:Math.min(0.85,0.05+stops*0.11);
    if(d<0) nOp=Math.min(0.9,nOp+(-d)*0.04);
    $('noiseRect').setAttribute('opacity',nOp.toFixed(2));
    // meter
    var clamped=Math.max(-3,Math.min(3,d));
    $('needle').style.left=((clamped+3)/6*100)+'%';
    var v=verdictText(d); $('verdict').textContent=v[0]; $('verdict').style.color=v[1];
    // hints
    $('fS').textContent = N<=2.8?'Дырка большая: много света, тонкая резкость':(N>=11?'Дырка маленькая: мало света, резко всё':'Средняя дырка: баланс');
    $('tS').textContent = t<=1/1000?'Очень коротко: заморозит что угодно':(t>=1/30?'Долго: всё движущееся смажется, нужен штатив':'Обычная скорость для прогулки');
    $('iS').textContent = iso<=200?'Без усиления: самая чистая картинка':(iso>=3200?'Сильное усиление: заметный шум':'Умеренное усиление');
    $('eBg').textContent = blur>5?'сильно размыт — портретный вид':(blur>2?'слегка размыт':(blur>0.6?'почти резкий':'резкий, как и цветок'));
    $('eBall').textContent = mb<2?'заморожен в воздухе':(mb<8?'чуть смазан':(mb<30?'заметный шлейф':'превратился в полосу'));
    $('eNoise').textContent = nOp<0.08?'нет':(nOp<0.3?'лёгкое зерно':(nOp<0.55?'заметный':'сильный'));
  }
  [fR,tR,iR].forEach(function(r){r.addEventListener('input',update)});
  document.querySelectorAll('#sceneSeg button').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('#sceneSeg button').forEach(function(x){x.setAttribute('aria-pressed','false')});
      b.setAttribute('aria-pressed','true'); sceneEV=+b.dataset.ev; update();
    });
  });
  $('autoIso').addEventListener('click',function(){
    var N=F[fR.value], t=T[tR.value];
    var need=Math.log2(N*N/t)-sceneEV; // stops of ISO needed above 100
    var idx=Math.round(need); idx=Math.max(0,Math.min(ISO.length-1,idx));
    iR.value=idx; update();
  });
  update();


