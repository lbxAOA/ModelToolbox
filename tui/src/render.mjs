import { sanitizeText } from './protocol.mjs';

const screens = ['Overview', 'Session', 'Workspace', 'Tools', 'Settings'];

export function createState() {
  return {
    phase: 'loading',
    screen: 0,
    snapshot: null,
    message: null,
  };
}

function pad(value, width) {
  return sanitizeText(value).slice(0, width).padEnd(width);
}

export function render(state, columns = 100, rows = 30) {
  const width = Math.max(40, columns);
  const contentWidth = width - 4;
  const title = screens[state.screen];
  const lines = [
    `ModelToolbox TUI  ·  ${title}`,
    '─'.repeat(contentWidth),
  ];

  if (state.phase === 'loading') {
    lines.push('Loading local workbench…');
  } else if (state.phase !== 'ready') {
    lines.push(sanitizeText(state.message || 'The local workbench is unavailable.'));
    lines.push('Press r to retry.');
  } else if (title === 'Overview') {
    lines.push(`Connected to ModelToolbox ${sanitizeText(state.snapshot.version)}`);
    const entries = state.snapshot.state_entries || [];
    if (!entries.length) lines.push('No local state is available yet.');
    for (const entry of entries.slice(0, Math.max(1, rows - 8))) {
      lines.push(`${pad(entry.key, 28)} ${sanitizeText(JSON.stringify(entry.value))}  [${sanitizeText(entry.value_type)}]`);
    }
  } else {
    const section = state.snapshot.workbench?.sections?.find((item) => item.title === title.toLowerCase() || item.key === title.toLowerCase());
    lines.push(sanitizeText(section?.message || `${title} is not enabled yet.`));
    lines.push('This framework surface will use first-party ModelToolbox contracts when available.');
  }

  while (lines.length < Math.max(5, rows - 2)) lines.push('');
  lines.push('─'.repeat(contentWidth));
  lines.push('[1-5] screen  [r] refresh  [Tab] next screen  [q/Ctrl+C] exit');
  return lines.slice(0, rows).join('\n');
}

export function nextScreen(state) {
  return { ...state, screen: (state.screen + 1) % screens.length };
}

export function selectScreen(state, value) {
  const screen = Number(value) - 1;
  return screen >= 0 && screen < screens.length ? { ...state, screen } : state;
}
