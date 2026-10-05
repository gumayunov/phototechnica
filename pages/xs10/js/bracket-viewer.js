(function(){
  // Переключатель кадров серии брекетинга: кнопки .seg внутри figure.bkv
  document.querySelectorAll('.bkv').forEach(function(box){
    var img=box.querySelector('.bkv-img'), cap=box.querySelector('.bkv-cap');
    var btns=box.querySelectorAll('.seg button');
    btns.forEach(function(b){
      var pre=new Image(); pre.src=b.dataset.src;
      b.addEventListener('click',function(){
        btns.forEach(function(x){x.setAttribute('aria-pressed','false')});
        b.setAttribute('aria-pressed','true');
        img.src=b.dataset.src; img.alt=b.dataset.alt; cap.textContent=b.dataset.cap;
      });
    });
  });
})();
