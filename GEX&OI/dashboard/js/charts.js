// ============================================================
// GEX & OI Dashboard — Chart Rendering (Plotly.js)
// ============================================================

const CHART_COLORS = {
  green:  '#10d98b',
  red:    '#f25757',
  blue:   '#38bdf8',
  gold:   '#f5c842',
  orange: '#fb923c',
  purple: '#a78bfa',
  text:   '#8896b0',
  grid:   '#1e2d45',
  bg:     '#151d2e',
  bg_alt: '#1a2235',
};

function getChartTheme() {
  const isLight = document.documentElement.getAttribute('data-theme') === 'light';
  return {
    bg:       isLight ? '#ffffff' : '#151d2e',
    paper_bg: isLight ? '#f8fafc' : '#111827',
    grid:     isLight ? '#e2e8f0' : '#1e2d45',
    text:     isLight ? '#475569' : '#8896b0',
    text_prim:isLight ? '#0f172a' : '#e8ecf4',
    green:    isLight ? '#059669' : '#10d98b',
    red:      isLight ? '#dc2626' : '#f25757',
    blue:     isLight ? '#0284c7' : '#38bdf8',
    gold:     isLight ? '#d97706' : '#f5c842',
    orange:   isLight ? '#ea580c' : '#fb923c',
    purple:   isLight ? '#7c3aed' : '#a78bfa',
  };
}

const LAYOUT_BASE = () => {
  const t = getChartTheme();
  return {
    plot_bgcolor:  t.bg,
    paper_bgcolor: t.paper_bg,
    font:          { family: "'JetBrains Mono', 'Fira Code', monospace", color: t.text, size: 11 },
    margin:        { t: 20, r: 20, b: 50, l: 60 },
    hovermode:     'x unified',
    hoverlabel:    {
      bgcolor:     t.bg,
      bordercolor: t.blue,
      font:        { family: "'Inter', system-ui, sans-serif", size: 12 },
    },
    xaxis: {
      gridcolor:     t.grid,
      zerolinecolor: t.grid,
      tickfont:      { color: t.text },
      linecolor:     t.grid,
    },
    yaxis: {
      gridcolor:     t.grid,
      zerolinecolor: t.grid,
      tickfont:      { color: t.text },
      linecolor:     t.grid,
    },
    legend: {
      bgcolor:     'rgba(0,0,0,0)',
      font:        { color: t.text, size: 11 },
    },
  };
};

const PLOTLY_CONFIG = {
  displayModeBar: true,
  modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d', 'toggleSpikelines'],
  modeBarButtonsToAdd: [],
  displaylogo: false,
  responsive: true,
  scrollZoom: true,
};

// ============================================================
// GEX BY STRIKE
// ============================================================
function renderGEXChart(containerId, data) {
  const t = getChartTheme();
  const { strikes, gex_values } = data.gex_by_strike;
  const spot = data.spot;

  const colors = gex_values.map(v => v >= 0 ? t.green : t.red);
  const opacities = gex_values.map(v => Math.min(1.0, 0.3 + Math.abs(v) / Math.max(...gex_values.map(Math.abs)) * 0.7));

  const trace = {
    x: strikes,
    y: gex_values,
    type: 'bar',
    name: 'GEX ($B)',
    marker: {
      color: colors,
      opacity: opacities,
      line: { color: colors, width: 0.5 },
    },
    hovertemplate: '<b>Strike %{x:,}</b><br>GEX: $%{y:.3f}B<extra></extra>',
  };

  const layout = {
    ...LAYOUT_BASE(),
    title: '',
    xaxis: {
      ...LAYOUT_BASE().xaxis,
      title: { text: 'Strike', font: { color: t.text, size: 10 } },
      tickformat: ',',
    },
    yaxis: {
      ...LAYOUT_BASE().yaxis,
      title: { text: 'GEX ($B)', font: { color: t.text, size: 10 } },
      zeroline: true,
      zerolinecolor: t.text,
      zerolinewidth: 1.5,
    },
    shapes: [
      // Spot line
      {
        type: 'line', x0: spot, x1: spot, y0: 0, y1: 1, yref: 'paper',
        line: { color: t.blue, width: 1.5, dash: 'dot' },
      },
      // Key levels
      ...buildGEXShapes(data, t),
    ],
    annotations: [
      {
        x: spot, y: 1.05, yref: 'paper', xref: 'x',
        text: `SPOT ${Number(spot).toLocaleString(undefined, {minimumFractionDigits:1, maximumFractionDigits:1})}`,
        showarrow: false,
        font: { color: t.blue, size: 10, family: "'JetBrains Mono', monospace" },
      },
    ],
    bargap: 0.15,
  };

  Plotly.newPlot(containerId, [trace], layout, PLOTLY_CONFIG);
}

