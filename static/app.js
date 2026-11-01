// Search items by name, then draw the selected item's price history.

const searchInput = document.getElementById('search');
const resultsList = document.getElementById('results');
const chartSection = document.getElementById('chart-section');
const itemNameTitle = document.getElementById('item-name');

let chart = null;
let searchTimer = null;

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
    li.addEventListener('click', () => showItem(item.item_id, item.name));
    resultsList.appendChild(li);
  }
}

async function showItem(itemId, name) {
  resultsList.innerHTML = '';
  searchInput.value = name;

  const response = await fetch(`/items/${itemId}/history`);
  const history = await response.json();

  itemNameTitle.textContent = name;
  chartSection.hidden = false;
  drawChart(history);
}

function drawChart(history) {
  const labels = history.map((point) => new Date(point.time).toLocaleString());
  const goldPrices = history.map((point) => point.min_price / 10000);  // copper -> gold
  const quantities = history.map((point) => point.total_quantity);

  if (chart) {
    chart.destroy();
  }

  chart = new Chart(document.getElementById('chart'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Lowest price (gold)',
          data: goldPrices,
          borderColor: '#c08a1e',
          yAxisID: 'price',
        },
        {
          label: 'Quantity listed',
          data: quantities,
          borderColor: '#9aa4ad',
          borderDash: [4, 4],
          yAxisID: 'quantity',
        },
      ],
    },
    options: {
      interaction: { mode: 'index', intersect: false },
      scales: {
        price: { position: 'left', title: { display: true, text: 'Gold' } },
        quantity: { position: 'right', title: { display: true, text: 'Quantity' }, grid: { drawOnChartArea: false } },
      },
    },
  });
}
