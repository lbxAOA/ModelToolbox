import process from 'node:process';

import { BridgeClient } from './bridge_client.mjs';
import { createState, moveProfile, nextScreen, render, selectScreen } from './render.mjs';
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
  const cleanup = async () => { if (!closed) { closed = true; terminal.restore(); await client.close(); } };
  const redraw = () => terminal.draw(render(state, terminal.output.columns, terminal.output.rows));
  const refresh = async (initial = false) => {
    state = { ...state, phase: 'loading', message: null };
    redraw();
    try {
      const [snapshot, profiles, adapters, router, listener, activity, integrations, marketplace, recommendations] = await Promise.all([client.request(initial ? 'view.snapshot' : 'view.refresh'), client.request('profiles.list'), client.request('profiles.adapters'), client.request('router.status'), client.request('router.listener-status'), client.request('router.activity'), client.request('integrations.list'), client.request('marketplace.status'), client.request('marketplace.recommendations')]);
      state = { ...state, phase: 'ready', snapshot, profiles: profiles.profiles || [], adapters: adapters.adapters || [], router, listener, activity: activity.events || [], integrations: integrations.adapters || [], marketplace, recommendations: recommendations.items || [], profileIndex: 0, profileDetail: null, plan: null, routerPlan: null, confirmApply: false, confirmRouterAction: null };
    } catch (error) { state = { ...state, phase: 'error', message: error.message }; }
    redraw();
  };
  const requestForProfile = async (operation) => {
    const profile = state.profiles[state.profileIndex];
    if (!profile) return;
    try {
      const data = await client.request(operation, { profile_id: profile.id });
      state = operation === 'profiles.inspect' ? { ...state, profileDetail: data, plan: null } : { ...state, plan: data, profileDetail: null, confirmApply: false };
    } catch (error) { state = { ...state, message: error.message }; }
  };
  const selectProfile = async () => {
    const profile = state.profiles[state.profileIndex];
    if (!profile) return;
    try {
      await client.request('profiles.select', { profile_id: profile.id });
      state = { ...state, profiles: state.profiles.map((item) => ({ ...item, selected: item.id === profile.id })), message: `Selected ${profile.name}. No external configuration changed.` };
    } catch (error) { state = { ...state, message: error.message }; }
  };
  const apply = async () => {
    const profile = state.profiles[state.profileIndex];
    if (!profile || !state.plan?.revision) return;
    try {
      await client.request('profiles.apply', { profile_id: profile.id, revision: state.plan.revision });
      state = { ...state, message: `Applied ${profile.name}.`, confirmApply: false, plan: null };
    } catch (error) { state = { ...state, message: error.message, confirmApply: false }; }
  };
  const requestRouterPlan = async () => {
    const profile = state.profiles[state.profileIndex];
    if (!profile) return;
    try {
      const routerPlan = await client.request('router.plan-activate', { profile_id: profile.id, inbound_protocol: 'anthropic', upstream_protocol: 'openai' });
      state = { ...state, routerPlan, confirmRouterAction: null, message: null };
    } catch (error) { state = { ...state, message: error.message }; }
  };
  const applyRouterAction = async () => {
    const action = state.confirmRouterAction;
    if (!action || !state.router) return;
    try {
      if (action === 'activate') {
        const profile = state.profiles[state.profileIndex];
        if (!profile || !state.routerPlan) return;
        await client.request('router.activate', { profile_id: profile.id, inbound_protocol: 'anthropic', upstream_protocol: 'openai', expected_revision: state.routerPlan.revision });
      } else if (action === 'direct') {
        await client.request('router.direct', { expected_revision: state.router.revision });
      } else if (action === 'rollback') {
        await client.request('router.rollback', { expected_revision: state.router.revision });
      } else if (action === 'listener-start') {
        await client.request('router.listener-start', { host: '127.0.0.1', port: 15721 });
      } else if (action === 'listener-stop') {
        await client.request('router.listener-stop');
      }
      await refresh(false);
    } catch (error) { state = { ...state, message: error.message, confirmRouterAction: null }; }
  };
  terminal.enter();
  process.once('SIGINT', () => cleanup().then(() => process.exit(0)));
  process.once('SIGTERM', () => cleanup().then(() => process.exit(0)));
  process.once('uncaughtException', () => cleanup().then(() => process.exit(1)));
  terminal.input.on('data', async (chunk) => {
    const key = chunk.toString('utf8');
    if (key === '' || key === 'q') { await cleanup(); process.exit(0); }
    if (key === 'r') await refresh(false);
    if (key === '\t') state = nextScreen(state);
    if (/^[1-7]$/.test(key)) state = selectScreen(state, key);
    if (state.screen === 5 && state.phase === 'ready') {
      if (key === 'p') await requestRouterPlan();
      if (key === 'a' && state.routerPlan?.ready) state = { ...state, confirmRouterAction: 'activate' };
      if (key === 'd') state = { ...state, confirmRouterAction: 'direct' };
      if (key === 'b' && state.router?.previous) state = { ...state, confirmRouterAction: 'rollback' };
      if (key === 's') state = { ...state, confirmRouterAction: state.listener?.running ? 'listener-stop' : 'listener-start' };
      if (key === 'y' && state.confirmRouterAction) await applyRouterAction();
      if (key === '') state = { ...state, confirmRouterAction: null };
    }
    redraw();
  });
  terminal.output.on('resize', redraw);
  await refresh(true);
  return 0;
}
