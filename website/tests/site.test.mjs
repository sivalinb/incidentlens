import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

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

class FakeClassList {
  constructor(...values) { this.values = new Set(values); }
  add(value) { this.values.add(value); }
  remove(value) { this.values.delete(value); }
  contains(value) { return this.values.has(value); }
}

class FakeElement {
  constructor(id, {value = '', classes = [], tab = undefined} = {}) {
    this.id = id;
    this.value = value;
    this.dataset = tab ? {tab} : {};
    this.classList = new FakeClassList(...classes);
    this.listeners = {};
    this.textContent = '';
    this.innerHTML = '';
  }
  addEventListener(type, callback) { this.listeners[type] = callback; }
  dispatch(type) { this.listeners[type]({target: this}); }
}

function loadInteractiveSite() {
  const ids = [
    'scenario', 'metric-title', 'metric-value', 'metric-summary', 'chart', 'log-lines',
    'trace-path', 'trace-summary', 'cause', 'confidence', 'rationale', 'counter',
    'recommendation', 'verification', 'decision-status', 'approve',
  ];
  const elements = new Map(ids.map(id => [id, new FakeElement(id)]));
  elements.get('scenario').value = 'payment';
  const panels = ['telemetry', 'analysis', 'agents', 'approval'].map(
    (id, index) => new FakeElement(id, {classes: index === 0 ? ['panel', 'active'] : ['panel']})
  );
  for (const panel of panels) elements.set(panel.id, panel);
  const tabs = panels.map((panel, index) => new FakeElement(`tab-${panel.id}`, {
    classes: index === 0 ? ['tab', 'active'] : ['tab'],
    tab: panel.id,
  }));
  const document = {
    getElementById: id => elements.get(id),
    querySelectorAll: selector => selector === '.tab' ? tabs : [...tabs, ...panels],
  };
  vm.runInNewContext(js, {document, Math});
  return {elements, panels, tabs};
}

test('interactive flow renders scenarios, tabs, and safe approval state', () => {
  const {elements, panels, tabs} = loadInteractiveSite();
  assert.equal(elements.get('metric-value').textContent, '28.2%');
  assert.equal(elements.get('cause').textContent, 'Invalid payment-service address');

  elements.get('scenario').value = 'email';
  elements.get('scenario').dispatch('change');
  assert.equal(elements.get('metric-value').textContent, '536 MiB');
  assert.equal(elements.get('cause').textContent, 'Email process retains allocations');

  tabs[3].dispatch('click');
  assert.equal(tabs[3].classList.contains('active'), true);
  assert.equal(panels[3].classList.contains('active'), true);
  assert.equal(panels[0].classList.contains('active'), false);

  elements.get('approve').dispatch('click');
  assert.equal(
    elements.get('decision-status').textContent,
    'State: approved_pending_verification - no production write',
  );
});
