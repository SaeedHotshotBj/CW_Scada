document.addEventListener('input', function(e){
  if(e.target.matches('input[type=number]')) e.target.value=e.target.value.replace(/[^0-9.\-]/g,'');
});
