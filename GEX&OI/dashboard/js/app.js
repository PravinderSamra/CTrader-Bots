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
  { id: 'charts',    label: 'Charts',         icon: '📈' },
  { id: 'metrics',   label: 'Metrics',         icon: '⚡' },
  { id: 'oi',        label: 'Open Interest',   icon: '🎯' },
  { id: 'situation', label: 'Situation',        icon: '🧭' },
  { id: 'levels',    label: 'Key Levels',      icon: '📌' },
  { id: 'scenarios', label: 'Trade Scenarios', icon: '🎲' },
  { id: 'orb',       label: 'ORB Setup',       icon: '⏱️' },
];

const SITUATION_SUBSECTIONS = [
  { id: 'levels-table', label: 'Levels Table' },
  { id: 'narrative',    label: 'Narrative'    },
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
    tab.innerHTML = `<span>${inst}</span><span class="tab-regime-badge ${regimeCls}">${regime}</span>`;
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
    el.textContent = `Last scan: ${d.toLocaleDateString('en-GB',{day:'2-digit',month:'short'})} ${d.toLocaleTimeString('en-GB',{hour:'2-digit',minute:'2-digit'})} BST`;
  } catch { el.textContent = data.scan_time || '—'; }
}

// ============================================================
// BUILD SIDEBAR
// ============================================================
function buildSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (!sidebar) return;
  sidebar.innerHTML = '';

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
    <div id="panel-orb"       class="panel"></div>
  `;
}

// ============================================================
// SWITCH INSTRUMENT
// ============================================================
function switchInstrument(inst, rerender = true) {
  STATE.instrument = inst;
  document.querySelectorAll('.instrument-tab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-instrument') === inst);
  });
  updateScanTime();
  renderCurrentPanel();
}

// ============================================================
// SWITCH SECTION
// ============================================================
function switchSection(sectionId, subSection = null) {
  STATE.section = sectionId;
  STATE.subSection = subSection || (sectionId === 'situation' ? SITUATION_SUBSECTIONS[0].id : null);

  document.querySelectorAll('.sidebar-tab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-section') === sectionId);
  });
  document.querySelectorAll('.sidebar-subtab').forEach(t => {
    t.classList.toggle('active', t.getAttribute('data-subsection') === STATE.subSection);
    t.style.display = sectionId === 'situation' ? '' : 'none';
  });

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
  document.querySelectorAll('.panel').forEach(p => {
    if (p.id !== `panel-${STATE.section}`) p.classList.remove('active');
  });

  if (!data) { panel.innerHTML = renderEmptyState(); return; }

  switch (STATE.section) {
    case 'charts':    renderChartsPanel(panel, data);    break;
    case 'metrics':   renderMetricsPanel(panel, data);   break;
    case 'oi':        renderOIPanel(panel, data);        break;
    case 'situation': renderSituationPanel(panel, data); break;
    case 'levels':    renderLevelsPanel(panel, data);    break;
    case 'scenarios': renderScenariosPanel(panel, data); break;
    case 'orb':       renderORBPanel(panel, data);       break;
  }
}

// ============================================================
// CHARTS PANEL
// ============================================================
function staleGexBanner(data) {
  if (!data.gex_stale) return '';
  return `<div class="gex-stale-banner">⏱ GEX &amp; OI data from previous NY close (${fmtTime(data.gex_data_time)}) — live price updated. GEX levels refresh at 14:30 BST when NY opens.</div>`;
}

function renderChartsPanel(panel, data) {
  if (data.proxy_mode) { renderProxyChartsPanel(panel, data); return; }
  panel.innerHTML = `
    <div class="content-header">
      <div>
        <div class="spot-strip">
          <div class="spot-instrument">${data.instrument}</div>
          <div class="spot-price">${fmtNum(data.spot)}</div>
          <div>
            <div class="spot-meta">Net GEX: ${fmtGex(data.metrics.net_gex)} &nbsp;|&nbsp; Regime: <strong>${data.metrics.regime}</strong> &nbsp;|&nbsp; Scan: ${fmtTime(data.scan_time)}</div>
          </div>
        </div>
      </div>
    </div>
    ${staleGexBanner(data)}
    <div class="card" style="padding:12px 16px 8px;">
      <div style="font-size:12px;color:var(--text-secondary);line-height:1.6;">
        ${regimeChartCaption(data.metrics.regime, data.metrics.net_gex, data.metrics.call_wall, data.metrics.put_wall, data.metrics.max_gex_strike, data.metrics.zero_gex_strike)}
      </div>
    </div>
    <div class="charts-grid">
      <div class="chart-card chart-card-full">
        <div class="chart-header">
          <span class="chart-title">GEX by Strike — with Key Levels</span>
          <span style="font-size:11px;color:var(--text-muted);">Green bars = dealers long gamma (stabilising). Red bars = dealers short gamma (amplifying).</span>
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
          <span class="chart-title">Open Interest by Strike</span>
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

function regimeChartCaption(regime, netGex, callWall, putWall, pin, zeroGex) {
  if (regime === 'PINNED') {
    return `<strong style="color:var(--accent-green)">⚓ PINNED REGIME</strong> — Net GEX is ${fmtGex(netGex)}, meaning options dealers are net long gamma. They are mechanically forced to <em>sell rallies and buy dips</em> to hedge their options book — this dampens price swings and keeps ${STATE.instrument} in a range. The tall green bars on the chart show where this dampening force is strongest. The <span style="color:var(--accent-gold)">gold dashed line</span> is the Max GEX Pin (${fmtNum(pin)}) — the gravitational centre price is being pulled toward. The <span style="color:var(--accent-red)">red dashed line</span> is the Call Wall (${fmtNum(callWall)}) — your upside ceiling. The <span style="color:var(--accent-green)">green dashed line</span> is the Put Wall (${fmtNum(putWall)}) — your downside floor. The <span style="color:var(--accent-orange)">orange line</span> is Zero GEX (${fmtNum(zeroGex)}) — if price breaks through this level, the pinning force disappears and moves accelerate.`;
  } else if (regime === 'TRENDING') {
    return `<strong style="color:var(--accent-red)">🚀 TRENDING REGIME</strong> — Net GEX is ${fmtGex(netGex)}, meaning options dealers are net short gamma. They are forced to <em>buy as price rises and sell as price falls</em> — this amplifies moves in whichever direction price is going. The red bars dominate the chart, showing dealer short gamma exposure. This is a momentum-friendly environment: breakouts tend to run further than expected and pullbacks can be sharp. The <span style="color:var(--accent-orange)">orange line</span> is Zero GEX (${fmtNum(zeroGex)}) — the critical pivot. Above it, some dealer dampening remains. Below it, negative GEX amplification kicks in fully and moves accelerate.`;
  }
  return `Net GEX: ${fmtGex(netGex)}. Mixed dealer positioning — no strong directional bias from gamma flows today.`;
}

