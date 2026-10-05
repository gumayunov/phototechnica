  // Sunflower petals
  var pg=document.getElementById('petals'), ns='http://www.w3.org/2000/svg';
  for(var k=0;k<16;k++){
    var e=document.createElementNS(ns,'ellipse');
    e.setAttribute('cx','0');e.setAttribute('cy','-40');e.setAttribute('rx','10');e.setAttribute('ry','22');
    e.setAttribute('transform','rotate('+(k*22.5)+')');pg.appendChild(e);
  }

