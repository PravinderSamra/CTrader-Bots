// ============================================================
// GEX & OI Dashboard — Application Logic
// ============================================================

// State
const STATE = {
  instrument: 'US500',
  section: 'charts',
  subSection: null,
  theme: 'dark',
};

const INSTRUMENTS = ['US500', 'XAUUSD', 'GER40', 'UK100'];

const SECTIONS = [
  { id: 'charts',   label: 'Charts',          icon: '📈' },
  { id: 'metrics',  label: 'Metrics',          icon: '⚡' },
  { id: 'oi',       label: 'Open Interest',    icon: '🎯' },
  { id: 'situation',label: 'Situation',        icon: '🧭' },
  { id: 'levels',   label: 'Key Levels',       icon: '📌' },
  { id: 'scenarios',label: 'Trade Scenarios',  icon: '🎲' },
];

const SITUATION_SUBSECTIONS = [
  { id: 'levels-table', label: 'Levels Table' },
  { id: 'narrative',    label: 'Narrative' },
  { id: 'vol-profile',  label: 'Volume Profile' },
  { id: 'confluence',   label: 'Confluence Matrix' },
];

// ============================================================
// INIT
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
  loadTheme();
  buildTopbar();
  buildSidebar();
  buildContent();
  switchInstrument(STATE.instrument, false);
});

// ============================================================
// THEME
// ============================================================
function loadTheme() {
  const saved = localStorage.getItem('gex-theme') || 'dark';
  STATE.theme = saved;
  applyTheme(saved, false);
}

function applyTheme(theme, save = true) {
  STATE.theme = theme;
  document.documentElement.setAttribute('data-theme', theme === 'light' ? 'light' : '');
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.title = theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode';
  if (btn) btn.textContent = theme === 'dark' ? '☀️' : '🌙';
  if (save) localStorage.setItem('gex-theme', theme);
}

function toggleTheme() {
  const next = STATE.theme === 'dark' ? 'light' : 'dark';
  applyTheme(next);
  // Re-render charts with new theme
  setTimeout(() => refreshAllCharts(STATE.instrument), 50);
}

// ============================================================
// BUILD TOPBAR
// ============================================================
function buildTopbar() {
  const tabsContainer = document.getElementById('instrument-tabs');
  if (!tabsContainer) return;
  tabsContainer.innerHTML = '';

  INSTRUMENTS.forEach(inst => {
    const data = window.GEX_OI_DATA && window.GEX_OI_DATA[inst];
    const regime = data ? data.metrics.regime : 'NEUTRAL';
    const regimeCls = regime === 'PINNED' ? 'badge-pinned' : regime === 'TRENDING' ? 'badge-trending' : 'badge-neutral';

    const tab = document.createElement('div');
    tab.className = `instrument-tab${inst === STATE.instrument ? ' active' : ''}`;
    tab.setAttribute('data-instrument', inst);
    tab.innerHTML = `
      <span>${inst}</span>
      <span class="tab-regime-badge ${regimeCls}">${regime}</span>
    `;
    tab.addEventListener('click', () => switchInstrument(inst));
    tabsContainer.appendChild(tab);
  });

  updateScanTime();
}

function updateScanTime() {
  const el = document.getElementById('scan-time');
  if (!el) return;
  const data = window.GEX_OI_DATA && window.GEX_OI_DATA[STATE.instrument];
  if (!data) { el.textContent = '—'; return; }
  try {
    const d = new Date(data.scan_time);
    el.textContent = `Last scan: ${d.toLocaleDateString('en-GB', {day:'2-digit',month:'short'})} ${d.toLocaleTimeString('en-GB', {hour:'2-digit',minute:'2-digit'})} BST`;
  } catch { el.textContent = data.scan_time || '—'; }
}