function buildGEXShapes(data, t) {
  const m = data.metrics;
  const shapes = [];
  const levels = [
    { v: m.call_wall,       color: t.red,    dash: 'dash',   label: 'CW' },
    { v: m.put_wall,        color: t.green,  dash: 'dash',   label: 'PW' },
    { v: m.max_gex_strike,  color: t.gold,   dash: 'dot',    label: 'PIN' },
    { v: m.zero_gex_strike, color: t.orange, dash: 'dashdot',label: 'ZGEX' },
  ];
  levels.forEach(l => {
    shapes.push({
      type: 'line', x0: l.v, x1: l.v, y0: 0, y1: 1, yref: 'paper',
      line: { color: l.color, width: 1, dash: l.dash },
    });
  });
  return shapes;
}

// ============================================================
// OI DISTRIBUTION
// ============================================================
function renderOIChart(containerId, data) {
  const t = getChartTheme();
  const { strikes, call_oi, put_oi } = data.oi_by_strike;
  const spot = data.spot;

  const calls_trace = {
    x: call_oi,
    y: strikes,
    type: 'bar',
    orientation: 'h',
    name: 'Call OI',
    marker: { color: t.red, opacity: 0.75 },
    hovertemplate: '<b>Strike %{y:,}</b><br>Call OI: %{x:,}<extra></extra>',
  };

  const puts_trace = {
    x: put_oi.map(v => -v),
    y: strikes,
    type: 'bar',
    orientation: 'h',
    name: 'Put OI',
    marker: { color: t.green, opacity: 0.75 },
    hovertemplate: '<b>Strike %{y:,}</b><br>Put OI: %{customdata:,}<extra></extra>',
    customdata: put_oi,
  };

  const maxOI = Math.max(...call_oi, ...put_oi);

  const layout = {
    ...LAYOUT_BASE(),
    barmode: 'overlay',
    xaxis: {
      ...LAYOUT_BASE().xaxis,
      title: { text: 'Open Interest (Calls →  ← Puts)', font: { color: t.text, size: 10 } },
      range: [-maxOI * 1.15, maxOI * 1.15],
      tickformat: ',',
      zeroline: true,
      zerolinecolor: t.text,
      zerolinewidth: 1.5,
    },
    yaxis: {
      ...LAYOUT_BASE().yaxis,
      title: { text: 'Strike', font: { color: t.text, size: 10 } },
      tickformat: ',',
    },
    shapes: [
      {
        type: 'line', x0: 0, x1: 1, xref: 'paper', y0: spot, y1: spot,
        line: { color: t.blue, width: 1.5, dash: 'dot' },
      },
      {
        type: 'line', x0: 0, x1: 1, xref: 'paper',
        y0: data.metrics.max_pain, y1: data.metrics.max_pain,
        line: { color: t.purple, width: 1, dash: 'dash' },
      },
    ],
    annotations: [
      {
        x: maxOI * 1.1, y: spot, xref: 'x', yref: 'y',
        text: 'SPOT', showarrow: false,
        font: { color: t.blue, size: 9, family: "'JetBrains Mono', monospace" },
        xanchor: 'right',
      },
      {
        x: maxOI * 1.1, y: data.metrics.max_pain, xref: 'x', yref: 'y',
        text: 'MAX PAIN', showarrow: false,
        font: { color: t.purple, size: 9, family: "'JetBrains Mono', monospace" },
        xanchor: 'right',
      },
    ],
    bargap: 0.1,
    margin: { ...LAYOUT_BASE().margin, l: 80 },
  };

  Plotly.newPlot(containerId, [calls_trace, puts_trace], layout, PLOTLY_CONFIG);
}

