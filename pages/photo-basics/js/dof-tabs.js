  // DOF tabs
  var dofCaps={
    'img/dof-f1-4.jpg':'f/1.4: резкость только на первом кубике, остальные тают в размытии.',
    'img/dof-f4.jpg':'f/4: резкой стала пара кубиков, дальние всё ещё мягкие.',
    'img/dof-f22.jpg':'f/22: читается почти каждая буква — от первого до последнего кубика.'
  };
  var dofImg=document.getElementById('dofImg'), dofCap=document.getElementById('dofCap');
  var crHtml=dofCap.querySelector('.cr') ? dofCap.querySelector('.cr').outerHTML : '';
  document.querySelectorAll('#dofSeg button').forEach(function(b){
    b.addEventListener('click',function(){
      document.querySelectorAll('#dofSeg button').forEach(function(x){x.setAttribute('aria-pressed','false')});
      b.setAttribute('aria-pressed','true');
      dofImg.src=b.dataset.src; dofCap.innerHTML=dofCaps[b.dataset.src]+crHtml;
    });
  });
  ['img/dof-f4.jpg','img/dof-f22.jpg'].forEach(function(s){var i=new Image();i.src=s;});