// ============================================================
// BUILD SIDEBAR
// ============================================================
function buildSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  sidebar.innerHTML = '';

  // Label
  const label = document.createElement('div');
  label.className = 'sidebar-section-label';
  label.textContent = 'Sections';
  sidebar.appendChild(label);

  SECTIONS.forEach(sec => {
    const tab = document.createElement('div');
    tab.className = `sidebar-tab${sec.id === STATE.section ? ' active' : ''}`;
    tab.setAttribute('data-section', sec.id);
    tab.innerHTML = `<span class="sidebar-tab-icon">${sec.icon}</span><span>${sec.label}</span>`;
    tab.addEventListener('click', () => switchSection(sec.id));
    sidebar.appendChild(tab);

    // Sub-tabs for Situation
    if (sec.id === 'situation') {
      SITUATION_SUBSECTIONS.forEach(sub => {
        const subTab = document.createElement('div');
        const isActive = STATE.section === 'situation' && STATE.subSection === sub.id;
        subTab.className = `sidebar-subtab${isActive ? ' active' : ''}`;
        subTab.setAttribute('data-subsection', sub.id);
        subTab.textContent = sub.label;
        subTab.addEventListener('click', (e) => {
          e.stopPropagation();
          switchSection('situation', sub.id);
        });
        sidebar.appendChild(subTab);
      });
    }
  });
}

// ============================================================
// BUILD CONTENT AREA
// ============================================================
function buildContent() {
  const area = document.getElementById('content-area');
  if (!area) return;
  area.innerHTML = `
    <div id="panel-charts"    class="panel"></div>
    <div id="panel-metrics"   class="panel"></div>
    <div id="panel-oi"        class="panel"></div>
    <div id="panel-situation" class="panel"></div>
    <div id="panel-levels"    class="panel"></div>
    <div id="panel-scenarios" class="panel"></div>
  `;
}

// ============================================================
// SWITCH INSTRUMENT
// ============================================================
function switchInstrument(inst, rerender = true) {
  STATE.instrument = inst;

  // Update topbar tabs
  document.querySelectorAll('.instrument-tab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-instrument') === inst);
  });

  updateScanTime();

  if (rerender) {
    renderCurrentPanel();
  } else {
    renderCurrentPanel();
  }
}

// ============================================================
// SWITCH SECTION
// ============================================================
function switchSection(sectionId, subSection = null) {
  STATE.section = sectionId;
  STATE.subSection = subSection || (sectionId === 'situation' ? SITUATION_SUBSECTIONS[0].id : null);

  // Update sidebar tabs
  document.querySelectorAll('.sidebar-tab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-section') === sectionId);
  });

  document.querySelectorAll('.sidebar-subtab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-subsection') === STATE.subSection);
  });

  // Show/hide sub-tabs
  const subTabs = document.querySelectorAll('.sidebar-subtab');
  subTabs.forEach(t => {
    t.style.display = sectionId === 'situation' ? '' : 'none';
  });

  // Show panel
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  const panel = document.getElementById(`panel-${sectionId}`);
  if (panel) panel.classList.add('active');

  renderCurrentPanel();
}

// ============================================================
// RENDER DISPATCHER
// ============================================================
function renderCurrentPanel() {
  const data = window.GEX_OI_DATA && window.GEX_OI_DATA[STATE.instrument];
  const panel = document.getElementById(`panel-${STATE.section}`);
  if (!panel) return;

  panel.classList.add('active');

  // Clear other panels
  document.querySelectorAll('.panel').forEach(p => {
    if (p.id !== `panel-${STATE.section}`) p.classList.remove('active');
  });

  if (!data) {
    panel.innerHTML = renderEmptyState();
    return;
  }

  switch (STATE.section) {
    case 'charts':    renderChartsPanel(panel, data); break;
    case 'metrics':   renderMetricsPanel(panel, data); break;
    case 'oi':        renderOIPanel(panel, data); break;
    case 'situation': renderSituationPanel(panel, data); break;
    case 'levels':    renderLevelsPanel(panel, data); break;
    case 'scenarios': renderScenariosPanel(panel, data); break;
  }
}

