import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const js = readFileSync(new URL('../app.js', import.meta.url), 'utf8');
const css = readFileSync(new URL('../styles.css', import.meta.url), 'utf8');

test('site explicitly labels replay and simulation modes', () => {
  assert.match(html, /Deterministic replay/);
  assert.match(html, /Simulation only/);
  assert.match(html, /does not claim fresh production telemetry/);
});

test('site presents the four-stage product flow', () => {
  for (const label of ['Telemetry', 'Analysis', 'Agent flow', 'Human gate']) {
    assert.match(html, new RegExp(label));
  }
});

test('site includes all three scenarios with accurate units', () => {
  assert.match(js, /28\.2%/);
  assert.match(js, /536 MiB/);
  assert.match(js, /12,480 messages/);
});

test('approval copy never claims incident closure', () => {
  assert.match(js, /approved_pending_verification/);
  assert.match(js, /no production write/);
  assert.doesNotMatch(js, /incident closed/i);
});

test('responsive layout includes mobile breakpoint', () => {
  assert.match(css, /@media\(max-width:540px\)/);
});

