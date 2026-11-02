// Search items by name, then show the selected item's price history for a chosen period.

const searchInput = document.getElementById('search');
const resultsList = document.getElementById('results');
const emptyState = document.getElementById('empty-state');
const itemPanel = document.getElementById('item-panel');
const itemNameTitle = document.getElementById('item-name');
const rangeButtons = document.querySelectorAll('#ranges button');
const noData = document.getElementById('no-data');
const chartCanvas = document.getElementById('chart');

let chart = null;
let searchTimer = null;
let selectedItem = null;  // { id, name }
let selectedDays = 30;

// ---------------------------------------------------------------- search

// Wait until the user stops typing for 300 ms before calling the API.
searchInput.addEventListener('input', () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(searchItems, 300);
});

async function searchItems() {
  const text = searchInput.value.trim();
  resultsList.innerHTML = '';
  if (text.length < 2) {
    return;
  }

  const response = await fetch(`/items?search=${encodeURIComponent(text)}`);
  const items = await response.json();

  for (const item of items) {
    const li = document.createElement('li');
    li.textContent = item.name;
    li.addEventListener('click', () => selectItem(item.item_id, item.name));
    resultsList.appendChild(li);
  }
}

function selectItem(itemId, name) {
  selectedItem = { id: itemId, name: name };
  resultsList.innerHTML = '';
  searchInput.value = name;
  itemNameTitle.textContent = name;
  emptyState.hidden = true;
  itemPanel.hidden = false;
  loadHistory();
}

// ---------------------------------------------------------------- period buttons

for (const button of rangeButtons) {
  button.addEventListener('click', () => {
    selectedDays = Number(button.dataset.days);
    for (const other of rangeButtons) {
      other.classList.toggle('active', other === button);
    }
    loadHistory();
  });
}

// ---------------------------------------------------------------- history

async function loadHistory() {
  const response = await fetch(`/items/${selectedItem.id}/history?days=${selectedDays}`);
  if (response.status === 404) {
    showNoData();
    return;
  }
  const history = await response.json();

  noData.hidden = true;
  chartCanvas.hidden = false;
  showStats(history);
  drawChart(history);
}

function showNoData() {
  noData.hidden = false;
  chartCanvas.hidden = true;
  for (const id of ['stat-current', 'stat-change', 'stat-low', 'stat-high', 'stat-quantity']) {
    document.getElementById(id).textContent = '-';
  }
  document.getElementById('stat-change').className = 'stat-value';
}

function showStats(history) {
  const prices = history.map((point) => point.min_price);
  const first = prices[0];
  const last = prices[prices.length - 1];
  const change = ((last - first) / first) * 100;

  document.getElementById('stat-current').textContent = formatMoney(last);
  document.getElementById('stat-low').textContent = formatMoney(Math.min(...prices));
  document.getElementById('stat-high').textContent = formatMoney(Math.max(...prices));
  document.getElementById('stat-quantity').textContent =
    history[history.length - 1].total_quantity.toLocaleString();

  const changeEl = document.getElementById('stat-change');
  changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
  changeEl.className = 'stat-value ' + (change > 0 ? 'up' : change < 0 ? 'down' : '');
}

// 1 gold = 100 silver = 10,000 copper. Shows "1,234g 56s 78c", skipping empty parts.
function formatMoney(copper) {
  const gold = Math.floor(copper / 10000);
  const silver = Math.floor((copper % 10000) / 100);
  const rest = copper % 100;

  const parts = [];
  if (gold) parts.push(`${gold.toLocaleString()}g`);
  if (silver) parts.push(`${silver}s`);
  if (rest || parts.length === 0) parts.push(`${rest}c`);
  return parts.join(' ');
}

// ---------------------------------------------------------------- chart

function drawChart(history) {
  const labels = history.map((point) =>
    new Date(point.time).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  );
  const goldPrices = history.map((point) => point.min_price / 10000);
  const quantities = history.map((point) => point.total_quantity);

  if (chart) {
    chart.destroy();
  }

  Chart.defaults.color = '#9a968a';
  Chart.defaults.borderColor = '#2a2f3a';

  chart = new Chart(chartCanvas, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Lowest price (gold)',
          data: goldPrices,
          borderColor: '#e0b44c',
          backgroundColor: 'rgba(224, 180, 76, 0.12)',
          fill: true,
          tension: 0.25,
          pointRadius: history.length > 60 ? 0 : 3,
          yAxisID: 'price',
        },
        {
          label: 'Quantity listed',
          data: quantities,
          borderColor: '#6f7a86',
          borderDash: [4, 4],
          pointRadius: 0,
          tension: 0.25,
          yAxisID: 'quantity',
        },
      ],
    },
    options: {
      interaction: { mode: 'index', intersect: false },
      plugins: {
        tooltip: {
          callbacks: {
            label: (context) =>
              context.dataset.yAxisID === 'price'
                ? `Price: ${formatMoney(Math.round(context.parsed.y * 10000))}`
                : `Listed: ${context.parsed.y.toLocaleString()}`,
          },
        },
      },
      scales: {
        x: { ticks: { maxTicksLimit: 8 } },
        price: { position: 'left', title: { display: true, text: 'Gold' } },
        quantity: {
          position: 'right',
          title: { display: true, text: 'Quantity' },
          grid: { drawOnChartArea: false },
        },
      },
    },
  });
}