// ============================================================
// VOLUME PROFILE (horizontal histogram)
// ============================================================
function renderVolProfileChart(containerId, data) {
  const t = getChartTheme();
  const vp = data.volume_profile;
  const { price_buckets, volume, poc, hvn_levels, lvn_levels } = vp;
  const spot = data.spot;

  if (!price_buckets || !volume) {
    document.getElementById(containerId).innerHTML =
      '<div class="empty-state"><div class="empty-state-icon">📊</div><div class="empty-state-text">Volume profile data unavailable for this instrument.</div></div>';
    return;
  }

  const maxVol = Math.max(...volume);

  const colors = price_buckets.map(p => {
    if (Math.abs(p - poc) < (vp.bucket_size || 5) / 2) return t.gold;
    if (hvn_levels && hvn_levels.some(h => Math.abs(p - h) < (vp.bucket_size || 5))) return t.green;
    if (lvn_levels && lvn_levels.some(l => Math.abs(p - l) < (vp.bucket_size || 5))) return t.red;
    return t.blue;
  });

  const trace = {
    x: volume,
    y: price_buckets,
    type: 'bar',
    orientation: 'h',
    name: 'Volume',
    marker: { color: colors, opacity: 0.7 },
    hovertemplate: '<b>Price %{y:,.1f}</b><br>Volume: %{x:,}<extra></extra>',
  };

  const shapes = [
    // Spot
    {
      type: 'line', x0: 0, x1: 1, xref: 'paper', y0: spot, y1: spot,
      line: { color: t.blue, width: 1.5, dash: 'dot' },
    },
    // POC
    {
      type: 'line', x0: 0, x1: 1, xref: 'paper', y0: poc, y1: poc,
      line: { color: t.gold, width: 1.5, dash: 'solid' },
    },
    // HVN
    ...(hvn_levels || []).filter(h => Math.abs(h - poc) > (vp.bucket_size || 5)).map(h => ({
      type: 'line', x0: 0, x1: 1, xref: 'paper', y0: h, y1: h,
      line: { color: t.green, width: 0.8, dash: 'dash' },
    })),
    // LVN
    ...(lvn_levels || []).map(l => ({
      type: 'line', x0: 0, x1: 1, xref: 'paper', y0: l, y1: l,
      line: { color: t.red, width: 0.8, dash: 'dot' },
    })),
  ];

  const annotations = [
    {
      x: maxVol * 1.05, y: poc, xref: 'x', yref: 'y',
      text: 'POC', showarrow: false,
      font: { color: t.gold, size: 9, family: "'JetBrains Mono', monospace" },
      xanchor: 'left',
    },
    {
      x: maxVol * 1.05, y: spot, xref: 'x', yref: 'y',
      text: 'SPOT', showarrow: false,
      font: { color: t.blue, size: 9, family: "'JetBrains Mono', monospace" },
      xanchor: 'left',
    },
  ];

  const layout = {
    ...LAYOUT_BASE(),
    xaxis: {
      ...LAYOUT_BASE().xaxis,
      title: { text: 'Volume', font: { color: t.text, size: 10 } },
      range: [0, maxVol * 1.2],
    },
    yaxis: {
      ...LAYOUT_BASE().yaxis,
      title: { text: 'Price', font: { color: t.text, size: 10 } },
      tickformat: ',',
    },
    shapes,
    annotations,
    bargap: 0.05,
    margin: { ...LAYOUT_BASE().margin, l: 80, r: 40 },
  };

  Plotly.newPlot(containerId, [trace], layout, PLOTLY_CONFIG);
}

// ============================================================
// COMBINED GEX + SPOT OVERLAY (for charts tab)
// ============================================================
function renderCombinedChart(containerId, data) {
  const t = getChartTheme();
  const { strikes, gex_values } = data.gex_by_strike;
  const spot = data.spot;
  const m = data.metrics;

  const colors = gex_values.map(v => v >= 0 ? t.green : t.red);

  const trace = {
    x: strikes,
    y: gex_values,
    type: 'bar',
    name: 'GEX ($B)',
    marker: { color: colors, opacity: 0.75 },
    hovertemplate: '<b>Strike %{x:,}</b><br>GEX: $%{y:.3f}B<extra></extra>',
  };

  const levelAnnotations = [
    { v: m.call_wall,       label: 'CALL WALL',  color: t.red },
    { v: m.put_wall,        label: 'PUT WALL',   color: t.green },
    { v: m.max_gex_strike,  label: 'MAX GEX',    color: t.gold },
    { v: m.zero_gex_strike, label: 'ZERO GEX',   color: t.orange },
    { v: m.max_pain,        label: 'MAX PAIN',   color: t.purple },
  ];

  const layout = {
    ...LAYOUT_BASE(),
    xaxis: {
      ...LAYOUT_BASE().xaxis,
      title: { text: 'Strike', font: { color: t.text, size: 10 } },
      tickformat: ',',
    },
    yaxis: {
      ...LAYOUT_BASE().yaxis,
      title: { text: 'GEX ($B)', font: { color: t.text, size: 10 } },
      zeroline: true,
      zerolinecolor: t.text,
      zerolinewidth: 1.5,
    },
    shapes: [
      { type: 'line', x0: spot, x1: spot, y0: 0, y1: 1, yref: 'paper',
        line: { color: t.blue, width: 2, dash: 'dot' } },
      ...levelAnnotations.map(l => ({
        type: 'line', x0: l.v, x1: l.v, y0: 0, y1: 1, yref: 'paper',
        line: { color: l.color, width: 1, dash: 'dash' },
      })),
    ],
    annotations: [
      { x: spot, y: 1.07, yref: 'paper', text: `● SPOT ${spot.toLocaleString()}`,
        showarrow: false, font: { color: t.blue, size: 9 } },
      ...levelAnnotations.map((l, i) => ({
        x: l.v, y: 1.03, yref: 'paper', text: l.label,
        showarrow: false, font: { color: l.color, size: 8 },
        textangle: -45,
      })),
    ],
    bargap: 0.15,
  };

  Plotly.newPlot(containerId, [trace], layout, PLOTLY_CONFIG);
}

// ============================================================
// RE-RENDER ALL VISIBLE CHARTS (theme toggle)
// ============================================================
function refreshAllCharts(instrument) {
  const data = window.GEX_OI_DATA && window.GEX_OI_DATA[instrument];
  if (!data) return;

  const chartMap = {
    'gex-chart':       () => renderGEXChart('gex-chart', data),
    'oi-chart':        () => renderOIChart('oi-chart', data),
    'vol-profile-chart': () => renderVolProfileChart('vol-profile-chart', data),
    'combined-chart':  () => renderCombinedChart('combined-chart', data),
  };

  Object.entries(chartMap).forEach(([id, fn]) => {
    if (document.getElementById(id)) fn();
  });
}
