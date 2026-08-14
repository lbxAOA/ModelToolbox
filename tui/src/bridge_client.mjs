import { spawn } from 'node:child_process';
import { createInterface } from 'node:readline';

import { decodeResponse, encodeRequest } from './protocol.mjs';

export class BridgeClient {
  constructor({ executable, arguments: argumentsList, cwd, timeoutMs = 5000 }) {
    this.executable = executable;
    this.arguments = argumentsList;
    this.cwd = cwd;
    this.timeoutMs = timeoutMs;
    this.child = null;
    this.lines = null;
    this.pending = Promise.resolve();
    this.sequence = 0;
  }

  async request(operation, payload = {}) {
    const run = this.pending.then(() => this.#requestOnce(operation, payload));
    this.pending = run.catch(() => undefined);
    return run;
  }

  async close() {
    const child = this.child;
    this.child = null;
    this.lines?.close();
    this.lines = null;
    if (!child) return;
    child.stdin.end();
    child.kill();
  }

  async #start() {
    if (this.child) return;
    try {
      const child = spawn(this.executable, this.arguments, { cwd: this.cwd, shell: false, stdio: ['pipe', 'pipe', 'ignore'] });
      const lines = createInterface({ input: child.stdout, crlfDelay: Infinity });
      child.once('error', () => this.#reset());
      child.once('exit', () => this.#reset());
      this.child = child;
      this.lines = lines;
    } catch {
      throw new Error('The local ModelToolbox runtime could not be started.');
    }
  }

  async #requestOnce(operation, payload) {
    await this.#start();
    if (!this.child || !this.lines) throw new Error('The local bridge is unavailable.');
    const requestId = `tui-${++this.sequence}`;
    this.child.stdin.write(`${encodeRequest(requestId, operation, payload)}\n`);
    const line = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('The local bridge did not respond in time.')), this.timeoutMs);
      const onLine = (value) => {
        clearTimeout(timer);
        this.lines.off('line', onLine);
        resolve(value);
      };
      this.lines.once('line', onLine);
    });
    try {
      return decodeResponse(line, requestId);
    } catch (error) {
      await this.#reset();
      throw error;
    }
  }

  async #reset() {
    const child = this.child;
    this.child = null;
    this.lines?.close();
    this.lines = null;
    child?.kill();
  }
}