// ============================================================
// METRICS PANEL
// ============================================================
function renderMetricsPanel(panel, data) {
  if (data.proxy_mode) { renderProxyMetricsPanel(panel, data); return; }
  const m = data.metrics;
  const mac = data.macro;
  const cta = data.cta || {};

  const regimeCls = m.regime === 'PINNED' ? 'pinned' : m.regime === 'TRENDING' ? 'trending' : 'neutral';
  const netGexColor = m.net_gex >= 0 ? 'val-green' : 'val-red';
  const pcrColor = m.put_call_ratio > 1.1 ? 'val-red' : m.put_call_ratio < 0.9 ? 'val-green' : 'val-gold';
  const skewColor = (m.iv_skew_ratio || 1) > 1.10 ? 'val-red' : 'val-gold';
  const ctaBiasCls = { 'LONG':'cta-long','MILD_LONG':'cta-mild-long','SHORT':'cta-short','NEUTRAL':'cta-neutral' }[cta.bias] || 'cta-neutral';

  panel.innerHTML = `
    <div class="content-header">
      <div>
        <div class="spot-strip">
          <div class="spot-instrument">${data.instrument}</div>
          <div class="spot-price">${fmtNum(data.spot)}</div>
        </div>
        <div class="content-subtitle">Scan as of ${fmtTime(data.scan_time)}</div>
      </div>
    </div>
    ${staleGexBanner(data)}
    ${renderRegimeBanner(m, regimeCls)}

    <div class="card">
      <div class="card-header">
        <span class="card-title">GEX Summary — Gamma Exposure Breakdown</span>
        <span class="card-badge ${regimeCls === 'pinned' ? 'badge-pinned' : regimeCls === 'trending' ? 'badge-trending' : 'badge-neutral'}">${m.regime}</span>
      </div>

      ${richMetricRow('Net GEX', fmtGex(m.net_gex), netGexColor,
        netGexExplainer(m.net_gex, m.regime, data.instrument))}

      ${richMetricRow('Call GEX', '+$' + m.call_gex.toFixed(2) + 'B', 'val-green',
        `The total gamma exposure from <strong>call options above the current spot price</strong>. Dealers who sold these calls must buy the underlying as price rises toward those strikes — which slows upward moves. The higher this number, the more ceiling resistance there is above spot. Call GEX concentration is what creates the Call Wall.`)}

      ${richMetricRow('Put GEX', '-$' + m.put_gex.toFixed(2) + 'B', 'val-red',
        `The total gamma exposure from <strong>put options below the current spot price</strong>. Dealers who sold these puts must sell the underlying as price falls toward those strikes — in a trending (negative GEX) environment this amplifies downside moves. In a pinned environment, high put GEX creates the Put Wall floor.`)}

      <div class="metric-divider"></div>

      ${richMetricRow('Call Wall — ' + fmtNum(m.call_wall), 'Primary Resistance', 'val-red',
        `The strike price where call option open interest is highest. This is your <strong>primary ceiling for the session</strong>. Options dealers who sold these calls have to sell ${data.instrument} futures as price rises toward this level to hedge their exposure — creating significant supply overhead. A clean break and hold ABOVE the Call Wall flips the dynamic and can trigger a sharp move higher as dealers are forced to cover. Until that happens, treat it as a hard cap.`)}

      ${richMetricRow('Max GEX Pin — ' + fmtNum(m.max_gex_strike), 'Gravitational Anchor', 'val-gold',
        `The strike where total dealer gamma exposure is at its absolute maximum. This is the <strong>most powerful gravitational level on the board</strong> — price is constantly being pulled back toward it throughout the session. In a pinned regime, this is your primary Target 1 on any trade. Think of it as a magnet: the further price moves away from the pin, the stronger the force pulling it back. It is also typically the best risk:reward entry zone for mean-reversion trades.`)}

      ${richMetricRow('Zero GEX — ' + fmtNum(m.zero_gex_strike), 'Volatility Trigger', 'val-orange',
        `The price level where dealer net gamma exposure flips from positive to negative (or vice versa). This is the <strong>most important level on the chart</strong> from a volatility perspective. Above Zero GEX: dealer dampening is active and moves are muted. Below Zero GEX: dealer dampening disappears, negative gamma amplification begins and moves accelerate rapidly. A confirmed break through Zero GEX on strong volume is a high-conviction signal — it is the trigger for a directional, fast-move trade setup.`)}

      ${richMetricRow('Max Pain — ' + fmtNum(m.max_pain), 'Expiry Magnet', 'val-purple',
        `The price at which the maximum number of options contracts (both calls and puts) expire worthless — minimising the payout to options buyers. Market makers and large dealers have a structural incentive to keep price near Max Pain heading into expiry, as it reduces their hedging obligations. Max Pain acts as a <strong>slow-moving gravitational pull</strong> — more relevant in the final 1–2 days before options expiry than early in the week, but always worth noting as an expiry target.`)}

      ${richMetricRow('Put Wall — ' + fmtNum(m.put_wall), 'Primary Support', 'val-green',
        `The strike price where put option open interest is highest. This is your <strong>primary floor for the session</strong>. Dealers who sold these puts must buy ${data.instrument} futures as price falls toward this level — creating significant demand and support. The Put Wall is the level where aggressive short sellers face the strongest natural opposition. A clean break and hold BELOW the Put Wall is a significant bearish signal and often leads to rapid further downside as the support flips to resistance.`)}
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">Options Market Sentiment</span>
      </div>
      ${richMetricRow('Put/Call Ratio — ' + m.put_call_ratio.toFixed(2), m.sentiment, pcrColor,
        pcrExplainer(m.put_call_ratio, m.sentiment, data.instrument))}

      ${m.iv_skew_ratio ? richMetricRow('IV Skew — ' + (m.iv_skew_ratio).toFixed(2), m.iv_skew_bias || '', skewColor,
        skewExplainer(m.iv_skew_ratio, m.iv_skew_bias, data.instrument)) : ''}
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">Macro Snapshot — Market Context</span></div>
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.65;margin-bottom:16px;">
        ${macroNarrative(mac, data.instrument)}
      </div>
      <div class="macro-strip">
        ${macroItem('VIX', (mac.vix||0).toFixed(2), mac.vix_signal || vixLabel(mac.vix))}
        ${macroItem('DXY', (mac.dxy||0).toFixed(2), mac.dxy_signal || 'US Dollar Index')}
        ${macroItem('US 10Y', (mac.us10y||0).toFixed(2) + '%', mac.us10y_signal || 'US Treasury yield')}
        ${macroItem('Prev High', fmtNum(mac.prev_day_high), 'Yesterday\'s session high')}
        ${macroItem('Prev Low', fmtNum(mac.prev_day_low), 'Yesterday\'s session low')}
        ${macroItem('Wkly Open', fmtNum(mac.weekly_open), 'Monday\'s opening price')}
      </div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">CTA Positioning — Systematic Trend Follower Bias</span></div>
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.65;margin-bottom:14px;">
        ${ctaExplainer(cta, data.instrument)}
      </div>
      <div class="cta-row">
        <div class="cta-bias-label">CTA Bias</div>
        <div class="cta-bias-value ${ctaBiasCls}">${(cta.bias||'N/A').replace('_',' ')}</div>
        <div class="cta-smas">
          ${cta.sma20  ? ctaSma('20-day MA',  cta.sma20)  : ''}
          ${cta.sma50  ? ctaSma('50-day MA',  cta.sma50)  : ''}
          ${cta.sma100 ? ctaSma('100-day MA', cta.sma100) : ''}
          ${cta.sma200 ? ctaSma('200-day MA', cta.sma200) : ''}
        </div>
      </div>
      ${cta.note ? `<div style="font-size:11.5px;color:var(--text-muted);margin-top:10px;font-style:italic;">${cta.note}</div>` : ''}
    </div>

    ${data.session_structure && data.session_structure.key_time_events && data.session_structure.key_time_events.length ? `
    <div class="card">
      <div class="card-header"><span class="card-title">Key Time Events Today</span></div>
      <div style="font-size:12px;color:var(--text-secondary);margin-bottom:12px;">Scheduled data releases and events that can trigger sharp moves. Size down or stand aside in the 5 minutes before and after each event until direction is confirmed.</div>
      <div style="display:flex;flex-direction:column;gap:8px;">
        ${data.session_structure.key_time_events.map(e => `
          <div style="display:flex;align-items:center;gap:12px;padding:10px 14px;background:var(--bg-card-alt);border-radius:6px;border:1px solid var(--border);">
            <span style="font-size:16px;">🕐</span>
            <span style="font-size:13px;color:var(--text-primary);font-weight:500;">${e}</span>
          </div>
        `).join('')}
      </div>
    </div>` : ''}
  `;
}

// ---- Regime Banner ----
function renderRegimeBanner(m, regimeCls) {
  const icon = m.regime === 'PINNED' ? '⚓' : m.regime === 'TRENDING' ? '🚀' : '〰️';
  const detail = regimeFullExplainer(m.regime, m.net_gex);
  return `
    <div class="regime-banner ${regimeCls}">
      <div class="regime-icon">${icon}</div>
      <div style="flex:1;">
        <div class="regime-label">${m.regime} REGIME</div>
        <div class="regime-detail" style="margin-top:4px;line-height:1.6;">${detail}</div>
      </div>
    </div>
  `;
}

// ---- Rich Metric Row ----
function richMetricRow(label, value, valCls, explanation) {
  return `
    <div class="rich-metric-row">
      <div class="rich-metric-header">
        <div class="rich-metric-label">${label}</div>
        <div class="rich-metric-value ${valCls}">${value}</div>
      </div>
      <div class="rich-metric-explanation">${explanation}</div>
    </div>
  `;
}

// ---- Explainer Functions ----
function regimeFullExplainer(regime, netGex) {
  if (regime === 'PINNED') {
    return `Net GEX is <strong>${fmtGex(netGex)}</strong> — positive, meaning options dealers are net long gamma. In simple terms: dealers have sold large amounts of options on both sides of the market. To stay hedged, they are mechanically forced to <strong>sell when price rallies and buy when price dips</strong>. This acts like a shock absorber — dampening swings and pulling price back toward the centre. The result is a <strong>range-bound, mean-reverting session</strong>. The best strategy is to fade moves to the extremes (Call Wall / Put Wall) and target the Max GEX Pin in the middle. Avoid chasing breakouts — dealer flows actively work against them.`;
  } else if (regime === 'TRENDING') {
    return `Net GEX is <strong>${fmtGex(netGex)}</strong> — negative, meaning options dealers are net short gamma. Dealers must <strong>buy as price rises and sell as price falls</strong> to stay hedged — the opposite of the pinned regime. Instead of dampening moves, dealer flows <strong>amplify and accelerate them</strong>. This is a momentum-friendly environment. Breakouts have more follow-through. Pullbacks can be sharper. The best strategy is to trade with the direction of the move once confirmed, use wider stops, and expect faster price action than normal.`;
  }
  return `Net GEX is near zero — dealers have balanced gamma exposure. No strong directional force from options flows today. Price can move freely in either direction. Focus on price action and key structural levels.`;
}

function netGexExplainer(netGex, regime, instrument) {
  const sign = netGex >= 0 ? 'positive' : 'negative';
  const abs = Math.abs(netGex).toFixed(2);
  return `Net GEX of <strong>${fmtGex(netGex)}</strong> represents the total dollar gamma exposure across all options on ${instrument}. A ${sign} reading means dealers are net ${netGex >= 0 ? 'long' : 'short'} gamma — they ${netGex >= 0 ? 'buy dips and sell rallies' : 'buy as price rises and sell as it falls'} to stay hedged. The magnitude ($${abs}B) tells you the strength of this force: the higher the absolute value, the stronger the pinning or amplifying effect on price movement today.`;
}

function pcrExplainer(pcr, sentiment, instrument) {
  if (pcr > 1.2) return `Put/Call ratio of <strong>${pcr.toFixed(2)}</strong> means there are significantly more put options open than calls. This indicates <strong>bearish positioning or heavy hedging activity</strong> in the ${instrument} options market. Participants are paying up for downside protection, suggesting expectations of either a correction or elevated uncertainty. This is a contrarian indicator when extreme — very high PCR can signal oversold conditions and a potential bounce as the hedging unwinds.`;
  if (pcr > 1.05) return `Put/Call ratio of <strong>${pcr.toFixed(2)}</strong> shows a mild tilt toward puts — slightly more participants are buying downside protection than upside calls. This reflects a cautious, mildly bearish bias in the options market but is not extreme. Watch for whether this builds further (more bearish) or fades (sentiment improving).`;
  if (pcr < 0.8) return `Put/Call ratio of <strong>${pcr.toFixed(2)}</strong> is notably low, meaning calls significantly outnumber puts. This indicates <strong>bullish positioning and speculative call-buying</strong>. Participants are positioned for upside. Extremely low PCR can be a contrarian warning — when everyone is positioned long via calls, there may be fewer buyers left to push price higher, and any disappointment can trigger a sharp unwinding.`;
  return `Put/Call ratio of <strong>${pcr.toFixed(2)}</strong> is near neutral — broadly balanced positioning between puts and calls. No extreme directional bias from the options market at this time. Sentiment: ${sentiment}.`;
}

function skewExplainer(skew, bias, instrument) {
  if (skew > 1.15) return `IV Skew of <strong>${skew.toFixed(2)}</strong> means put options are significantly more expensive than equivalent call options (${Math.round((skew-1)*100)}% premium). This tells you <strong>institutional money is paying up for downside insurance</strong> on ${instrument}. It doesn't necessarily mean a crash is coming — but it shows that large players are hedging their long exposure and are worried about downside risk. Elevated skew adds weight to bearish scenarios and suggests the market is not fully confident in the upside.`;
  if (skew > 1.08) return `IV Skew of <strong>${skew.toFixed(2)}</strong> shows a mild bias toward put premium — puts cost slightly more than calls. This is a <strong>mild bearish hedge signal</strong>: the options market has a slight lean toward downside protection but nothing extreme. Standard defensive positioning. Note this as a slight headwind for aggressive long setups.`;
  return `IV Skew of <strong>${skew.toFixed(2)}</strong> — options market is showing broadly balanced implied volatility between puts and calls. No significant skew bias. Consistent with a neutral to mildly bullish options sentiment on ${instrument}.`;
}

