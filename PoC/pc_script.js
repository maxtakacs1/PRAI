document.getElementById('pocForm').addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.target;
  const data = new FormData(form);

  const res = await fetch('/praipoc/invoke', { method: 'POST', body: data });
  if (!res.ok) {
    alert('Error: ' + res.statusText);
    return;
  }
  const json = await res.json();
  document.getElementById('info_sheet').innerHTML = marked.parse(json.info_sheet);
  document.getElementById('final_draft').innerHTML = marked.parse(json.final_draft);
  // keep raw markdown for PDF rendering
  window._latestDraft = json.final_draft;
});

// view in new window
document.getElementById('viewBtn').addEventListener('click', () => {
  const content = document.getElementById('final_draft').textContent;
  const w = window.open('', '_blank');
  if (!w) {
    alert('Unable to open window');
    return;
  }
  w.document.title = 'Final Draft';
  // ensure body exists
  w.document.body.innerHTML = '';
  const pre = w.document.createElement('pre');
  pre.textContent = content;
  pre.style.whiteSpace = 'pre-wrap';
  pre.style.padding = '1rem';
  w.document.body.appendChild(pre);
});

// download as PDF
document.getElementById('downloadBtn').addEventListener('click', () => {
  const md = window._latestDraft || '';
  const html = marked.parse(md);
  const wrapper = document.createElement('div');
  wrapper.className = 'markdown-body';
  wrapper.style.padding = '1rem';
  wrapper.innerHTML = html;
  document.body.appendChild(wrapper);

  const opt = {
    margin:       0.5,
    filename:     'final_draft.pdf',
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: 'in', format: 'letter', orientation: 'portrait' }
  };

  html2pdf().from(wrapper).set(opt).save().then(() => {
    document.body.removeChild(wrapper);
  });
});
