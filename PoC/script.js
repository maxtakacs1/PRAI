document.getElementById('pocForm').addEventListener('submit', async e => {
  e.preventDefault();
  const form = e.target;
  const data = new FormData(form);

  const res = await fetch('/poc/invoke', { method: 'POST', body: data });
  if (!res.ok) {
    alert('Error: ' + res.statusText);
    return;
  }
  const json = await res.json();
  document.getElementById('info_sheet').textContent = json.info_sheet;
  document.getElementById('final_draft').textContent = json.final_draft;
});

// view in new window
document.getElementById('viewBtn').addEventListener('click', () => {
  const content = document.getElementById('final_draft').textContent;
  const w = window.open('', '_blank');
  w.document.write('<pre>' + content + '</pre>');
  w.document.close();
});

// download as PDF
document.getElementById('downloadBtn').addEventListener('click', () => {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF();
  const content = document.getElementById('final_draft').textContent;
  const lines = doc.splitTextToSize(content, 180);
  doc.text(lines, 10, 10);
  doc.save('final_draft.pdf');
});
