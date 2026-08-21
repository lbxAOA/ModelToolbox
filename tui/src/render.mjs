import { sanitizeText } from './protocol.mjs';

const screens = ['Overview', 'Session', 'Integrations', 'Skills', 'Profiles', 'Router', 'Marketplace'];

export function createState() {
  return { phase: 'loading', screen: 0, snapshot: null, profiles: [], adapters: [], integrations: [], marketplace: null, recommendations: [], router: null, listener: null, activity: [], profileIndex: 0, profileDetail: null, plan: null, routerPlan: null, message: null, confirmApply: false, confirmRouterAction: null };
}

function pad(value, width) {
  return sanitizeText(value).slice(0, width).padEnd(width);
}

function selectedProfile(state) {
  return state.profiles[state.profileIndex] || null;
}

function renderProfiles(state, lines, rows) {
  const profile = selectedProfile(state);
  if (!state.profiles.length) {
    lines.push('No profiles configured. Use mtb profiles-create to add one.');
    return;
  }
  lines.push('Profiles (j/k or arrows to choose; Enter selects locally)');
  const adapters = state.adapters || [];
  if (adapters.length) lines.push(`Integrations: ${adapters.map((item) => `${sanitizeText(item.name)} ${item.available ? 'enabled' : 'pending'}`).join(' · ')}`);
  for (let index = 0; index < Math.min(state.profiles.length, Math.max(1, rows - 13)); index += 1) {
    const item = state.profiles[index];
    const cursor = index === state.profileIndex ? '>' : ' ';
    const selected = item.selected ? '*' : ' ';
    lines.push(`${cursor}${selected} ${pad(item.name, 20)} ${pad(item.adapter_name || item.adapter_id, 16)} ${item.adapter_available ? 'enabled' : 'pending'} ${sanitizeText(item.base_url)}`);
  }
  if (!profile) return;
  lines.push('');
  lines.push(`Selected row: ${sanitizeText(profile.id)}  Model: ${sanitizeText(profile.model || 'default')}`);
  if (!profile.adapter_available) lines.push(sanitizeText(profile.adapter_message || 'This application adapter is pending verification.'));
  if (state.plan) {
    lines.push(`Preview: ${state.plan.changes?.length || 0} managed field change(s).`);
    if (state.plan.message) lines.push(sanitizeText(state.plan.message));
    for (const change of (state.plan.changes || []).slice(0, 3)) lines.push(`  ${sanitizeText(change.field)}: ${sanitizeText(change.from ?? 'unset')} -> ${sanitizeText(change.to)}`);
    lines.push(state.confirmApply ? 'Apply this preview? [y] confirm / [Esc] cancel' : 'Press [a] to request apply confirmation.');
  } else if (state.profileDetail) {
    lines.push(`Target: ${sanitizeText(state.profileDetail.target || 'not inspected')}  Status: ${sanitizeText(state.profileDetail.status || 'ready')}`);
  } else {
    lines.push('[i] inspect target  [p] preview changes');
  }
}

function renderRouter(state, lines) {
  const router = state.router;
  if (!router) { lines.push('Router status is unavailable.'); return; }
  lines.push(`Mode: ${sanitizeText(router.state)}  Policy revision: ${sanitizeText(String(router.revision))}`);
  if (router.active) lines.push(`Active profile: ${sanitizeText(router.active.profile_id)}  ${sanitizeText(router.active.inbound_protocol)} → ${sanitizeText(router.active.upstream_protocol)}`);
  else lines.push('Direct mode: no route policy is active.');
  const listener = state.listener;
  lines.push(listener?.running ? `Listener: running at ${sanitizeText(listener.host)}:${sanitizeText(String(listener.port))}` : 'Listener: stopped (policy can be configured independently).');
  const profile = selectedProfile(state);
  if (state.routerPlan) {
    lines.push(`Route preview: revision ${sanitizeText(String(state.routerPlan.revision))} → ${sanitizeText(String(state.routerPlan.next_revision))}`);
    for (const change of (state.routerPlan.changes || []).slice(0, 3)) lines.push(`  ${sanitizeText(change.field)}: ${sanitizeText(change.from ?? 'unset')} → ${sanitizeText(change.to)}`);
  } else if (profile) {
    lines.push(`Selected profile: ${sanitizeText(profile.name)}  [p] preview route (${sanitizeText(profile.adapter_id)})`);
  }
  if (state.confirmRouterAction) lines.push(`${sanitizeText(state.confirmRouterAction)}? [y] confirm / [Esc] cancel`);
  else lines.push('[p] preview route  [a] activate  [d] direct  [b] rollback  [s] start/stop listener');
  if (state.activity?.length) lines.push(`Recent activity: ${state.activity.slice(0, 2).map((item) => `${sanitizeText(item.inbound_protocol)}:${sanitizeText(item.outcome)} ${sanitizeText(String(item.status ?? ''))}`).join(' · ')}`);
  lines.push('This local router supports bounded non-streaming text requests only.');
  lines.push('Authorization values and request/response content are never stored or shown.');
}

