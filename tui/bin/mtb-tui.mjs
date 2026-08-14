#!/usr/bin/env node

import { run } from '../src/app.mjs';

process.exitCode = await run();
