// Ceylon Micro Credit - site scripts
document.getElementById("year").textContent = new Date().getFullYear();

function formatRs(n) {
  return "Rs. " + Math.round(n).toLocaleString("en-LK");
}

// Monthly instalment on a reducing balance: P*r*(1+r)^n / ((1+r)^n - 1)
function monthlyInstalment(principal, annualRate, months) {
  const r = annualRate / 12 / 100;
  if (!months) return 0;
  if (!r) return principal / months;
  const f = Math.pow(1 + r, months);
  return (principal * r * f) / (f - 1);
}

function initCalculator(applyUrl) {
  const product = document.getElementById("calcProduct");
  const amount = document.getElementById("calcAmount");
  const amountText = document.getElementById("calcAmountText");
  const term = document.getElementById("calcTerm");
  const termLabel = document.getElementById("calcTermLabel");
  const rate = document.getElementById("calcRate");
  if (!product || !product.options.length) return;

  function loadProduct() {
    const o = product.selectedOptions[0].dataset;
    const min = +o.min || 10000, max = +o.max || 1000000, maxTerm = +o.term || 60;
    amount.min = min; amount.max = max;
    amount.value = Math.round((min + max) / 4 / 10000) * 10000 || min;
    term.max = maxTerm;
    term.value = Math.min(12, maxTerm);
    rate.value = o.rate;
    amountText.value = amount.value;
    update();
  }

  function update() {
    const p = +amount.value, n = +term.value, r = +rate.value;
    const emi = monthlyInstalment(p, r, n);
    termLabel.textContent = n + " months";
    document.getElementById("calcEmi").textContent = formatRs(emi);
    document.getElementById("calcInterest").textContent = formatRs(emi * n - p);
    document.getElementById("calcTotal").textContent = formatRs(emi * n);
    document.getElementById("calcApply").href =
      applyUrl + "?product=" + encodeURIComponent(product.value) + "&amount=" + p + "&term=" + n;
  }

  product.addEventListener("change", loadProduct);
  amount.addEventListener("input", () => { amountText.value = amount.value; update(); });
  amountText.addEventListener("change", () => {
    const v = Math.min(Math.max(+amountText.value || 0, +amount.min), +amount.max);
    amountText.value = amount.value = v; update();
  });
  term.addEventListener("input", update);
  rate.addEventListener("input", update);
  loadProduct();
}

// Count-up animation for elements with data-count, started when they scroll into view
function initCounters() {
  const els = document.querySelectorAll("[data-count]");
  const run = (el) => {
    const target = parseFloat(String(el.dataset.count).replace(/,/g, "")) || 0;
    const start = performance.now(), duration = 1600;
    const step = (now) => {
      const t = Math.min((now - start) / duration, 1);
      el.textContent = Math.round(target * (1 - Math.pow(1 - t, 3))).toLocaleString("en-LK");
      if (t < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };
  if (!("IntersectionObserver" in window)) { els.forEach(run); return; }
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => { if (e.isIntersecting) { run(e.target); io.unobserve(e.target); } });
  }, { threshold: 0.4 });
  els.forEach((el) => io.observe(el));
}