function macroNarrative(mac, instrument) {
  const vix = mac.vix || 0;
  const dxy = mac.dxy || 0;
  const y10 = mac.us10y || 0;

  let parts = [];

  if (vix < 15) parts.push(`<strong>VIX at ${vix.toFixed(1)}</strong> is in low volatility territory — the market's "fear gauge" is calm. This favours range-trading, premium-selling strategies, and mean-reversion setups. Options are cheap, which means implied moves are small. Don't expect explosive directional moves unless there's a major catalyst.`);
  else if (vix < 20) parts.push(`<strong>VIX at ${vix.toFixed(1)}</strong> is in a normal range — moderate implied volatility. Normal intraday ranges. Standard position sizing applies.`);
  else if (vix < 30) parts.push(`<strong>VIX at ${vix.toFixed(1)}</strong> is elevated — the market is pricing in above-average uncertainty. Intraday ranges will be wider than normal. Consider reducing position size by 20–30% and widening stops to account for the noisier price action.`);
  else parts.push(`<strong>VIX at ${vix.toFixed(1)}</strong> is HIGH — fear is elevated and markets are volatile. Specialist setups only. Significantly reduced position sizes. Wide stops. Favour defined-risk trades.`);

  if (dxy > 0) {
    if (instrument === 'XAUUSD') {
      parts.push(`<strong>DXY at ${dxy.toFixed(2)}</strong>: Gold trades inversely to the US Dollar. A strong DXY is a headwind for Gold prices — dollar strength makes Gold more expensive for foreign buyers. Watch DXY direction as a leading indicator for XAUUSD throughout the session.`);
    } else if (instrument === 'US500') {
      parts.push(`<strong>DXY at ${dxy.toFixed(2)}</strong>: A strong dollar can be a mild headwind for US equities as it impacts multinational earnings. More relevant for longer-term positioning — for intraday GEX setups, treat DXY as background context.`);
    } else {
      parts.push(`<strong>DXY at ${dxy.toFixed(2)}</strong>: US Dollar index for broader macro context.`);
    }
  }

  if (y10 > 0) {
    if (y10 > 4.5) parts.push(`<strong>US 10-Year Yield at ${y10.toFixed(2)}%</strong> is elevated. High real yields compete with equities for capital and create a structural headwind for risk assets and Gold. Watch for any yield spikes intraday — sudden moves higher in the 10Y are typically negative for equities and Gold.`);
    else parts.push(`<strong>US 10-Year Yield at ${y10.toFixed(2)}%</strong> — moderate yield environment. Monitoring for any significant moves that could shift risk appetite.`);
  }

  return parts.join('<br><br>');
}

function ctaExplainer(cta, instrument) {
  if (!cta || !cta.bias) return `CTA positioning data unavailable for this scan.`;
  const bias = cta.bias;
  const biasLabel = bias.replace('_', ' ');
  let text = `<strong>CTAs (Commodity Trading Advisors)</strong> are large systematic/quantitative hedge funds that follow price trends — they go long when prices are above their key moving averages and short when below. They collectively manage hundreds of billions in capital, meaning their positioning creates real order flow that can amplify or counteract your trades.<br><br>`;

  if (bias === 'LONG') {
    text += `Current CTA bias is <strong style="color:var(--accent-green)">LONG</strong> — ${instrument} is trading above all major moving averages (20, 50, 100, 200-day) with the shorter averages above the longer ones (uptrend structure). Systematic funds are positioned long and are a <strong>tailwind for long trades</strong>. If the Call Wall breaks today, CTA momentum-buying could add significant fuel to the move. Rejection shorts at resistance are working against the CTA flow — keep stops tighter on short positions.`;
  } else if (bias === 'MILD_LONG') {
    text += `Current CTA bias is <strong style="color:#6ee7b7">MILD LONG</strong> — ${instrument} is above the 50-day MA but the moving average structure is not fully aligned. CTAs are leaning long but without maximum conviction. There is some systematic support for longs, but not the full-force tailwind of a clean uptrend. Both long and short setups are playable — just note that the mild CTA tailwind slightly favours buyers.`;
  } else if (bias === 'SHORT') {
    text += `Current CTA bias is <strong style="color:var(--accent-red)">SHORT</strong> — ${instrument} is below its 50-day MA with moving averages in a downtrend structure. Systematic funds are positioned short and are a <strong>headwind for long trades</strong>. Short setups have CTA selling flows behind them, giving them more conviction. Long trades at support need to be treated as counter-trend — use tighter targets and stops.`;
  } else {
    text += `Current CTA bias is <strong>NEUTRAL</strong> — ${instrument} is near a moving average crossover zone and systematic funds have not committed to a clear direction. No significant CTA tailwind or headwind today. Trade purely off GEX levels and price action signals.`;
  }
  return text;
}

function vixLabel(vix) {
  if (!vix) return 'N/A';
  if (vix < 15) return 'Low vol — range-trading conditions';
  if (vix < 20) return 'Normal vol environment';
  if (vix < 30) return 'Elevated — reduce position size';
  return 'High vol — specialist setups only';
}