// ============================================================
// CHARTS PANEL
// ============================================================
function renderChartsPanel(panel, data) {
  panel.innerHTML = `
    <div class="content-header">
      <div>
        <div class="spot-strip">
          <div class="spot-instrument">${data.instrument}</div>
          <div class="spot-price">${fmtNum(data.spot)}</div>
          <div>
            <div class="spot-meta">GEX: ${fmtGex(data.metrics.net_gex)} &nbsp;|&nbsp; Regime: ${data.metrics.regime}</div>
          </div>
        </div>
      </div>
    </div>
    <div class="charts-grid">
      <div class="chart-card chart-card-full">
        <div class="chart-header">
          <span class="chart-title">GEX by Strike</span>
          <div class="chart-controls">
            <span class="chart-control-btn active">All</span>
          </div>
        </div>
        <div class="chart-container" id="combined-chart" style="min-height:320px;"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">GEX Distribution</span>
        </div>
        <div class="chart-container" id="gex-chart" style="min-height:280px;"></div>
      </div>
      <div class="chart-card">
        <div class="chart-header">
          <span class="chart-title">Open Interest Distribution</span>
        </div>
        <div class="chart-container" id="oi-chart" style="min-height:280px;"></div>
      </div>
    </div>
  `;

  setTimeout(() => {
    renderCombinedChart('combined-chart', data);
    renderGEXChart('gex-chart', data);
    renderOIChart('oi-chart', data);
  }, 30);
}

