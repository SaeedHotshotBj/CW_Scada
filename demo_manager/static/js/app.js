document.addEventListener('DOMContentLoaded', () => {
  if (window.jalaliDatepicker) {
    jalaliDatepicker.startWatch({minDate:'attr', maxDate:'attr', time:true, separator:' '});
  }
  loadProducts();
  loadData();
});

async function loadProducts() {
  const res = await fetch('/api/products');
  const products = await res.json();
  const select = document.getElementById('product');
  products.forEach(p => {
    const o = document.createElement('option');
    o.value = p; o.textContent = p;
    select.appendChild(o);
  });
}

function money(n) {
  return Math.round(Number(n || 0)).toLocaleString('fa-IR');
}
function number(n) {
  return Number(n || 0).toLocaleString('fa-IR', {maximumFractionDigits:2});
}

async function loadData() {
  const q = new URLSearchParams({
    start: document.getElementById('start').value,
    end: document.getElementById('end').value,
    product: document.getElementById('product').value
  });
  const res = await fetch('/api/manager_data?' + q.toString());
  const data = await res.json();
  document.getElementById('message').textContent = data.message || '';
  const s = data.summary || {};
  document.getElementById('sumWeight').textContent = number(s.weight);
  document.getElementById('sumMeters').textContent = number(s.meters);
  document.getElementById('sumWeightAmount').textContent = money(s.weight_amount);
  document.getElementById('sumMeterAmount').textContent = money(s.meter_amount);
  document.getElementById('sumTotal').textContent = money(s.total);

  const body = document.getElementById('rows');
  body.innerHTML = '';
  (data.rows || []).forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${r.date}</td><td>${r.product}</td><td>${number(r.weight)}</td><td>${money(r.weight_price)}</td><td>${money(r.weight_amount)}</td><td>${number(r.meters)}</td><td>${money(r.meter_price)}</td><td>${money(r.meter_amount)}</td><td><strong>${money(r.total)}</strong></td>`;
    body.appendChild(tr);
  });
}