// ============================================================
// OI PANEL
// ============================================================
function renderOIPanel(panel, data) {
  if (data.proxy_mode) { renderProxyOIPanel(panel, data); return; }
  const oi = data.top_strikes;
  const m = data.metrics;
  if (!oi || !oi.calls || !oi.puts || oi.calls.length === 0 || oi.puts.length === 0) {
    panel.innerHTML = renderEmptyState(); return;
  }
  const maxCallOI = Math.max(...oi.calls.map(c => c.oi));
  const maxPutOI  = Math.max(...oi.puts.map(p => p.oi));

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Open Interest — Top Strikes</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Spot: ${fmtNum(data.spot)}</div>
    </div>

    <div class="card" style="padding:16px 20px;">
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.7;">
        <strong>What is Open Interest?</strong> Open Interest (OI) is the total number of live options contracts that have not yet been closed or expired. High OI at a specific strike price means a large number of participants hold options at that level — which forces options dealers to maintain significant hedges near those prices.<br><br>
        <strong>Call OI (Red bars — above spot):</strong> Strikes with high call open interest act as <strong>resistance zones</strong>. Dealers who sold these calls must sell ${data.instrument} futures as price approaches these levels to stay hedged — creating supply overhead. The strike with the <em>highest</em> call OI is your Call Wall: <strong>${fmtNum(m.call_wall)}</strong>.<br><br>
        <strong>Put OI (Green bars — below spot):</strong> Strikes with high put open interest act as <strong>support zones</strong>. Dealers who sold these puts must buy ${data.instrument} futures as price falls toward these levels — creating demand. The strike with the <em>highest</em> put OI is your Put Wall: <strong>${fmtNum(m.put_wall)}</strong>.<br><br>
        <strong>Max Pain (${fmtNum(m.max_pain)}):</strong> The price where the most options contracts expire worthless — minimising payouts to option buyers. Dealers are incentivised to keep price near this level, especially approaching expiry.
      </div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">Interactive OI Chart — Calls vs Puts by Strike</span></div>
      <div class="chart-container" id="oi-chart" style="min-height:360px;"></div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">Top Strikes — Supply & Demand Map</span></div>
      <div class="oi-grid">
        <div>
          <div class="oi-side-header oi-calls-header">↑ CALLS — Supply / Resistance Above Spot</div>
          ${oi.calls.map((c,i) => `
            <div class="oi-bar-row">
              <div class="oi-strike">${fmtNum(c.strike)}</div>
              <div class="oi-bar-wrap">
                <div class="oi-bar oi-bar-call" style="width:${Math.round(c.oi/maxCallOI*100)}%"></div>
              </div>
              <div class="oi-value">${c.oi.toLocaleString()}</div>
              <div class="oi-note">${i === 0 ? '← Call Wall (max resistance)' : c.note}</div>
            </div>
          `).join('')}
          <div style="font-size:11px;color:var(--text-muted);padding:10px 12px 4px;line-height:1.5;">
            These are the strikes with the most call contracts open. Dealers are forced to sell ${data.instrument} as price approaches each level. The longer the bar, the stronger the resistance.
          </div>
        </div>
        <div>
          <div class="oi-side-header oi-puts-header">↓ PUTS — Demand / Support Below Spot</div>
          ${oi.puts.map((p,i) => `
            <div class="oi-bar-row">
              <div class="oi-strike">${fmtNum(p.strike)}</div>
              <div class="oi-bar-wrap">
                <div class="oi-bar oi-bar-put" style="width:${Math.round(p.oi/maxPutOI*100)}%"></div>
              </div>
              <div class="oi-value">${p.oi.toLocaleString()}</div>
              <div class="oi-note">${i === 0 ? '← Put Wall (max support)' : p.note}</div>
            </div>
          `).join('')}
          <div style="font-size:11px;color:var(--text-muted);padding:10px 12px 4px;line-height:1.5;">
            These are the strikes with the most put contracts open. Dealers are forced to buy ${data.instrument} as price falls toward each level. The longer the bar, the stronger the support floor.
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><span class="card-title">Full OI Strike Table</span></div>
      <table class="data-table">
        <thead><tr><th>Strike</th><th>Type</th><th>OI Contracts</th><th>Role</th></tr></thead>
        <tbody>
          ${oi.calls.map((c,i) => `
            <tr class="row-resistance">
              <td>${fmtNum(c.strike)}</td>
              <td><span style="color:var(--accent-red);font-weight:700;">CALL</span></td>
              <td>${c.oi.toLocaleString()}</td>
              <td style="color:var(--text-muted);font-size:11px;">${i===0 ? 'Call Wall — primary ceiling / max resistance' : 'Call resistance — supply overhead'}</td>
            </tr>
          `).join('')}
          ${oi.puts.map((p,i) => `
            <tr class="row-support">
              <td>${fmtNum(p.strike)}</td>
              <td><span style="color:var(--accent-green);font-weight:700;">PUT</span></td>
              <td>${p.oi.toLocaleString()}</td>
              <td style="color:var(--text-muted);font-size:11px;">${i===0 ? 'Put Wall — primary floor / max support' : 'Put support — demand below'}</td>
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

  const subNavHtml = `
    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:16px;">
      ${SITUATION_SUBSECTIONS.map(s => `
        <button onclick="switchSection('situation','${s.id}')"
          style="font-size:11px;font-weight:600;padding:6px 14px;border-radius:4px;cursor:pointer;
            border:1px solid var(--border);
            background:${sub===s.id ? 'var(--accent-blue)' : 'var(--bg-card)'};
            color:${sub===s.id ? '#fff' : 'var(--text-secondary)'};
            transition:all 0.18s ease;">
          ${s.label}
        </button>
      `).join('')}
    </div>
  `;

  let content = '';
  if (sub === 'levels-table') content = renderLevelsTable(data);
  else if (sub === 'narrative')    content = renderNarrative(data);
  else if (sub === 'vol-profile')  content = renderVolProfileSection(data);
  else if (sub === 'confluence')   content = renderConfluenceSection(data);

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Situation at a Glance</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Active Scenario: ${data.situation.confluence_scenario} — ${data.situation.scenario_name}</div>
    </div>
    ${subNavHtml}
    ${content}
  `;

  if (sub === 'vol-profile') {
    setTimeout(() => renderVolProfileChart('vol-profile-chart', data), 30);
  }
}

function renderLevelsTable(data) {
  const typeMap = {
    'CALL_WALL':   { cls: 'row-resistance', label: 'Call Wall',    desc: 'Primary resistance ceiling — highest call OI' },
    'PUT_WALL':    { cls: 'row-support',    label: 'Put Wall',     desc: 'Primary support floor — highest put OI' },
    'MAX_GEX':     { cls: 'row-pin',        label: 'Max GEX Pin',  desc: 'Gravitational anchor — strongest dealer gamma' },
    'ZERO_GEX':    { cls: 'row-trigger',    label: 'Zero GEX',     desc: 'Volatility trigger — gamma flips here' },
    'MAX_PAIN':    { cls: 'row-poc',        label: 'Max Pain',     desc: 'Expiry magnet — max options decay strike' },
    'PDH':         { cls: '',               label: 'Prev Day High', desc: 'Yesterday\'s high — key reference level' },
    'PDL':         { cls: '',               label: 'Prev Day Low',  desc: 'Yesterday\'s low — key reference level' },
    'WEEKLY_OPEN': { cls: '',               label: 'Weekly Open',   desc: 'This week\'s opening price — trend reference' },
    'POC':         { cls: 'row-poc',        label: 'Volume POC',   desc: 'Highest volume price — strong acceptance zone' },
    'SPOT':        { cls: 'row-spot',       label: 'Current Spot', desc: 'Live market price' },
    'GEX_RES':     { cls: 'row-resistance', label: 'GEX Resistance', desc: 'Secondary resistance from gamma levels' },
    'GEX_SUP':     { cls: 'row-support',    label: 'GEX Support',   desc: 'Secondary support from gamma levels' },
  };

  return `
    <div class="card">
      <div class="card-header"><span class="card-title">Structured Levels Map — Resistance to Support</span></div>
      <div style="font-size:12px;color:var(--text-secondary);margin-bottom:14px;line-height:1.6;">
        All key levels for today's session, ordered from highest to lowest price. <span style="color:var(--accent-red)">Red</span> = resistance above (supply). <span style="color:var(--accent-gold)">Gold</span> = pin / magnet. <span style="color:var(--accent-blue)">Blue</span> = current spot. <span style="color:var(--accent-green)">Green</span> = support below (demand). <span style="color:var(--accent-orange)">Orange</span> = volatility trigger.
      </div>
      <table class="data-table">
        <thead><tr><th>Level Name</th><th>Price</th><th>Role</th><th>Tag</th></tr></thead>
        <tbody>
          ${data.situation.levels_table.map(row => {
            const meta = typeMap[row.type] || { cls: '', label: row.type, desc: '' };
            const tagHtml = row.tag ? tagChip(row.tag) : '';
            return `
              <tr class="${meta.cls}">
                <td>${meta.label}${tagHtml}</td>
                <td style="font-family:'JetBrains Mono',monospace;font-weight:700;">${fmtNum(row.level)}</td>
                <td style="font-size:11px;color:var(--text-muted);">${meta.desc}</td>
                <td>${row.tag ? tagChip(row.tag) : ''}</td>
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
    <div class="card" style="padding:20px 24px;">
      <div class="card-header" style="margin-bottom:16px;"><span class="card-title">Market Narrative — Full Analysis</span></div>
      <div style="font-size:13.5px;color:var(--text-secondary);line-height:1.8;">
        ${data.situation.narrative}
      </div>
    </div>
  `;
}

function renderVolProfileSection(data) {
  const vp = data.volume_profile;
  if (!vp || !vp.poc) {
    return `<div class="card"><div style="padding:20px;color:var(--text-muted);">Volume Profile data will be available after running a live scan. The agent fetches H1 candles from CTrader and distributes tick volume into price buckets to identify where the most trading activity has occurred.</div></div>`;
  }
  return `
    <div class="card" style="padding:16px 20px;">
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.7;">
        <strong>What is the Volume Profile?</strong> The Volume Profile shows how much trading volume occurred at each price level over the past ${vp.lookback_bars || 168} hourly candles (approximately the past week). It answers the question: <em>"Where has this market spent the most time and activity?"</em><br><br>
        <strong>POC (Point of Control) — ${fmtNum(vp.poc)}:</strong> The single price bucket with the <em>highest volume</em>. This is the most accepted price in recent history — price tends to return to the POC when untethered and it acts as a strong magnet for mean-reversion trades.<br><br>
        <strong>HVN (High Volume Nodes) — ${vp.hvn_levels ? vp.hvn_levels.map(h => fmtNum(h)).join(', ') : 'N/A'}:</strong> Price ranges with above-average volume. Markets tend to <em>slow down and consolidate</em> when entering HVN zones — there are many buyers and sellers who transacted here and will defend their positions. Expect choppy, difficult price action in HVN zones.<br><br>
        <strong>LVN (Low Volume Nodes) — ${vp.lvn_levels ? vp.lvn_levels.map(l => fmtNum(l)).join(', ') : 'N/A'}:</strong> Price ranges with very little historical volume — thin areas. Markets tend to <em>move quickly through LVN zones</em> because there is little opposing order flow. If price enters an LVN, expect a fast, sharp move to the next HVN or key level. LVNs create the "fast-through" momentum setups.
      </div>
    </div>
    <div class="card">
      <div class="card-header">
        <span class="card-title">Volume Profile Chart</span>
        <span style="font-size:11px;color:var(--text-muted);">${vp.lookback_bars || 168} H1 bars · bucket size ${vp.bucket_size || 5} points</span>
      </div>
      <div class="chart-container vol-profile-container" id="vol-profile-chart"></div>
      <div class="vp-legend">
        <div class="vp-legend-item"><div class="vp-dot vp-dot-poc"></div>POC ${fmtNum(vp.poc)} — highest volume</div>
        ${(vp.hvn_levels||[]).slice(0,3).map(h => `<div class="vp-legend-item"><div class="vp-dot vp-dot-hvn"></div>HVN ${fmtNum(h)}</div>`).join('')}
        ${(vp.lvn_levels||[]).slice(0,2).map(l => `<div class="vp-legend-item"><div class="vp-dot vp-dot-lvn"></div>LVN ${fmtNum(l)} (thin)</div>`).join('')}
      </div>
    </div>
    <div class="metrics-grid" style="margin-top:0;">
      ${metricItem('POC', fmtNum(vp.poc), 'Most accepted price — mean reversion target', 'val-gold')}
      ${vp.hvn_levels ? metricItem('HVN Zones', vp.hvn_levels.length, 'High vol zones — expect slow/choppy price action', 'val-green') : ''}
      ${vp.lvn_levels ? metricItem('LVN Zones', vp.lvn_levels.length, 'Thin zones — expect fast moves through here', 'val-red') : ''}
      ${metricItem('Lookback', (vp.lookback_bars||168) + ' H1 bars', 'Approx. 7 trading days of data', '')}
    </div>
  `;
}

function renderConfluenceSection(data) {
  const active = data.situation.confluence_scenario;
  const allScenarios = [
    {
      id: 'A',
      name: 'Mean Reversion',
      shortDesc: 'Positive GEX + price near pin = dealer dampening active. Fade the extremes, target the pin.',
      fullDesc: 'This is the highest-probability setup in a pinned GEX environment. Price is gravitationally attracted to the Max GEX Pin. Dealer flows actively oppose directional moves. The strategy is to wait for price to reach an extreme — the Call Wall above or the Put Wall below — and fade it back toward the pin. Use tight stops just beyond the wall, target the pin as T1. Best executed as a scalp with defined risk.',
    },
    {
      id: 'B',
      name: 'Directional Acceleration',
      shortDesc: 'Negative GEX or wall broken + CTA aligned = momentum amplified. Trade with the move.',
      fullDesc: 'When net GEX is negative (TRENDING regime) or a key wall has been broken and absorbed, dealer flows amplify directional moves rather than dampening them. Combined with CTA trend-following positioning in the same direction, this creates a high-conviction momentum environment. The strategy is to enter on the first confirmed pullback after the break, trail stops aggressively, and target the next key level (GEX resistance/support). Avoid fading — fighting the flow is costly in this scenario.',
    },
    {
      id: 'C',
      name: 'Fast Through LVN',
      shortDesc: 'Price enters a Low Volume Node = thin area = fast, sharp move to next HVN or key level.',
      fullDesc: 'When price breaks into a Low Volume Node (LVN) on the Volume Profile, historical volume in that zone is thin — meaning there are very few resting orders to slow the move. Price tends to travel quickly to the next High Volume Node or key GEX level. The setup: identify the LVN boundary, wait for a confirmed entry, set a tight stop just inside the LVN, and target the next HVN or key level as T1. These moves can be very fast — execution and discipline on the stop are critical.',
    },
    {
      id: 'D',
      name: 'Structural Accumulation',
      shortDesc: 'Price in HVN zone = high acceptance = choppy two-way price action. Wait for a breakout.',
      fullDesc: 'When price is sitting inside a High Volume Node (HVN) on the Volume Profile, it is in a zone of heavy historical acceptance. There are many participants who bought and sold here and will defend their positions both ways. This creates slow, choppy, mean-reverting price action with no clear directional edge. The correct play is to stand aside and wait for a confirmed breakout of the HVN boundary — at which point the move becomes directional and you can trade the break.',
    },
  ];

  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">Confluence Scenario Matrix</span>
        <span class="card-badge badge-pinned">Active Today: ${active}</span>
      </div>
      <div style="font-size:12px;color:var(--text-secondary);margin-bottom:16px;line-height:1.6;">
        The Confluence Matrix combines GEX regime, Volume Profile position, and CTA bias into one of four defined scenario types. Each scenario has a different trading strategy. The active scenario for today is highlighted.
      </div>
      <div class="confluence-grid">
        ${allScenarios.map(s => `
          <div class="confluence-item${s.id === active ? ' active-scenario' : ''}">
            <div class="conf-scenario-letter">${s.id}</div>
            <div class="conf-scenario-name">${s.name}</div>
            <div class="conf-scenario-desc" style="margin-bottom:8px;">${s.shortDesc}</div>
            ${s.id === active ? `<div style="font-size:11px;color:var(--text-secondary);line-height:1.5;border-top:1px solid var(--border);padding-top:8px;margin-top:4px;">${s.fullDesc}</div>` : ''}
          </div>
        `).join('')}
      </div>
    </div>
    <div class="narrative-card" style="margin-top:0;">
      <div style="font-size:10px;font-weight:700;letter-spacing:1px;text-transform:uppercase;color:var(--text-muted);margin-bottom:10px;">Today's Active Scenario — ${active}: ${data.situation.scenario_name}</div>
      <div style="font-size:13.5px;color:var(--text-secondary);line-height:1.75;">${data.situation.scenario_description}</div>
    </div>
  `;
}

// ============================================================
// KEY LEVELS PANEL
// ============================================================
function renderLevelsPanel(panel, data) {
  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Key Levels — Trade Setup Blocks</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Spot: ${fmtNum(data.spot)} &nbsp;|&nbsp; ${data.metrics.regime} regime</div>
    </div>
    <div class="card" style="padding:14px 18px;">
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.7;">
        Each level below is a structured trade setup. Tap a level to expand the full entry, stop, targets, risk:reward, and the reasoning behind the setup. Levels are listed from the most significant resistance down to the most significant support. The <strong>regime is ${data.metrics.regime}</strong> — ${data.metrics.regime === 'PINNED' ? 'fade the extremes and target the pin' : 'trade momentum with the direction of the break'}.
      </div>
    </div>
    <div class="level-blocks-container">
      ${data.key_levels.map((lv, i) => renderLevelBlock(lv, i)).join('')}
    </div>
  `;
}

function renderLevelBlock(lv, idx) {
  const dotCls = {
    resistance: 'dot-resistance', support: 'dot-support',
    pin: 'dot-pin', trigger: 'dot-trigger',
  }[lv.type] || 'dot-pin';

  const typeLabel = {
    resistance: 'RESISTANCE', support: 'SUPPORT', pin: 'PIN / MAGNET', trigger: 'VOL TRIGGER',
  }[lv.type] || lv.type.toUpperCase();

  const typeBadgeColor = {
    resistance: 'color:var(--accent-red);background:rgba(242,87,87,0.1)',
    support:    'color:var(--accent-green);background:rgba(16,217,139,0.1)',
    pin:        'color:var(--accent-gold);background:rgba(245,200,66,0.1)',
    trigger:    'color:var(--accent-orange);background:rgba(251,146,60,0.1)',
  }[lv.type] || '';

  return `
    <div class="level-block" id="level-block-${idx}">
      <div class="level-block-header" onclick="toggleLevelBlock(${idx})">
        <div class="level-type-dot ${dotCls}"></div>
        <div style="flex:1;">
          <div class="level-block-label">${lv.label}</div>
          <span style="font-size:9px;font-weight:700;letter-spacing:0.6px;padding:2px 6px;border-radius:3px;${typeBadgeColor}">${typeLabel}</span>
        </div>
        <div class="level-block-price">${fmtNum(lv.level)}</div>
        <span style="font-size:18px;color:var(--text-muted);margin-left:8px;" id="level-chevron-${idx}">▾</span>
      </div>
      <div class="level-block-body" id="level-body-${idx}">
        <div class="level-detail-grid">
          <div class="level-detail-item">
            <div class="level-detail-label">Entry</div>
            <div class="level-detail-value">${lv.entry}</div>
          </div>
          <div class="level-detail-item">
            <div class="level-detail-label">Stop Loss</div>
            <div class="level-detail-value" style="color:var(--accent-red);">${lv.stop}</div>
          </div>
          <div class="level-detail-item">
            <div class="level-detail-label">Risk : Reward</div>
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
        <div class="level-context" style="font-size:13px;line-height:1.7;">${lv.context}</div>
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
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Active Confluence: ${data.situation.confluence_scenario} — ${data.situation.scenario_name}</div>
    </div>
    <div class="card" style="padding:14px 18px;">
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.7;">
        Three defined scenarios for today's session, ranked by probability. The <strong>Primary Scenario</strong> is what the GEX regime, Volume Profile, and CTA data all point toward. The Alternative Scenarios cover the key ways the primary could be invalidated. <em>Only trade the scenario that is actively playing out — do not force a trade if price action is not confirming.</em>
      </div>
    </div>
    <div class="scenarios-container">
      ${sc.primary ? renderScenarioCard(sc.primary, 'primary', 'A') : ''}
      ${sc.alt1    ? renderScenarioCard(sc.alt1,    'alt1',    'B') : ''}
      ${sc.alt2    ? renderScenarioCard(sc.alt2,    'alt2',    'C') : ''}
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
          <label>Entry Trigger</label>
          <p>${sc.entry}</p>
        </div>
        <div class="scenario-field">
          <label>Target / Exit</label>
          <p style="color:var(--accent-green);">${sc.target}</p>
        </div>
        <div class="scenario-field">
          <label>Stop Loss</label>
          <p style="color:var(--accent-red);">${sc.stop}</p>
        </div>
        <div class="scenario-field">
          <label>Scenario Invalidation</label>
          <p style="color:var(--accent-orange);">${sc.invalidation}</p>
        </div>
        <div class="scenario-context">
          <div style="font-size:10px;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;color:var(--text-muted);margin-bottom:6px;">Reasoning &amp; Context</div>
          <p style="font-size:13px;line-height:1.75;">${sc.context}</p>
        </div>
      </div>
    </div>
  `;
}

// ============================================================
// ORB SETUP PANEL
// ============================================================
function renderORBPanel(panel, data) {
  const m      = data.metrics;
  const cta    = data.cta || {};
  const mac    = data.macro || {};
  const events = (data.session_structure || {}).key_time_events || [];

  const envData   = orbEnvData(m, cta, mac);
  const biasData  = orbBiasData(data);
  const lvls      = orbKeyLevels(data);

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">ORB Setup — Opening Range Breakout</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Spot: ${fmtNum(data.spot)} &nbsp;|&nbsp; ${m.regime} regime</div>
    </div>
    ${renderORBEnvCard(envData)}
    ${renderORBBiasCard(biasData, data.instrument)}
    ${renderORBTargetsCard(lvls, data)}
    ${renderORBRulesCard(m, lvls, data.instrument)}
    ${renderORBWarningsCard(data, lvls, events)}
  `;
}

// ---- Environment Rating ----
function orbEnvData(m, cta, mac) {
  const regime = m.regime;
  const hasCTABias = ['LONG','MILD_LONG','SHORT'].includes(cta.bias);

  if (regime === 'TRENDING') {
    return {
      rating: 'HIGH CONVICTION', cls: 'orb-env-high',
      headline: 'Breakout conditions are active today.',
      body: `Net GEX is <strong>${fmtGex(m.net_gex)}</strong> — dealers are net short gamma (TRENDING regime). Their hedging flows <em>amplify</em> moves rather than dampening them: as price rises they must buy more, as it falls they must sell more. This is the ideal environment for ORB — breakouts have real dealer-flow momentum behind them and are significantly more likely to follow through to the next GEX level.`,
      timeframeNote: `<strong>5-min ORB:</strong> Valid and high-probability today. Enter on the candle close through the range high/low — in trending conditions price may not return for a retest, so don't wait for one. &nbsp;·&nbsp; <strong>15-min ORB:</strong> Also valid, slightly better signal quality. The wider range gives cleaner stop placement. Both approaches are acceptable.`,
    };
  }
  if (hasCTABias) {
    return {
      rating: 'MODERATE', cls: 'orb-env-moderate',
      headline: 'ORB can work — favour the directional bias, use the 15-min.',
      body: `Net GEX is <strong>${fmtGex(m.net_gex)}</strong> — dealers are net long gamma (PINNED regime). They buy dips and sell rallies, which creates genuine false-break risk. However, there is a directional CTA bias (${(cta.bias||'').replace('_',' ')}) that provides a tailwind in one direction. ORB breaks in the direction of that bias carry meaningfully higher follow-through probability than breaks against it.`,
      timeframeNote: `<strong>5-min ORB:</strong> Treat with caution — pinned conditions create high false-break noise in the first five minutes. Only trade if the break has clear volume confirmation. &nbsp;·&nbsp; <strong>15-min ORB:</strong> Strongly preferred today. The wider range is harder to fake and gives more time for noise to resolve before you commit.`,
    };
  }
  return {
    rating: 'CAUTION', cls: 'orb-env-caution',
    headline: 'Classic mean-reversion day — ORB has a lower success rate today.',
    body: `Net GEX is <strong>${fmtGex(m.net_gex)}</strong> — dealers are net long gamma (PINNED regime) with no strong CTA directional bias. Dealer hedging flows actively oppose breakouts. ORB setups in this environment typically break the range, run 10–20 points, then reverse hard as dealer flows kick in. <strong>The better strategy today is fading the GEX walls back toward the Max GEX Pin — see the Key Levels and Scenarios tabs for those setups.</strong>`,
    timeframeNote: `<strong>5-min ORB:</strong> Not recommended today — false-break probability is high in a pinned, neutral regime. &nbsp;·&nbsp; <strong>15-min ORB:</strong> If you trade ORB today, the 15-min is the only timeframe worth considering. Require volume confirmation AND a second candle hold outside the range before entry.`,
  };
}

function renderORBEnvCard(r) {
  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">Today's ORB Environment</span>
        <span class="orb-env-badge ${r.cls}">${r.rating}</span>
      </div>
      <div style="font-size:13px;font-weight:700;color:var(--text-primary);margin-bottom:10px;">${r.headline}</div>
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.7;margin-bottom:14px;">${r.body}</div>
      <div class="orb-timeframe-note">${r.timeframeNote}</div>
    </div>
  `;
}

// ---- Directional Bias ----
function orbBiasData(data) {
  const m   = data.metrics;
  const cta = data.cta || {};
  const spot = data.spot;
  let score = 0;
  const factors = [];

  if (cta.bias === 'LONG')      { score += 2; factors.push({ dir:'long',    text:'CTA LONG — systematic trend funds are positioned long, a tailwind for upside ORB breaks.' }); }
  else if (cta.bias === 'MILD_LONG') { score += 1; factors.push({ dir:'long',    text:'CTA MILD LONG — trend followers lean long, mild upside tailwind.' }); }
  else if (cta.bias === 'SHORT')     { score -= 2; factors.push({ dir:'short',   text:'CTA SHORT — systematic funds are positioned short, a tailwind for downside ORB breaks.' }); }
  else                               {             factors.push({ dir:'neutral', text:'CTA NEUTRAL — no directional signal from trend-following funds today.' }); }

  if (m.put_call_ratio < 0.85)      { score += 1; factors.push({ dir:'long',    text:`PCR ${m.put_call_ratio.toFixed(2)} — call-heavy positioning, options market leaning bullish.` }); }
  else if (m.put_call_ratio > 1.10) { score -= 1; factors.push({ dir:'short',   text:`PCR ${m.put_call_ratio.toFixed(2)} — put-heavy, bearish hedging activity dominant.` }); }
  else                              {             factors.push({ dir:'neutral', text:`PCR ${m.put_call_ratio.toFixed(2)} — balanced put/call positioning, no strong lean.` }); }

  const skew = m.iv_skew_ratio || 1;
  if (skew > 1.10)      { score -= 1; factors.push({ dir:'short',   text:`IV Skew ${skew.toFixed(2)} — put options priced at a premium, institutional bearish hedging present.` }); }
  else if (skew < 0.95) { score += 1; factors.push({ dir:'long',    text:`IV Skew ${skew.toFixed(2)} — calls priced at a slight premium, mild bullish options sentiment.` }); }

  const pin = m.max_gex_strike;
  if (spot < pin)      { score += 1; factors.push({ dir:'long',    text:`Spot (${fmtNum(spot)}) is ${(pin-spot).toFixed(1)} pts below Max GEX Pin (${fmtNum(pin)}) — gravitational pull is upward.` }); }
  else if (spot > pin) { score -= 1; factors.push({ dir:'short',   text:`Spot (${fmtNum(spot)}) is ${(spot-pin).toFixed(1)} pts above Max GEX Pin (${fmtNum(pin)}) — gravitational pull is downward.` }); }
  else                 {             factors.push({ dir:'neutral', text:`Spot is at the Max GEX Pin — balanced pin pull, no directional lean from this.` }); }

  let bias, biasCls, biasDesc;
  if (score >= 2) {
    bias = 'LONG BIAS'; biasCls = 'orb-bias-long';
    biasDesc = `Multiple factors point toward upside. When the opening range forms, a break to the upside carries higher follow-through probability. Treat long ORB as your A-setup and short ORB as a lower-conviction counter-trade requiring extra confirmation.`;
  } else if (score <= -2) {
    bias = 'SHORT BIAS'; biasCls = 'orb-bias-short';
    biasDesc = `Multiple factors point toward downside. A break below the opening range low carries higher follow-through probability. Treat short ORB as your A-setup. Long ORB against this bias is lower conviction — require extra confirmation before entry.`;
  } else {
    bias = 'NEUTRAL'; biasCls = 'orb-bias-neutral';
    biasDesc = `No strong directional lean — factors are balanced or conflicting. Trade whichever direction the opening range actually breaks, with equal conviction for both. Focus on the quality of the break (volume, candle close) rather than direction.`;
  }
  return { score, bias, biasCls, biasDesc, factors };
}

function renderORBBiasCard(b, instrument) {
  const icon = b.bias === 'LONG BIAS' ? '↑' : b.bias === 'SHORT BIAS' ? '↓' : '↔';
  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">Directional Bias — Which ORB Break to Favour</span>
        <span class="orb-bias-badge ${b.biasCls}">${icon} ${b.bias}</span>
      </div>
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.7;margin-bottom:16px;">${b.biasDesc}</div>
      <div class="orb-factors">
        ${b.factors.map(f => `
          <div class="orb-factor">
            <span class="orb-factor-dot orb-factor-${f.dir}"></span>
            <span style="font-size:12px;color:var(--text-secondary);line-height:1.5;">${f.text}</span>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// ---- Pre-mapped GEX Targets ----
function orbKeyLevels(data) {
  const m   = data.metrics;
  const mac = data.macro || {};
  const spot = data.spot;

  const pool = [
    { name: 'Call Wall',   price: m.call_wall,       role: 'Hard ceiling — primary dealer selling zone', type: 'resistance' },
    { name: 'Max GEX Pin', price: m.max_gex_strike,  role: 'Gravitational anchor — strongest pull',      type: 'pin' },
    { name: 'Zero GEX',   price: m.zero_gex_strike,  role: 'Volatility trigger — gamma flips here',      type: 'trigger' },
    { name: 'Max Pain',   price: m.max_pain,          role: 'Expiry magnet',                              type: 'pain' },
    { name: 'Put Wall',   price: m.put_wall,          role: 'Hard floor — primary dealer buying zone',    type: 'support' },
  ];
  if (mac.prev_day_high) pool.push({ name: 'Prev Day High', price: mac.prev_day_high, role: 'Prior session structural reference', type: 'pdh' });
  if (mac.prev_day_low)  pool.push({ name: 'Prev Day Low',  price: mac.prev_day_low,  role: 'Prior session structural reference', type: 'pdl' });

  const above = pool.filter(l => l.price > spot).sort((a,b) => a.price - b.price);
  const below = pool.filter(l => l.price < spot).sort((a,b) => b.price - a.price);
  return { above, below, spot };
}

function renderORBTargetsCard(lvls, data) {
  const { above, below, spot } = lvls;
  const m = data.metrics;

  function typeColor(t) {
    return { resistance:'var(--accent-red)', pin:'var(--accent-gold)', trigger:'var(--accent-orange)',
             pain:'var(--accent-purple)', support:'var(--accent-green)', pdh:'var(--text-secondary)', pdl:'var(--text-secondary)' }[t] || 'var(--text-secondary)';
  }

  function levelRows(list, isAbove) {
    if (!list.length) return `<div style="padding:12px;color:var(--text-muted);font-size:12px;">No GEX levels on this side of spot.</div>`;
    return list.map((lv, i) => {
      const badge = i === 0 ? '<span class="orb-t-badge orb-t1">T1</span>' : i === 1 ? '<span class="orb-t-badge orb-t2">T2</span>' : '<span class="orb-t-badge orb-t-ext">EXT</span>';
      const dist  = isAbove ? (lv.price - spot).toFixed(1) + ' pts above' : (spot - lv.price).toFixed(1) + ' pts below';
      return `
        <div class="orb-target-level${i < 2 ? ' orb-target-highlight' : ''}">
          <div style="display:flex;align-items:center;gap:8px;">
            ${badge}
            <span style="font-size:12px;font-weight:700;color:${typeColor(lv.type)};flex:1;">${lv.name}</span>
            <span style="font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:700;color:${typeColor(lv.type)};">${fmtNum(lv.price)}</span>
          </div>
          <div style="font-size:11px;color:var(--text-muted);margin-top:3px;padding-left:32px;">${lv.role} &nbsp;·&nbsp; ${dist}</div>
        </div>`;
    }).join('');
  }

  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">Pre-Mapped GEX Targets — Long &amp; Short ORB</span>
      </div>
      <div style="font-size:12px;color:var(--text-secondary);line-height:1.6;margin-bottom:14px;">
        The opening range forms at market open — but the GEX levels that will act as targets, stops, and ceilings are known right now. Once the range is set, slot these in as your reference map. Spot reference: <strong>${fmtNum(spot)}</strong>.
      </div>
      <div class="orb-targets-grid">
        <div class="orb-target-col">
          <div class="orb-target-header orb-target-long">↑ LONG ORB — Levels Above Spot</div>
          <div style="font-size:11px;color:var(--text-muted);padding:8px 14px 4px;">T1 = first target. T2 = extended run. EXT = only if momentum strong.</div>
          <div class="orb-target-levels-list">${levelRows(above, true)}</div>
          <div class="orb-target-footer orb-footer-long">Stop reference: below ORB low &nbsp;·&nbsp; First key level below: <strong>${below[0] ? below[0].name + ' ' + fmtNum(below[0].price) : 'N/A'}</strong></div>
        </div>
        <div class="orb-target-col">
          <div class="orb-target-header orb-target-short">↓ SHORT ORB — Levels Below Spot</div>
          <div style="font-size:11px;color:var(--text-muted);padding:8px 14px 4px;">T1 = first target. T2 = extended run. EXT = only if momentum strong.</div>
          <div class="orb-target-levels-list">${levelRows(below, false)}</div>
          <div class="orb-target-footer orb-footer-short">Stop reference: above ORB high &nbsp;·&nbsp; First key level above: <strong>${above[0] ? above[0].name + ' ' + fmtNum(above[0].price) : 'N/A'}</strong></div>
        </div>
      </div>
    </div>
  `;
}

// ---- Regime-Specific ORB Rules ----
function renderORBRulesCard(m, lvls, instrument) {
  const regime   = m.regime;
  const { above, below } = lvls;
  const pin      = fmtNum(m.max_gex_strike);
  const zeroGex  = fmtNum(m.zero_gex_strike);
  const callWall = fmtNum(m.call_wall);
  const putWall  = fmtNum(m.put_wall);
  const t1Long   = above[0] ? `${above[0].name} (${fmtNum(above[0].price)})` : 'first GEX level above';
  const t1Short  = below[0] ? `${below[0].name} (${fmtNum(below[0].price)})` : 'first GEX level below';

  const rules = regime === 'TRENDING' ? [
    `<strong>Both 5-min and 15-min ORB are valid today.</strong> Dealer flows amplify breakouts in TRENDING regime — the setup has real momentum behind it in both timeframes.`,
    `<strong>Enter on the candle close through the ORB level.</strong> In trending conditions price may not return for a retest. If it does retest and holds, that's an even stronger entry — but don't wait for one that may never come.`,
    `<strong>Long ORB primary target: ${t1Long}.</strong> Trail stop to breakeven once T1 is hit and let T2 run. Full runs to the Call Wall (${callWall}) are realistic on strong trending days.`,
    `<strong>Short ORB primary target: ${t1Short}.</strong> Once Zero GEX (${zeroGex}) is broken on a short ORB, expect an acceleration — the volatility amplification kicks in fully below that level. Target Put Wall (${putWall}) as T2.`,
    `<strong>Trail stops aggressively.</strong> Trending moves run further and faster than you expect. Use a trailing stop rather than fixed exit — your job is to stay in, not just reach T1.`,
    `<strong>If the break reverses back inside the range within 2 candles, exit without hesitation.</strong> False breaks do happen even in trending regimes. The stop is your insurance — honour it and re-evaluate.`,
  ] : [
    `<strong>Strongly favour the 15-min ORB over the 5-min today.</strong> PINNED regime means dealer flows actively oppose early breakout attempts. The first 5 minutes are high-noise — the 15-min range is much harder to fake.`,
    `<strong>Volume confirmation is non-negotiable in PINNED conditions.</strong> A low-volume break is almost certainly a dealer-flow false break being absorbed. If the break doesn't have notably above-average volume, skip it.`,
    `<strong>Require two candle closes beyond the range before entry.</strong> One candle is not enough in a pinned environment. The second close confirms dealer flows have not immediately capped the move.`,
    `<strong>Long ORB primary target: ${t1Long} — not the Call Wall.</strong> In PINNED conditions, dealer selling starts building before the Call Wall (${callWall}). Take T1, bank profit, and reassess before extending to T2.`,
    `<strong>Short ORB primary target: ${t1Short}.</strong> Genuine acceleration only begins if Zero GEX (${zeroGex}) is cleanly breached — that is the volatility trigger. Before that, treat every bounce as a potential reversal.`,
    `<strong>If price breaks the range and reverses back inside within 3 candles, exit immediately.</strong> This is the classic pinned false break. No second-guessing — out. Dealer flows just reasserted themselves.`,
    `<strong>When in doubt, the better trade today is the mean-reversion fade at the GEX walls targeting the Max GEX Pin (${pin}).</strong> See Key Levels for those pre-built setups.`,
  ];

  return `
    <div class="card">
      <div class="card-header">
        <span class="card-title">ORB Rules for Today — ${regime} Regime</span>
        <span class="card-badge ${regime === 'TRENDING' ? 'badge-trending' : 'badge-pinned'}">${regime}</span>
      </div>
      <div class="orb-rules-list">
        ${rules.map((r, i) => `
          <div class="orb-rule">
            <div class="orb-rule-num">${i+1}</div>
            <div class="orb-rule-text">${r}</div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// ---- Warnings / Pre-Session Checklist ----
function renderORBWarningsCard(data, lvls, events) {
  const m    = data.metrics;
  const mac  = data.macro || {};
  const spot = data.spot;
  const vix  = mac.vix || 0;

  const distUp   = m.call_wall - spot;
  const distDown = spot - m.put_wall;

  function roomRating(d) {
    if (d < 20) return { cls:'orb-room-tight',    label:'TIGHT' };
    if (d < 50) return { cls:'orb-room-moderate', label:'MODERATE' };
    return          { cls:'orb-room-clear',    label:'GOOD ROOM' };
  }

  const upRoom   = roomRating(distUp);
  const downRoom = roomRating(distDown);

  const upNote   = distUp < 20   ? 'Call Wall is very close — long ORB has minimal upside before hitting the ceiling. Only worthwhile if targeting the Max GEX Pin, not the wall itself.'
                 : distUp < 50   ? 'Moderate room above. Long ORB can work but manage targets — the ceiling is relatively close.'
                 :                 'Good room above. Long ORB has space to run to T1 and potentially T2 before hitting the Call Wall.';
  const downNote = distDown < 20  ? 'Put Wall is very close — short ORB has minimal downside before hitting the floor. Low-reward setup unless Zero GEX breaks and accelerates.'
                 : distDown < 50  ? 'Moderate room below. Short ORB can work — manage targets and watch the Zero GEX level carefully.'
                 :                  'Good room below. Short ORB has space to run to T1 and T2 before the Put Wall floor.';

  return `
    <div class="card">
      <div class="card-header"><span class="card-title">Pre-Session Checklist &amp; Warnings</span></div>

      <div class="orb-section-label">Room to Run</div>
      <div class="orb-room-strip">
        <div class="orb-room-item">
          <div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:6px;">↑ Long ORB — upside to Call Wall</div>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:800;color:var(--accent-red);">${distUp.toFixed(1)}<span style="font-size:12px;font-weight:400;"> pts</span></span>
            <span class="orb-room-badge ${upRoom.cls}">${upRoom.label}</span>
          </div>
          <div style="font-size:11px;color:var(--text-muted);line-height:1.5;">${upNote}</div>
        </div>
        <div class="orb-room-item">
          <div style="font-size:12px;font-weight:700;color:var(--text-primary);margin-bottom:6px;">↓ Short ORB — downside to Put Wall</div>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="font-family:'JetBrains Mono',monospace;font-size:20px;font-weight:800;color:var(--accent-green);">${distDown.toFixed(1)}<span style="font-size:12px;font-weight:400;"> pts</span></span>
            <span class="orb-room-badge ${downRoom.cls}">${downRoom.label}</span>
          </div>
          <div style="font-size:11px;color:var(--text-muted);line-height:1.5;">${downNote}</div>
        </div>
      </div>

      ${vix > 25 ? `
      <div class="orb-vix-warning">
        ⚠️ <strong>VIX ${vix.toFixed(1)} — elevated volatility.</strong> Intraday ranges will be wider than normal. Widen your stops proportionally and reduce position size by 20–30% to account for the noisier price action.
      </div>` : ''}

      ${events.length ? `
      <div class="orb-section-label" style="margin-top:16px;">Key Events — Stand Aside 5 Min Either Side</div>
      <div style="display:flex;flex-direction:column;gap:6px;">
        ${events.map(e => `
          <div style="display:flex;align-items:center;gap:10px;padding:8px 12px;background:rgba(251,146,60,0.08);border:1px solid rgba(251,146,60,0.2);border-radius:6px;">
            <span style="font-size:15px;">⚡</span>
            <span style="font-size:12.5px;color:var(--text-primary);font-weight:500;">${e}</span>
          </div>
        `).join('')}
        <div style="font-size:11px;color:var(--text-muted);padding:4px 4px 0;line-height:1.5;">During news events, spreads widen and stops can be hunted. Reduce size or stand aside until the candle following the event has closed and direction is confirmed.</div>
      </div>` : ''}
    </div>
  `;
}

// ============================================================
// UTILITY / HELPER FUNCTIONS
// ============================================================
function fmtNum(n) {
  if (n === null || n === undefined || n === 0) return n === 0 ? '0' : '—';
  return Number(n).toLocaleString('en-GB', {
    minimumFractionDigits: Math.abs(n) % 1 !== 0 ? 1 : 0,
    maximumFractionDigits: Math.abs(n) < 100 ? 2 : 1,
  });
}

function fmtGex(v) {
  if (v === null || v === undefined) return '—';
  const sign = v >= 0 ? '+' : '';
  return `${sign}$${Number(v).toFixed(2)}B`;
}

function fmtOI(n) {
  if (n >= 1000000) return (n/1000000).toFixed(1)+'M';
  if (n >= 1000) return (n/1000).toFixed(1)+'K';
  return n.toString();
}

function fmtTime(ts) {
  try {
    const d = new Date(ts);
    return d.toLocaleDateString('en-GB', { weekday:'short', day:'2-digit', month:'short' }) +
      ' ' + d.toLocaleTimeString('en-GB', { hour:'2-digit', minute:'2-digit' }) + ' BST';
  } catch { return ts || '—'; }
}

function metricItem(label, value, note, valCls='') {
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
  return `<span class="level-tag ${cls}">${tag.replace(/[[\]]/g,'')}</span>`;
}

function probClass(p) {
  const map = { 'HIGH':'prob-high','MEDIUM-HIGH':'prob-medium-high','MEDIUM':'prob-medium','LOW-MEDIUM':'prob-low-medium','LOW':'prob-low' };
  return map[p] || 'prob-medium';
}

function biasClass(b) {
  const map = { 'LONG':'bias-long','SHORT':'bias-short','RANGE':'bias-range','NEUTRAL':'bias-neutral' };
  return map[b] || 'bias-neutral';
}

function renderEmptyState() {
  return `
    <div class="empty-state">
      <div class="empty-state-icon">📭</div>
      <div class="empty-state-text">No scan data available for ${STATE.instrument}.<br>Run the agent with <code>--output both</code> to populate the dashboard with live data.</div>
    </div>
  `;
}

// ============================================================
// PROXY INSTRUMENTS — UK100 / GER40 (no direct options data)
// ============================================================

function renderProxyChartsPanel(panel, data) {
  const mac  = data.macro || {};
  const ss   = data.session_structure || {};
  const m    = data.metrics;
  const spot = data.spot;

  const pdh       = mac.prev_day_high;
  const pdl       = mac.prev_day_low;
  const todayOpen = ss.today_open;
  const sesHigh   = ss.session_high;
  const sesLow    = ss.session_low;
  const range     = (pdh && pdl) ? (pdh - pdl) : 0;
  const spotPct   = range > 0 ? Math.max(2, Math.min(97, (spot - pdl) / range * 100)) : 50;
  const openPct   = (todayOpen && range > 0) ? Math.max(2, Math.min(97, (todayOpen - pdl) / range * 100)) : null;

  const spxRegime = m.spx_regime || m.regime || 'NEUTRAL';
  const spxGex    = m.spx_gex_bn || 0;
  const regimeCls = spxRegime === 'PINNED' ? 'badge-pinned' : spxRegime === 'TRENDING' ? 'badge-trending' : 'badge-neutral';
  const corrPct   = data.instrument === 'GER40' ? 87 : 78;

  panel.innerHTML = `
    <div class="content-header">
      <div>
        <div class="spot-strip">
          <div class="spot-instrument">${data.instrument}</div>
          <div class="spot-price">${fmtNum(spot)}</div>
          <div>
            <div class="spot-meta">
              SPX Regime (proxy): <strong>${spxRegime}</strong> &nbsp;|&nbsp; Scan: ${fmtTime(data.scan_time)}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card" style="padding:12px 16px;">
      <div class="proxy-notice">
        <span class="proxy-notice-icon">ℹ</span>
        <div>
          <strong>Cross-Market Proxy Mode</strong> — No liquid free options data exists for ${data.instrument}.
          GEX regime is derived from SPX (US500), which has a <strong>${corrPct}% correlation</strong> with ${data.instrument}.
          Session structure levels from CTrader live candles are the primary reference.
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">SPX GEX Regime → ${data.instrument} Implication</span>
        <span class="card-badge ${regimeCls}">${spxRegime}</span>
      </div>
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.75;margin-bottom:14px;">
        ${data.situation && data.situation.narrative ? data.situation.narrative : regimeFullExplainer(spxRegime, spxGex)}
      </div>
      <div class="macro-strip">
        ${macroItem('SPX Regime', spxRegime, 'S&P 500 GEX regime applied as proxy')}
        ${macroItem('Correlation', corrPct + '%', 'Historical correlation with SPX')}
        ${macroItem('VIX', (mac.vix||0).toFixed(1), vixLabel(mac.vix))}
        ${macroItem('DXY', (mac.dxy||0).toFixed(2), 'US Dollar Index')}
        ${macroItem('US 10Y', (mac.us10y||0).toFixed(2) + '%', 'Treasury yield')}
      </div>
    </div>

    ${range > 0 ? `
    <div class="card">
      <div class="card-header"><span class="card-title">Session Range — Spot vs Prior Day H/L</span></div>
      <div class="prc-wrapper">
        <div class="prc-pdh-row">
          <span class="prc-extreme-val" style="color:var(--accent-red)">${fmtNum(pdh)}</span>
          <span class="prc-extreme-lbl">PDH — Resistance</span>
          <span class="prc-dist" style="color:var(--accent-red)">▲ ${fmtNum(pdh - spot)} to PDH</span>
        </div>
        <div class="prc-track-container">
          <div class="prc-track">
            <div class="prc-fill" style="width:${spotPct}%"></div>
            ${openPct !== null ? `<div class="prc-open-mark" style="left:${openPct}%" title="Today Open: ${fmtNum(todayOpen)}"><div class="prc-open-dot"></div><div class="prc-open-label">Open</div></div>` : ''}
            <div class="prc-spot-pin" style="left:${spotPct}%">
              <div class="prc-spot-dot"></div>
              <div class="prc-spot-label">${fmtNum(spot)} LIVE</div>
            </div>
          </div>
        </div>
        <div class="prc-pdl-row">
          <span class="prc-extreme-val" style="color:var(--accent-green)">${fmtNum(pdl)}</span>
          <span class="prc-extreme-lbl">PDL — Support</span>
          <span class="prc-dist" style="color:var(--accent-green)">▼ ${fmtNum(spot - pdl)} to PDL</span>
        </div>
      </div>
      <div class="proxy-struct-grid">
        ${structMetric('Live Spot',     fmtNum(spot),     'Current price',                  'val-gold')}
        ${todayOpen ? structMetric('Today Open', fmtNum(todayOpen), spot > todayOpen ? '▲ Above open' : '▼ Below open', spot > todayOpen ? 'val-green' : 'val-red') : ''}
        ${pdh ? structMetric('PDH',     fmtNum(pdh),      fmtNum(pdh - spot) + ' above spot','val-red')   : ''}
        ${pdl ? structMetric('PDL',     fmtNum(pdl),      fmtNum(spot - pdl) + ' below spot','val-green') : ''}
        ${sesHigh ? structMetric('Session High', fmtNum(sesHigh), 'Intraday high', '') : ''}
        ${sesLow  ? structMetric('Session Low',  fmtNum(sesLow),  'Intraday low',  '') : ''}
        ${structMetric('Daily Range', fmtNum(range), 'PDH minus PDL', 'val-gold')}
        ${structMetric('Position',    spotPct.toFixed(1) + '%', 'of range from PDL',
          spotPct > 70 ? 'val-red' : spotPct < 30 ? 'val-green' : '')}
      </div>
    </div>` : ''}
  `;
}

function structMetric(label, value, sub, cls) {
  return `
    <div class="proxy-struct-item">
      <div class="psi-label">${label}</div>
      <div class="psi-value ${cls}">${value}</div>
      ${sub ? `<div class="psi-sub">${sub}</div>` : ''}
    </div>
  `;
}

function renderProxyMetricsPanel(panel, data) {
  renderProxyChartsPanel(panel, data);
  const mac = data.macro || {};
  const extra = document.createElement('div');
  extra.className = 'card';
  extra.innerHTML = `
    <div class="card-header"><span class="card-title">Macro Snapshot — Market Context</span></div>
    <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.65;margin-bottom:16px;">
      ${macroNarrative(mac, data.instrument)}
    </div>
    <div class="macro-strip">
      ${macroItem('VIX',       (mac.vix||0).toFixed(2),        mac.vix_signal  || vixLabel(mac.vix))}
      ${macroItem('DXY',       (mac.dxy||0).toFixed(2),        'US Dollar Index')}
      ${macroItem('US 10Y',    (mac.us10y||0).toFixed(2) + '%','US Treasury yield')}
      ${macroItem('Prev High', fmtNum(mac.prev_day_high),      'Yesterday\'s session high')}
      ${macroItem('Prev Low',  fmtNum(mac.prev_day_low),       'Yesterday\'s session low')}
      ${macroItem('Wkly Open', fmtNum(mac.weekly_open),        'Monday\'s opening price')}
    </div>
  `;
  panel.appendChild(extra);
}

function renderProxyOIPanel(panel, data) {
  const m         = data.metrics;
  const spxRegime = m.spx_regime || m.regime || 'NEUTRAL';
  const regimeCls = spxRegime === 'PINNED' ? 'badge-pinned' : spxRegime === 'TRENDING' ? 'badge-trending' : 'badge-neutral';
  const corrPct   = data.instrument === 'GER40' ? 87 : 78;

  panel.innerHTML = `
    <div class="content-header">
      <div class="content-title">Open Interest — Cross-Market Reference</div>
      <div class="content-subtitle">${data.instrument} &nbsp;|&nbsp; Spot: ${fmtNum(data.spot)}</div>
    </div>

    <div class="card" style="padding:20px 24px;">
      <div class="proxy-notice" style="margin-bottom:16px;">
        <span class="proxy-notice-icon">ℹ</span>
        <div>
          <strong>No direct OI data for ${data.instrument}</strong> —
          ${data.instrument === 'UK100' ? 'FTSE 100' : 'DAX 40'} options are not freely available with sufficient liquidity for GEX/OI modelling.
          The ETF proxies (${data.instrument === 'UK100' ? 'EWU' : 'EWG'}) traded on US markets have too little open interest
          to generate reliable dealer positioning data.
        </div>
      </div>
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.8;">
        <strong>What to use instead:</strong><br><br>
        <strong>1. Session Structure (PDH / PDL)</strong> — The most reliable, market-generated reference levels
        for ${data.instrument}. Prior day high and low represent where price was accepted and rejected yesterday.
        These are the de facto support and resistance for today's session.<br><br>
        <strong>2. SPX GEX as Global Risk Proxy</strong> — SPX has a <strong>${corrPct}% correlation</strong> with ${data.instrument}.
        The dealer gamma regime on SPX (${spxRegime}) tends to set the tone for global index volatility.
        PINNED SPX = expect range-bound, lower-volatility sessions across all indices.
        TRENDING SPX = expect directional, higher-range sessions globally.<br><br>
        <strong>3. VIX as Volatility Gauge</strong> — VIX tracks closely with VFTSE and VDAX.
        VIX above 20 = widen stops and expect larger intraday ranges on ${data.instrument}.
      </div>
    </div>

    <div class="card">
      <div class="card-header">
        <span class="card-title">SPX Regime → ${data.instrument} Volatility Implication</span>
        <span class="card-badge ${regimeCls}">${spxRegime}</span>
      </div>
      <div style="font-size:12.5px;color:var(--text-secondary);line-height:1.75;">
        ${data.situation && data.situation.narrative ? data.situation.narrative : regimeFullExplainer(spxRegime, m.spx_gex_bn || 0)}
      </div>
    </div>

    ${data.key_levels && data.key_levels.length ? `
    <div class="card">
      <div class="card-header"><span class="card-title">Session Key Levels — PDH / PDL Reference</span></div>
      <table class="data-table">
        <thead><tr><th>Level</th><th>Price</th><th>Role</th></tr></thead>
        <tbody>
          ${data.key_levels.map(lv => `
            <tr class="${lv.type === 'resistance' ? 'row-resistance' : lv.type === 'support' ? 'row-support' : ''}">
              <td style="font-weight:600;">${lv.label}</td>
              <td style="font-family:'JetBrains Mono',monospace;font-weight:700;">${fmtNum(lv.level)}</td>
              <td style="font-size:11px;color:var(--text-muted);">${lv.note || ''}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>` : ''}
  `;
}

// ============================================================
// REFRESH BUTTON — GitHub Actions manual trigger
// ============================================================

const GITHUB_DISPATCH_URL =
  'https://api.github.com/repos/pravindersamra/ctrader-bots/actions/workflows/run-agent.yml/dispatches';

function triggerAgentRefresh() {
  const token = localStorage.getItem('gex_github_pat');
  if (!token) { showTokenModal(); return; }

  const btn = document.getElementById('refresh-btn');
  if (btn) { btn.disabled = true; btn.textContent = '↺ Sending...'; }

  fetch(GITHUB_DISPATCH_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Accept': 'application/vnd.github+json',
      'Content-Type': 'application/json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    body: JSON.stringify({ ref: 'main' }),
  })
  .then(res => {
    if (res.status === 204) {
      if (btn) btn.textContent = '✓ Triggered! (~2-3 min)';
      setTimeout(() => {
        if (btn) { btn.textContent = '↺ Refresh'; btn.disabled = false; }
      }, 10000);
    } else if (res.status === 401) {
      // Credentials rejected — token is wrong or expired
      localStorage.removeItem('gex_github_pat');
      if (btn) { btn.textContent = '↺ Refresh'; btn.disabled = false; }
      showTokenModal('HTTP 401 — Token rejected. Re-enter the token (make sure you copied the full ghp_... string).');
    } else if (res.status === 403) {
      // Authenticated but no permission — wrong scope
      if (btn) { btn.textContent = '↺ Refresh'; btn.disabled = false; }
      showTokenModal('HTTP 403 — Token lacks permission. On the token page, make sure the "workflow" checkbox is ticked. You may need to regenerate the token.');
    } else if (res.status === 404) {
      if (btn) { btn.textContent = '↺ Refresh'; btn.disabled = false; }
      alert('HTTP 404 — Workflow not found. The run-agent.yml may still be deploying. Wait 1 minute and try again.');
    } else {
      res.text().then(t => {
        console.error('Dispatch failed:', res.status, t);
        if (btn) { btn.textContent = '↺ Refresh'; btn.disabled = false; }
        alert(`Refresh failed (HTTP ${res.status}). Open browser console for details.`);
      });
    }
  })
  .catch(err => {
    console.error('Refresh error:', err);
    if (btn) { btn.textContent = '↺ Refresh'; btn.disabled = false; }
    alert('Could not reach GitHub API. Check your internet connection.');
  });
}

function showTokenModal(msg = '') {
  const modal = document.getElementById('token-modal');
  if (!modal) return;
  const msgEl = document.getElementById('token-modal-msg');
  if (msgEl) msgEl.textContent = msg;
  const inp = document.getElementById('token-modal-input');
  if (inp) inp.value = '';
  modal.style.display = 'flex';
  if (inp) setTimeout(() => inp.focus(), 60);
}

function closeTokenModal() {
  const modal = document.getElementById('token-modal');
  if (modal) modal.style.display = 'none';
}

function saveTokenAndRefresh() {
  const inp = document.getElementById('token-modal-input');
  if (!inp || !inp.value.trim()) return;
  localStorage.setItem('gex_github_pat', inp.value.trim());
  closeTokenModal();
  triggerAgentRefresh();
}
