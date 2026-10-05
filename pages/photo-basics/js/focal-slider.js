  // Focal slider
  var FL=[17,24,35,50,70,100,135,200,300,500,1000,2000];
  var fImg=$('focalImg'), fRead=$('focalRead'), focalR=$('focalR');
  FL.forEach(function(m){var i=new Image();i.src='img/focal-'+m+'.jpg';});
  function upF(){
    var m=FL[focalR.value];
    fImg.src='img/focal-'+m+'.jpg';
    var aov=2*Math.atan(22.3/(2*m))*180/Math.PI;
    var a=aov>=10?Math.round(aov):aov.toFixed(1).replace('.',',');
    fRead.innerHTML=m+' мм<small>≈ '+Math.round(m*1.6)+' мм экв. · угол '+a+'°</small>';
  }
  focalR.addEventListener('input',upF); upF();