// ============================================================
// METRICS PANEL
// ============================================================
function renderMetricsPanel(panel, data) {
  const m = data.metrics;
  const mac = data.macro;
  const cta = data.cta;

  const regimeCls = m.regime === 'PINNED' ? 'pinned' : m.regime === 'TRENDING' ? 'trending' : 'neutral';
  const regimeIcon = m.regime === 'PINNED' ? '⚓' : m.regime === 'TRENDING' ? '🚀' : '〰️';
  const regimeDetail = m.regime === 'PINNED'
    ? 'Positive GEX — Dealer long gamma. Sell rallies, buy dips. Range environment.'
    : m.regime === 'TRENDING'
    ? 'Negative GEX — Dealer short gamma. Moves amplified. Momentum environment.'
    : 'Neutral GEX — Mixed positioning. No strong directional bias.';

  const netGexColor = m.net_gex >= 0 ? 'val-green' : 'val-red';
  const pcrColor = m.put_call_ratio > 1.1 ? 'val-red' : m.put_call_ratio < 0.9 ? 'val-green' : 'val-gold';
  const skewColor = m.iv_skew_ratio > 1.10 ? 'val-red' : 'val-gold';

  const ctaBiasCls = { 'LONG':'cta-long','MILD_LONG':'cta-mild-long','SHORT':'cta-short','NEUTRAL':'cta-neutral' }[cta.bias] || 'cta-neutral';

  panel.innerHTML = `
    <div class="content-header">
      <div>
        <div class="spot-strip">
          <div class="spot-instrument">${data.instrument}</div>
          <div class="spot-price">${fmtNum(data.spot)}</div>
        </div>
        <div class="content-subtitle">As of ${fmtTime(data.scan_time)}</div>
      </div>
    </div>

    <div class="regime-banner ${regimeCls}">
      <div class="regime-icon">${regimeIcon}</div>
      <div>
        <div class="regime-label">${m.regime} REGIME</div>
        <div class="regime-detail">${regimeDetail}</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">GEX Summary</span>
        <span class="card-badge ${regimeCls === 'pinned' ? 'badge-pinned' : regimeCls === 'trending' ? 'badge-trending' : 'badge-neutral'}">${m.regime}</span>
      </div>
      <div class="metrics-grid">
        ${metricItem('Net GEX', fmtGex(m.net_gex), m.regime, netGexColor)}
        ${metricItem('Call GEX', '+$' + m.call_gex.toFixed(2) + 'B', 'dealer long above spot', 'val-green')}
        ${metricItem('Put GEX', '-$' + m.put_gex.toFixed(2) + 'B', 'dealer short below spot', 'val-red')}
        ${metricItem('Call Wall', fmtNum(m.call_wall), 'primary resistance', 'val-red')}
        ${metricItem('Max GEX Pin', fmtNum(m.max_gex_strike), 'gravitational pin / T1', 'val-gold')}
        ${metricItem('Zero GEX', fmtNum(m.zero_gex_strike), 'volatility trigger', 'val-orange')}
        ${metricItem('Max Pain', fmtNum(m.max_pain), 'expiry magnet', 'val-purple')}
        ${metricItem('Put Wall', fmtNum(m.put_wall), 'primary support', 'val-green')}
        ${metricItem('P/C Ratio', m.put_call_ratio.toFixed(2), m.sentiment, pcrColor)}
        ${metricItem('IV Skew', m.iv_skew_ratio.toFixed(2), m.iv_skew_bias, skewColor)}
      </div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">Macro Snapshot</span></div>
      <div class="macro-strip">
        ${macroItem('VIX', mac.vix.toFixed(2), mac.vix_signal)}
        ${macroItem('DXY', mac.dxy.toFixed(2), mac.dxy_signal)}
        ${macroItem('US 10Y', mac.us10y.toFixed(2) + '%', mac.us10y_signal)}
        ${macroItem('Prev High', fmtNum(mac.prev_day_high), 'session high')}
        ${macroItem('Prev Low', fmtNum(mac.prev_day_low), 'session low')}
        ${macroItem('Wkly Open', fmtNum(mac.weekly_open), 'weekly reference')}
      </div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">CTA Positioning (Approximate)</span></div>
      <div class="cta-row">
        <div class="cta-bias-label">CTA Bias</div>
        <div class="cta-bias-value ${ctaBiasCls}">${cta.bias.replace('_', ' ')}</div>
        <div class="cta-smas">
          ${ctaSma('SMA20', cta.sma20)}
          ${ctaSma('SMA50', cta.sma50)}
          ${ctaSma('SMA100', cta.sma100)}
          ${ctaSma('SMA200', cta.sma200)}
        </div>
        <div class="cta-note">${cta.note}</div>
      </div>
    </div>

    ${data.session_structure && data.session_structure.key_time_events.length ? `
    <div class="card">
      <div class="card-header"><span class="card-title">Key Time Events Today</span></div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        ${data.session_structure.key_time_events.map(e => `
          <div style="display:flex;align-items:center;gap:12px;padding:8px 12px;background:var(--bg-card-alt);border-radius:4px;border:1px solid var(--border);">
            <span style="font-size:14px;">🕐</span>
            <span style="font-size:12.5px;color:var(--text-primary);">${e}</span>
          </div>
        `).join('')}
      </div>
    </div>` : ''}
  `;
}

