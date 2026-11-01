(function(){
var d=document,css=d.getElementById('fullcss');if(css)css.media='all';
var mb=d.querySelector('.menu-btn'),mn=d.getElementById('mnav');
if(mb&&mn){mb.addEventListener('click',function(){var o=mn.classList.toggle('open');mb.setAttribute('aria-expanded',o)})}
d.querySelectorAll('.nav button.dd').forEach(function(b){
b.addEventListener('click',function(e){e.stopPropagation();var li=b.parentNode,o=!li.classList.contains('open');
d.querySelectorAll('.nav li.open').forEach(function(x){x.classList.remove('open');x.querySelector('button').setAttribute('aria-expanded','false')});
if(o){li.classList.add('open');b.setAttribute('aria-expanded','true')}})});
d.addEventListener('click',function(){d.querySelectorAll('.nav li.open').forEach(function(x){x.classList.remove('open');x.querySelector('button').setAttribute('aria-expanded','false')})});
d.addEventListener('keydown',function(e){if(e.key==='Escape'){d.querySelectorAll('.nav li.open').forEach(function(x){x.classList.remove('open')})}});
window.dataLayer=window.dataLayer||[];
d.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a[href^="tel:"]');if(a){window.dataLayer.push({event:'call_click',link_location:a.getAttribute('data-loc')||'inline',page_path:location.pathname})}});
var mp=d.querySelector('[data-map]');if(mp){mp.querySelector('button').addEventListener('click',function(){var f=d.createElement('iframe');f.src=mp.getAttribute('data-map');f.width='100%';f.height='360';f.style.border='0';f.loading='lazy';f.title='Map of the Laurel Dry Pros service area';f.referrerPolicy='no-referrer-when-downgrade';mp.replaceWith(f)})}
var fm=d.getElementById('lead-form');if(fm){fm.addEventListener('submit',function(e){e.preventDefault();var m=fm.querySelector('.msg'),b=fm.querySelector('button');b.disabled=true;m.textContent='Sending…';
fetch('/api/contact',{method:'POST',body:new FormData(fm)}).then(function(r){return r.json().catch(function(){return{}}).then(function(j){return{ok:r.ok,j:j}})}).then(function(x){if(x.ok){m.textContent='Thanks. Your request was sent. For water in the home right now, please call us.';fm.reset();window.dataLayer.push({event:'form_submit'})}else{m.textContent=(x.j&&x.j.error)||'Sorry, that did not send. Please call us instead.'}b.disabled=false}).catch(function(){m.textContent='Sorry, that did not send. Please call us instead.';b.disabled=false})})}
})();