function renderIntegrations(state, lines) {
  lines.push('MCP and Skill integrations use verified local contracts.');
  for (const item of state.integrations || []) lines.push(`${pad(item.name, 20)} ${pad(item.contract_status, 12)} ${item.write_enabled ? 'writable' : 'inspection/export'}  ${sanitizeText(item.message)}`);
}

function renderMarketplace(state, lines) {
  lines.push(sanitizeText(state.marketplace?.message || 'Marketplace status is unavailable.'));
  lines.push(`Online: ${state.marketplace?.online_enabled ? 'enabled' : 'disabled'}  Cached items: ${sanitizeText(String(state.marketplace?.catalog_items || 0))}`);
  lines.push('Recommendations are deterministic: trust, declared risk, type, and name.');
  for (const item of (state.recommendations || []).slice(0, 8)) lines.push(`${pad(item.kind, 6)} ${pad(item.trust, 10)} ${pad(item.name, 24)} ${sanitizeText(item.version)}  risk:${sanitizeText(item.risk_level)}`);
  if (!(state.recommendations || []).length) lines.push('No trusted catalog items are cached. Online refresh requires explicit enablement.');
}

export function render(state, columns = 100, rows = 30) {
  const width = Math.max(40, columns);
  const contentWidth = width - 4;
  const title = screens[state.screen];
  const lines = [`ModelToolbox TUI  ·  ${title}`, '─'.repeat(contentWidth)];
  if (state.phase === 'loading') {
    lines.push('Loading local workbench…');
  } else if (state.phase !== 'ready') {
    lines.push(sanitizeText(state.message || 'The local workbench is unavailable.'));
    lines.push('Press r to retry.');
  } else if (title === 'Overview') {
    lines.push(`Connected to ModelToolbox ${sanitizeText(state.snapshot.version)}`);
    const entries = state.snapshot.state_entries || [];
    if (!entries.length) lines.push('No local state is available yet.');
    for (const entry of entries.slice(0, Math.max(1, rows - 8))) lines.push(`${pad(entry.key, 28)} ${sanitizeText(JSON.stringify(entry.value))}  [${sanitizeText(entry.value_type)}]`);
  } else if (title === 'Profiles') {
    renderProfiles(state, lines, rows);
  } else if (title === 'Router') {
    renderRouter(state, lines);
  } else if (title === 'Integrations' || title === 'Skills') {
    renderIntegrations(state, lines);
  } else if (title === 'Marketplace') {
    renderMarketplace(state, lines);
  } else {
    const section = state.snapshot.workbench?.sections?.find((item) => item.title === title.toLowerCase() || item.key === title.toLowerCase());
    lines.push(sanitizeText(section?.message || `${title} is not enabled yet.`));
    lines.push('This framework surface will use first-party ModelToolbox contracts when available.');
  }
  while (lines.length < Math.max(5, rows - 2)) lines.push('');
  lines.push('─'.repeat(contentWidth));
  lines.push(title === 'Profiles' ? '[1-7/Tab] screen  [j/k/arrows] choose [Enter] select [i] inspect [p] preview [a/y] apply [Esc] cancel [r] refresh [q] exit' : title === 'Router' ? '[1-7/Tab] screen  [p] preview [a/y] activate [d/y] direct [b/y] rollback [s/y] listener [Esc] cancel [r] refresh [q] exit' : '[1-7] screen  [r] refresh  [Tab] next screen  [q/Ctrl+C] exit');
  return lines.slice(0, rows).join('\n');
}

export function nextScreen(state) { return { ...state, screen: (state.screen + 1) % screens.length, message: null }; }
export function selectScreen(state, value) { const screen = Number(value) - 1; return screen >= 0 && screen < screens.length ? { ...state, screen, message: null } : state; }
export function moveProfile(state, delta) { const length = state.profiles.length; return length ? { ...state, profileIndex: (state.profileIndex + delta + length) % length, profileDetail: null, plan: null, confirmApply: false } : state; }
