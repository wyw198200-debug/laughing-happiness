const csvInput = document.getElementById('csvInput');
const filterColumn = document.getElementById('filterColumn');
const filterValue = document.getElementById('filterValue');
const applyFilterBtn = document.getElementById('applyFilter');
const clearFilterBtn = document.getElementById('clearFilter');
const xColumn = document.getElementById('xColumn');
const yColumn = document.getElementById('yColumn');
const chartType = document.getElementById('chartType');
const aggType = document.getElementById('aggType');
const renderChartBtn = document.getElementById('renderChart');
const dataTable = document.getElementById('dataTable');
const rowInfo = document.getElementById('rowInfo');

let originalRows = [];
let currentRows = [];
let headers = [];

function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (!lines.length) return { headers: [], rows: [] };

  const parseLine = (line) => {
    const result = [];
    let cur = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i += 1) {
      const ch = line[i];
      if (ch === '"') {
        if (inQuotes && line[i + 1] === '"') {
          cur += '"';
          i += 1;
        } else {
          inQuotes = !inQuotes;
        }
      } else if (ch === ',' && !inQuotes) {
        result.push(cur.trim());
        cur = '';
      } else {
        cur += ch;
      }
    }
    result.push(cur.trim());
    return result;
  };

  const headers = parseLine(lines[0]);
  const rows = lines.slice(1).filter(Boolean).map((line) => {
    const values = parseLine(line);
    const row = {};
    headers.forEach((h, idx) => {
      row[h] = values[idx] ?? '';
    });
    return row;
  });

  return { headers, rows };
}

function fillSelectOptions(columns) {
  [filterColumn, xColumn, yColumn].forEach((selectEl) => {
    selectEl.innerHTML = '';
    columns.forEach((col) => {
      const option = document.createElement('option');
      option.value = col;
      option.textContent = col;
      selectEl.appendChild(option);
    });
  });
}

function renderTable(rows) {
  if (!rows.length || !headers.length) {
    dataTable.innerHTML = '<tr><td>无数据</td></tr>';
    return;
  }

  const thead = `<thead><tr>${headers.map((h) => `<th>${h}</th>`).join('')}</tr></thead>`;
  const tbodyRows = rows.slice(0, 200).map(
    (row) => `<tr>${headers.map((h) => `<td>${row[h]}</td>`).join('')}</tr>`,
  );
  dataTable.innerHTML = `${thead}<tbody>${tbodyRows.join('')}</tbody>`;
}

function toNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
}

function aggregate(rows, xKey, yKey, method) {
  const groups = new Map();

  rows.forEach((row) => {
    const key = row[xKey];
    if (!groups.has(key)) {
      groups.set(key, { values: [], count: 0 });
    }
    const cell = groups.get(key);
    cell.count += 1;
    const n = toNumber(row[yKey]);
    if (n !== null) {
      cell.values.push(n);
    }
  });

  const x = [];
  const y = [];

  groups.forEach((meta, key) => {
    let value = 0;
    if (method === 'count') {
      value = meta.count;
    } else if (method === 'avg') {
      value = meta.values.length
        ? meta.values.reduce((s, n) => s + n, 0) / meta.values.length
        : 0;
    } else {
      value = meta.values.reduce((s, n) => s + n, 0);
    }

    x.push(key);
    y.push(Number(value.toFixed(2)));
  });

  return { x, y };
}

function renderChart(rows) {
  if (!rows.length) return;

  const xKey = xColumn.value;
  const yKey = yColumn.value;
  const type = chartType.value;
  const agg = aggType.value;

  const { x, y } = aggregate(rows, xKey, yKey, agg);

  const trace = {
    x,
    y,
    type,
    mode: type === 'line' ? 'lines+markers' : 'markers',
    marker: { color: '#60a5fa' },
    line: { color: '#93c5fd' },
  };

  Plotly.newPlot(
    'chart',
    [trace],
    {
      paper_bgcolor: '#111827',
      plot_bgcolor: '#111827',
      font: { color: '#e5e7eb' },
      xaxis: { title: xKey },
      yaxis: { title: `${agg.toUpperCase()}(${yKey})` },
      margin: { t: 32, r: 16, b: 56, l: 56 },
    },
    { responsive: true },
  );
}

function applyFilter() {
  const col = filterColumn.value;
  const keyword = filterValue.value.trim().toLowerCase();
  if (!col || !keyword) {
    currentRows = [...originalRows];
  } else {
    currentRows = originalRows.filter((row) => String(row[col]).toLowerCase().includes(keyword));
  }
  rowInfo.textContent = `当前 ${currentRows.length} 行 / 原始 ${originalRows.length} 行`;
  renderTable(currentRows);
  renderChart(currentRows);
}

csvInput.addEventListener('change', async (event) => {
  const [file] = event.target.files;
  if (!file) return;
  const text = await file.text();
  const parsed = parseCSV(text);
  headers = parsed.headers;
  originalRows = parsed.rows;
  currentRows = [...originalRows];

  fillSelectOptions(headers);
  rowInfo.textContent = `当前 ${currentRows.length} 行 / 原始 ${originalRows.length} 行`;
  renderTable(currentRows);
  renderChart(currentRows);
});

applyFilterBtn.addEventListener('click', applyFilter);
clearFilterBtn.addEventListener('click', () => {
  filterValue.value = '';
  currentRows = [...originalRows];
  rowInfo.textContent = `当前 ${currentRows.length} 行 / 原始 ${originalRows.length} 行`;
  renderTable(currentRows);
  renderChart(currentRows);
});
renderChartBtn.addEventListener('click', () => renderChart(currentRows));
