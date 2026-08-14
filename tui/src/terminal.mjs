import process from 'node:process';

export class Terminal {
  constructor({ input = process.stdin, output = process.stdout } = {}) {
    this.input = input;
    this.output = output;
    this.active = false;
  }

  get isInteractive() {
    return Boolean(this.input.isTTY && this.output.isTTY);
  }

  enter() {
    if (!this.isInteractive || this.active) return;
    this.active = true;
    this.output.write('[?1049h[?25l[2J[H');
    this.input.setRawMode?.(true);
    this.input.resume();
  }

  draw(frame) {
    if (!this.active) return;
    this.output.write(`[H[2J${frame}`);
  }

  restore() {
    if (!this.active) return;
    this.active = false;
    this.input.setRawMode?.(false);
    this.output.write('[?25h[?1049l');
  }
}
