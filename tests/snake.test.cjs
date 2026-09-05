// Run with: node tests/snake.test.cjs (Node.js built-ins only).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const html = fs.readFileSync(path.join(__dirname, '..', 'snake.html'), 'utf8');
const source = html.match(/<script id="game-engine">([\s\S]*?)<\/script>/)[1];
const sandbox = {module: {exports: {}}};
vm.runInNewContext(source, sandbox);
const {SnakeGame} = sandbox.module.exports;
let passed = 0;
function test(name, fn) { fn(); passed++; console.log('PASS ' + name); }
function rng(seed) {
  return () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
}
function playing(mode = 'manual', seed = 1) {
  const game = new SnakeGame(12, rng(seed));
  game.reset(mode); game.status = 'running'; return game;
}
function invariant(game) {
  assert.equal(new Set(game.snake.map(p => game.key(p))).size, game.snake.length, 'body overlaps');
  for (const p of game.snake) assert(p.x >= 0 && p.y >= 0 && p.x < game.size && p.y < game.size, 'outside board');
  if (game.food) assert(!game.snake.some(p => game.key(p) === game.key(game.food)), 'food on snake');
  assert.equal(game.snake.length, 4 + game.eaten);
}
test('cycle covers all cells once, every step and closure are adjacent', () => {
  for (const size of [4, 6, 12, 16]) {
    const g = new SnakeGame(size);
    assert.equal(g.cycle.length, size * size);
    assert.equal(new Set(g.cycle.map(p => g.key(p))).size, size * size);
    g.cycle.forEach((p, i) => {
      const q = g.cycle[(i + 1) % g.cycle.length];
      assert.equal(Math.abs(p.x - q.x) + Math.abs(p.y - q.y), 1);
    });
  }
});
test('ordinary movement advances head and removes tail', () => {
  const g = playing(); const x = g.snake[0].x, y = g.snake[0].y;
  g.food = {x: 11, y: 11}; g.tick();
  assert.equal(g.snake[0].x, x + 1); assert.equal(g.snake[0].y, y);
  assert.equal(g.snake.length, 4); assert.equal(g.eaten, 0); assert.equal(g.steps, 1);
});
test('eating grows exactly one cell and replaces food on an empty cell', () => {
  const g = playing(); g.food = {x: g.snake[0].x + 1, y: g.snake[0].y}; g.tick();
  assert.equal(g.snake.length, 5); assert.equal(g.eaten, 1); invariant(g);
});
test('reverse turns and a second turn before a tick are ignored', () => {
  const g = playing();
  assert.equal(g.turn(-1, 0), false);
  assert.equal(g.turn(0, 1), true);
  assert.equal(g.turn(-1, 0), false);
  g.tick(); assert.equal(g.direction.y, 1);
  assert.equal(g.turn(-1, 0), true);
});
test('wall collision ends the game and prevents further movement', () => {
  const g = playing(); g.food = {x: 0, y: 11};
  for (let i = 0; i < 20; i++) g.tick();
  assert.equal(g.status, 'lost'); assert.equal(g.reason, '撞到墙壁了');
  const steps = g.steps; g.tick(); assert.equal(g.steps, steps);
});
test('body collision is detected', () => {
  const g = playing();
  g.snake = [{x:2,y:2},{x:2,y:3},{x:3,y:3},{x:3,y:2},{x:4,y:2},{x:4,y:3}];
  g.direction = {x:1,y:0}; g.food = {x:0,y:0}; g.tick();
  assert.equal(g.status, 'lost'); assert.equal(g.reason, '撞到自己的身体了');
});
test('moving into the departing tail is legal', () => {
  const g = playing();
  g.snake = [{x:2,y:2},{x:2,y:3},{x:3,y:3},{x:3,y:2}];
  g.direction = {x:1,y:0}; g.food = {x:0,y:0}; g.tick();
  assert.equal(g.status, 'running'); invariant(g);
});
test('paused and ready states do not advance', () => {
  const g = playing();
  for (const status of ['ready', 'paused']) { g.status = status; g.tick(); assert.equal(g.steps, 0); }
});
test('restart clears score, pending input, body length and mode', () => {
  const g = playing(); g.food = {x:g.snake[0].x+1,y:g.snake[0].y}; g.tick(); g.turn(0,1);
  g.reset('ai'); assert.equal(g.mode, 'ai'); assert.equal(g.eaten, 0); assert.equal(g.steps, 0);
  assert.equal(g.snake.length, 4); assert.equal(g.pending, null); assert.equal(g.status, 'ready');
});
let min = Infinity, max = 0;
test('AI eats 15 foods without collision for 200 independent seeded layouts', () => {
  for (let seed = 1; seed <= 200; seed++) {
    const g = playing('ai', seed);
    while (g.eaten < 15 && g.status === 'running' && g.steps < 2160) { g.tick(); invariant(g); }
    assert(g.eaten >= 15, 'seed ' + seed + ' did not reach 15');
    assert.equal(g.status, 'running'); min = Math.min(min, g.steps); max = Math.max(max, g.steps);
  }
});
test('AI fills the board and wins for 5 independent seeded layouts', () => {
  for (let seed = 1; seed <= 5; seed++) {
    const g = playing('ai', seed);
    while (g.status === 'running' && g.steps < 20160) { g.tick(); invariant(g); }
    assert.equal(g.status, 'won'); assert.equal(g.eaten, 140);
    assert.equal(g.snake.length, 144); assert.equal(g.food, null);
  }
});
console.log(JSON.stringify({testGroups: passed, aiSeeds: 200, foodTarget: 15, minSteps: min, maxSteps: max, fullBoardWins: 5}));