// ============================================================
// OI PANEL
// ============================================================
function renderOIPanel(panel, data) {
  const oi = data.top_strikes;

  const maxCallOI = Math.max(...oi.calls.map(c => c.oi));
  const maxPutOI  = Math.max(...oi.puts.map(p => p.oi));

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Open Interest — Top Strikes</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Spot: ${fmtNum(data.spot)}</div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">OI Distribution Chart</span>
      </div>
      <div class="chart-container" id="oi-chart" style="min-height:340px;"></div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">Top Strike Analysis</span></div>
      <div class="oi-grid">
        <div>
          <div class="oi-side-header oi-calls-header">↑ CALLS — Supply Above</div>
          ${oi.calls.map(c => `
            <div class="oi-bar-row">
              <div class="oi-strike">${fmtNum(c.strike)}</div>
              <div class="oi-bar-wrap">
                <div class="oi-bar oi-bar-call" style="width:${Math.round(c.oi/maxCallOI*100)}%"></div>
              </div>
              <div class="oi-value">${fmtOI(c.oi)}</div>
              <div class="oi-note">${c.note}</div>
            </div>
          `).join('')}
        </div>
        <div>
          <div class="oi-side-header oi-puts-header">↓ PUTS — Demand Below</div>
          ${oi.puts.map(p => `
            <div class="oi-bar-row">
              <div class="oi-strike">${fmtNum(p.strike)}</div>
              <div class="oi-bar-wrap">
                <div class="oi-bar oi-bar-put" style="width:${Math.round(p.oi/maxPutOI*100)}%"></div>
              </div>
              <div class="oi-value">${fmtOI(p.oi)}</div>
              <div class="oi-note">${p.note}</div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">Full OI Table</span></div>
      <table class="data-table">
        <thead>
          <tr><th>Strike</th><th>Type</th><th>OI Contracts</th><th>Note</th></tr>
        </thead>
        <tbody>
          ${oi.calls.map(c => `
            <tr class="row-resistance">
              <td>${fmtNum(c.strike)}</td>
              <td><span style="color:var(--accent-red);font-weight:700;">CALL</span></td>
              <td>${c.oi.toLocaleString()}</td>
              <td style="color:var(--text-muted);font-size:11px;">${c.note}</td>
            </tr>
          `).join('')}
          ${oi.puts.map(p => `
            <tr class="row-support">
              <td>${fmtNum(p.strike)}</td>
              <td><span style="color:var(--accent-green);font-weight:700;">PUT</span></td>
              <td>${p.oi.toLocaleString()}</td>
              <td style="color:var(--text-muted);font-size:11px;">${p.note}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;

  setTimeout(() => renderOIChart('oi-chart', data), 30);
}

// ============================================================
// SITUATION PANEL
// ============================================================
function renderSituationPanel(panel, data) {
  const sub = STATE.subSection || SITUATION_SUBSECTIONS[0].id;

  // Sub-tab nav
  const subNavHtml = `
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;">
      ${SITUATION_SUBSECTIONS.map(s => `
        <button onclick="switchSection('situation','${s.id}')"
          style="font-size:11px;font-weight:600;padding:6px 14px;border-radius:4px;cursor:pointer;border:1px solid var(--border);
            background:${sub===s.id ? 'var(--accent-blue)' : 'var(--bg-card)'};
            color:${sub===s.id ? '#fff' : 'var(--text-secondary)'};
            transition:all 0.18s ease;">
          ${s.label}
        </button>
      `).join('')}
    </div>
  `;

  let content = '';

  if (sub === 'levels-table') {
    content = renderLevelsTable(data);
  } else if (sub === 'narrative') {
    content = renderNarrative(data);
  } else if (sub === 'vol-profile') {
    content = renderVolProfileSection(data);
  } else if (sub === 'confluence') {
    content = renderConfluenceSection(data);
  }

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Situation at a Glance</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; ${data.situation.confluence_scenario}: ${data.situation.scenario_name}</div>
    </div>
    ${subNavHtml}
    ${content}
  `;

  // Render vol profile chart after DOM insert
  if (sub === 'vol-profile') {
    setTimeout(() => renderVolProfileChart('vol-profile-chart', data), 30);
  }
}

function renderLevelsTable(data) {
  const typeMap = {
    'CALL_WALL':  { cls: 'row-resistance', label: 'Resistance' },
    'PUT_WALL':   { cls: 'row-support',    label: 'Support'    },
    'MAX_GEX':    { cls: 'row-pin',        label: 'Pin'        },
    'ZERO_GEX':   { cls: 'row-trigger',    label: 'Trigger'    },
    'MAX_PAIN':   { cls: 'row-poc',        label: 'Magnet'     },
    'PDH':        { cls: '',               label: 'PDH'        },
    'PDL':        { cls: '',               label: 'PDL'        },
    'WEEKLY_OPEN':{ cls: '',               label: 'Ref'        },
    'POC':        { cls: 'row-poc',        label: 'POC'        },
    'SPOT':       { cls: 'row-spot',       label: 'Current'    },
    'GEX_RES':    { cls: 'row-resistance', label: 'GEX Res'    },
    'GEX_SUP':    { cls: 'row-support',    label: 'GEX Sup'    },
  };

  return `
    <div class="card">
      <div class="card-header"><span class="card-title">Key Levels — Structured View</span></div>
      <table class="data-table">
        <thead><tr><th>Level</th><th>Price</th><th>Type</th><th>Note</th></tr></thead>
        <tbody>
          ${data.situation.levels_table.map(row => {
            const meta = typeMap[row.type] || { cls: '', label: row.type };
            const tagHtml = row.tag ? tagChip(row.tag) : '';
            return `
              <tr class="${meta.cls}">
                <td>${row.label}${tagHtml}</td>
                <td>${fmtNum(row.level)}</td>
                <td><span style="font-size:10px;color:var(--text-muted);">${meta.label}</span></td>
                <td style="color:var(--text-muted);font-size:11px;">${row.tag || ''}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

function renderNarrative(data) {
  return `
    <div class="narrative-card">
      <div class="narrative-text">${data.situation.narrative}</div>
    </div>
  `;
}

function renderVolProfileSection(data) {
  const vp = data.volume_profile;
  return `
    <div class="card">
      <div class="card-header"><span class="card-title">Volume Profile</span>
        <span style="font-size:11px;color:var(--text-muted);">168-bar lookback · H1 candles</span>
      </div>
      <div class="chart-container vol-profile-container" id="vol-profile-chart"></div>
      <div class="vp-legend">
        <div class="vp-legend-item"><div class="vp-dot vp-dot-poc"></div>POC ${fmtNum(vp.poc)}</div>
        ${vp.hvn_levels ? vp.hvn_levels.slice(0,3).map(h =>
          `<div class="vp-legend-item"><div class="vp-dot vp-dot-hvn"></div>HVN ${fmtNum(h)}</div>`
        ).join('') : ''}
        ${vp.lvn_levels ? vp.lvn_levels.slice(0,2).map(l =>
          `<div class="vp-legend-item"><div class="vp-dot vp-dot-lvn"></div>LVN ${fmtNum(l)}</div>`
        ).join('') : ''}
      </div>
    </div>
    <div class="metrics-grid" style="margin-top:4px;">
      ${metricItem('POC', fmtNum(vp.poc), 'highest volume price', 'val-gold')}
      ${vp.hvn_levels ? metricItem('HVN Count', vp.hvn_levels.length, 'high volume nodes', 'val-green') : ''}
      ${vp.lvn_levels ? metricItem('LVN Count', vp.lvn_levels.length, 'low volume nodes (thin)', 'val-red') : ''}
      ${metricItem('Lookback', vp.lookback_bars + ' bars', 'H1 candles ~7 days', '')}
    </div>
  `;
}

function renderConfluenceSection(data) {
  const active = data.situation.confluence_scenario;
  const scenarios = [
    { id: 'A', name: 'Mean Reversion', desc: 'Positive GEX + price near pin = dealer dampening. Fade extremes, target pin.' },
    { id: 'B', name: 'Directional Acceleration', desc: 'Negative GEX + CTA aligned = momentum amplified. Trade the trend.' },
    { id: 'C', name: 'Fast Through LVN', desc: 'Price enters LVN zone = thin volume = fast move. Momentum trade, tight SL.' },
    { id: 'D', name: 'Structural Accumulation', desc: 'Price in HVN zone = high acceptance = chop and accumulation. Wait for breakout.' },
  ];

  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">Confluence Scenario Matrix</span>
        <span class="card-badge badge-pinned">Active: ${active}</span>
      </div>
      <div class="confluence-grid">
        ${scenarios.map(s => `
          <div class="confluence-item${s.id === active ? ' active-scenario' : ''}">
            <div class="conf-scenario-letter">${s.id}</div>
            <div class="conf-scenario-name">${s.name}</div>
            <div class="conf-scenario-desc">${s.desc}</div>
          </div>
        `).join('')}
      </div>
    </div>
    <div class="narrative-card" style="margin-top:0;">
      <div style="font-size:11px;font-weight:700;letter-spacing:0.6px;text-transform:uppercase;color:var(--text-muted);margin-bottom:8px;">Active Scenario</div>
      <div class="narrative-text"><strong>${active}: ${data.situation.scenario_name}</strong><br><br>${data.situation.scenario_description}</div>
    </div>
  `;
}

// ============================================================
// KEY LEVELS PANEL
// ============================================================
function renderLevelsPanel(panel, data) {
  const levels = data.key_levels;

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Key Levels</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Spot: ${fmtNum(data.spot)}</div>
    </div>
    <div class="level-blocks-container">
      ${levels.map((lv, i) => renderLevelBlock(lv, i)).join('')}
    </div>
  `;
}

function renderLevelBlock(lv, idx) {
  const dotCls = {
    resistance: 'dot-resistance',
    support:    'dot-support',
    pin:        'dot-pin',
    trigger:    'dot-trigger',
  }[lv.type] || 'dot-pin';

  const bodyId = `level-body-${idx}`;

  return `
    <div class="level-block" id="level-block-${idx}">
      <div class="level-block-header" onclick="toggleLevelBlock(${idx})">
        <div class="level-type-dot ${dotCls}"></div>
        <div class="level-block-label">${lv.label}</div>
        <div class="level-block-price">${fmtNum(lv.level)}</div>
        <span style="font-size:18px;color:var(--text-muted);margin-left:8px;" id="level-chevron-${idx}">▾</span>
      </div>
      <div class="level-block-body" id="${bodyId}">
        <div class="level-detail-grid">
          <div class="level-detail-item">
            <div class="level-detail-label">Entry</div>
            <div class="level-detail-value">${lv.entry}</div>
          </div>
          <div class="level-detail-item">
            <div class="level-detail-label">Stop</div>
            <div class="level-detail-value" style="color:var(--accent-red);">${lv.stop}</div>
          </div>
          <div class="level-detail-item">
            <div class="level-detail-label">R:R</div>
            <div class="level-detail-value level-rr">${lv.rr}</div>
          </div>
          <div class="level-detail-item">
            <div class="level-detail-label">Target 1</div>
            <div class="level-detail-value" style="color:var(--accent-green);">${lv.target1}</div>
          </div>
          <div class="level-detail-item">
            <div class="level-detail-label">Target 2</div>
            <div class="level-detail-value" style="color:var(--accent-green);">${lv.target2}</div>
          </div>
        </div>
        <div class="level-context">${lv.context}</div>
      </div>
    </div>
  `;
}

function toggleLevelBlock(idx) {
  const body = document.getElementById(`level-body-${idx}`);
  const chevron = document.getElementById(`level-chevron-${idx}`);
  if (!body) return;
  const isOpen = body.style.display !== 'none';
  body.style.display = isOpen ? 'none' : '';
  if (chevron) chevron.textContent = isOpen ? '▸' : '▾';
}

// ============================================================
// SCENARIOS PANEL
// ============================================================
function renderScenariosPanel(panel, data) {
  const sc = data.trade_scenarios;

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Today's Trade Scenarios</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Active: ${data.situation.confluence_scenario} — ${data.situation.scenario_name}</div>
    </div>
    <div class="scenarios-container">
      ${renderScenarioCard(sc.primary, 'primary', 'A')}
      ${sc.alt1 ? renderScenarioCard(sc.alt1, 'alt1', 'B') : ''}
      ${sc.alt2 ? renderScenarioCard(sc.alt2, 'alt2', 'C') : ''}
    </div>
  `;
}

function renderScenarioCard(sc, type, letter) {
  const letterClsMap = { primary: 'letter-primary', alt1: 'letter-alt1', alt2: 'letter-alt2' };
  const probCls = probClass(sc.probability);
  const biasCls = biasClass(sc.bias);

  return `
    <div class="scenario-card${type === 'primary' ? ' primary-scenario' : ''}">
      <div class="scenario-header">
        <div class="scenario-letter ${letterClsMap[type]}">${letter}</div>
        <div class="scenario-meta">
          <div class="scenario-label">
            ${sc.label}
            <span class="scenario-prob ${probCls}">${sc.probability}</span>
          </div>
        </div>
        <span class="scenario-bias-badge ${biasCls}">${sc.bias}</span>
      </div>
      <div class="scenario-body">
        <div class="scenario-field">
          <label>Entry</label>
          <p>${sc.entry}</p>
        </div>
        <div class="scenario-field">
          <label>Target</label>
          <p style="color:var(--accent-green);">${sc.target}</p>
        </div>
        <div class="scenario-field">
          <label>Stop</label>
          <p style="color:var(--accent-red);">${sc.stop}</p>
        </div>
        <div class="scenario-field">
          <label>Invalidation</label>
          <p style="color:var(--accent-orange);">${sc.invalidation}</p>
        </div>
        <div class="scenario-context">
          <p>${sc.context}</p>
        </div>
      </div>
    </div>
  `;
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================
function fmtNum(n) {
  if (n === null || n === undefined) return '—';
  return Number(n).toLocaleString('en-GB', { minimumFractionDigits: n % 1 !== 0 ? 1 : 0, maximumFractionDigits: 1 });
}

function fmtGex(v) {
  if (v === null || v === undefined) return '—';
  const sign = v >= 0 ? '+' : '';
  return `${sign}$${Number(v).toFixed(2)}B`;
}

function fmtOI(n) {
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n.toString();
}

function fmtTime(ts) {
  try {
    const d = new Date(ts);
    return d.toLocaleDateString('en-GB', { weekday: 'short', day: '2-digit', month: 'short' }) +
      ' ' + d.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' }) + ' BST';
  } catch { return ts || '—'; }
}

function metricItem(label, value, note, valCls = '') {
  return `
    <div class="metric-item">
      <div class="metric-label">${label}</div>
      <div class="metric-value ${valCls}">${value}</div>
      ${note ? `<div class="metric-note">${note}</div>` : ''}
    </div>
  `;
}

function macroItem(label, value, signal) {
  return `
    <div class="macro-item">
      <div class="macro-item-label">${label}</div>
      <div class="macro-item-value">${value}</div>
      <div class="macro-item-signal">${signal}</div>
    </div>
  `;
}

function ctaSma(label, value) {
  return `<div class="cta-sma-item">${label}: <span>${fmtNum(value)}</span></div>`;
}

function tagChip(tag) {
  if (!tag) return '';
  const cls = tag.includes('HVN') ? 'tag-hvn' : tag.includes('LVN') ? 'tag-lvn' : tag.includes('POC') ? 'tag-poc' : '';
  return `<span class="level-tag ${cls}">${tag.replace(/[[\]]/g, '')}</span>`;
}

function probClass(p) {
  const map = {
    'HIGH': 'prob-high',
    'MEDIUM-HIGH': 'prob-medium-high',
    'MEDIUM': 'prob-medium',
    'LOW-MEDIUM': 'prob-low-medium',
    'LOW': 'prob-low',
  };
  return map[p] || 'prob-medium';
}

function biasClass(b) {
  const map = { 'LONG': 'bias-long', 'SHORT': 'bias-short', 'RANGE': 'bias-range', 'NEUTRAL': 'bias-neutral' };
  return map[b] || 'bias-neutral';
}

function renderEmptyState() {
  return `
    <div class="empty-state">
      <div class="empty-state-icon">📭</div>
      <div class="empty-state-text">No scan data available for ${STATE.instrument}. Run a scan to populate this dashboard.</div>
    </div>
  `;
}
