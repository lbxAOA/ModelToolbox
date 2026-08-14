import process from 'node:process';

import { BridgeClient } from './bridge_client.mjs';
import { createState, nextScreen, render, selectScreen } from './render.mjs';
import { Terminal } from './terminal.mjs';

export async function run({ executable = process.env.MODELTOOLBOX_PYTHON, root = process.env.MODELTOOLBOX_ROOT, terminal = new Terminal() } = {}) {
  if (!terminal.isInteractive) {
    process.stderr.write('ModelToolbox TUI requires an interactive terminal.\n');
    return 1;
  }
  if (!executable || !root) {
    process.stderr.write('Set MODELTOOLBOX_PYTHON and MODELTOOLBOX_ROOT before starting the TUI.\n');
    return 1;
  }

  const client = new BridgeClient({ executable, arguments: ['cli/main.py', 'bridge', '--protocol', 'mtb.bridge/1'], cwd: root });
  let state = createState();
  let closed = false;

  const cleanup = async () => {
    if (closed) return;
    closed = true;
    terminal.restore();
    await client.close();
  };
  const redraw = () => terminal.draw(render(state, terminal.output.columns, terminal.output.rows));
  const refresh = async (initial = false) => {
    state = { ...state, phase: 'loading', message: null };
    redraw();
    try {
      const snapshot = await client.request(initial ? 'view.snapshot' : 'view.refresh');
      state = { ...state, phase: 'ready', snapshot };
    } catch (error) {
      state = { ...state, phase: 'error', message: error.message };
    }
    redraw();
  };

  terminal.enter();
  process.once('SIGINT', () => cleanup().then(() => process.exit(0)));
  process.once('SIGTERM', () => cleanup().then(() => process.exit(0)));
  process.once('uncaughtException', () => cleanup().then(() => process.exit(1)));
  terminal.input.on('data', async (chunk) => {
    const key = chunk.toString('utf8');
    if (key === '' || key === 'q') {
      await cleanup();
      process.exit(0);
    }
    if (key === '\t') state = nextScreen(state);
    if (/^[1-5]$/.test(key)) state = selectScreen(state, key);
    if (key === 'r') await refresh(false);
    redraw();
  });
  terminal.output.on('resize', redraw);
  await refresh(true);
  return 0;
}
