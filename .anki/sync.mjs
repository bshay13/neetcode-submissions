// Adds an AnkiWeb card for every NeetCode problem that appears in a push.
// Usage (repo root): node .anki/sync.mjs [--dry-run]
// Env: BEFORE, AFTER (push shas), SLUGS (comma list, overrides the diff),
//      ANKIWEB_EMAIL, ANKIWEB_PASSWORD, ANTHROPIC_API_KEY (only for problems missing from cards.json).
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const ROOT = 'Data Structures & Algorithms';
const DECK = 'NeetCode';
const MAX_NEW = 15;
const CATEGORIES = [
  'Arrays & Hashing', 'Two Pointers', 'Sliding Window', 'Binary Search', 'Linked List', 'Stack',
  'Trees', 'Tries', 'Backtracking', 'Heap / Priority Queue', 'Graphs', 'Advanced Graphs',
  '1-D Dynamic Programming', '2-D Dynamic Programming', 'Greedy', 'Intervals', 'Bit Manipulation',
  'Math & Geometry',
];

const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const plain = (s) => String(s).replace(/[–—]/g, '-').trim();
export const problemUrl = (slug) => `https://neetcode.io/problems/${slug}/question`;

export function cardHtml(card) {
  const url = problemUrl(card.slug);
  return {
    front: `${esc(card.name)}<br><a href="${url}">${url}</a>`,
    back:
      `<b>Time:</b> ${esc(card.time)}<br><b>Space:</b> ${esc(card.space)}<br>` +
      `<b>Category:</b> ${esc(card.category)}<br><b>Trick:</b> ${esc(card.trick)}`,
  };
}

// Problem slugs whose submission files were ADDED in the given commit range.
export function detectSlugs({ before, after, cwd = process.cwd() }) {
  const git = (args) => execFileSync('git', args, { cwd, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
  const hasBefore = before && !/^0+$/.test(before);
  let out;
  try {
    out = hasBefore
      ? git(['diff', '--name-only', '-z', '--diff-filter=A', before, after])
      : git(['show', '--name-only', '-z', '--diff-filter=A', '--format=', after]);
  } catch {
    out = git(['show', '--name-only', '-z', '--diff-filter=A', '--format=', after]);
  }
  const re = new RegExp(`^${ROOT}/([^/]+)/submission-\\d+\\.[^/]+$`);
  const slugs = new Set();
  for (const path of out.split('\0')) {
    const m = re.exec(path);
    if (m) slugs.add(m[1]);
  }
  return [...slugs];
}

export function parseGenerated(text, slug) {
  const m = text.match(/\{[\s\S]*\}/);
  if (!m) throw new Error(`no JSON in model reply for "${slug}"`);
  const obj = JSON.parse(m[0]);
  if (obj.error) throw new Error(`model could not identify "${slug}": ${obj.error}`);
  const card = { slug };
  for (const k of ['name', 'category', 'time', 'space', 'trick']) {
    if (typeof obj[k] !== 'string' || !obj[k].trim()) throw new Error(`model reply for "${slug}" is missing "${k}"`);
    card[k] = plain(obj[k]);
  }
  return card;
}

export async function generate(slug, examples) {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error(`no card text for "${slug}" and ANTHROPIC_API_KEY is not set`);
  const prompt =
    `You write Anki flashcard text for a NeetCode problem. The problem's URL slug is "${slug}" ` +
    `(${problemUrl(slug)}). A slug can differ from the title, for example duplicate-integer is "Contains Duplicate".\n` +
    `Reply with ONLY a JSON object with these string fields: name (the NeetCode problem title), ` +
    `category (one of: ${CATEGORIES.join(' | ')} | Other), time and space (big-O of the OPTIMAL solution, ` +
    `short), trick (one or two sentences naming the key insight, with the main alternative's complexity in ` +
    `parentheses when useful). Optimal solution only. Use plain hyphens, never em dashes. ` +
    `If you do not recognize the problem, reply {"error":"unknown problem"}.\n` +
    `Style examples:\n${examples.map((e) => JSON.stringify(e)).join('\n')}`;
  const res = await fetch(process.env.ANTHROPIC_API_URL || 'https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: { 'x-api-key': key, 'anthropic-version': '2023-06-01', 'content-type': 'application/json' },
    body: JSON.stringify({
      model: process.env.ANKI_MODEL || 'claude-sonnet-5-5',
      max_tokens: 1000,
      messages: [{ role: 'user', content: prompt }],
    }),
  });
  if (!res.ok) throw new Error(`Anthropic API returned HTTP ${res.status} for "${slug}"`);
  const data = await res.json();
  const text = (data.content || []).filter((b) => b.type === 'text').map((b) => b.text).join('');
  return parseGenerated(text, slug);
}

async function login(page) {
  const { ANKIWEB_EMAIL, ANKIWEB_PASSWORD } = process.env;
  if (!ANKIWEB_EMAIL || !ANKIWEB_PASSWORD) throw new Error('ANKIWEB_EMAIL and ANKIWEB_PASSWORD secrets are not set');
  await page.goto('https://ankiweb.net/account/login', { waitUntil: 'domcontentloaded' });
  await page.getByRole('textbox').first().fill(ANKIWEB_EMAIL);
  await page.locator('input[type="password"]').fill(ANKIWEB_PASSWORD);
  await page.getByRole('button', { name: 'Log In' }).click();
  try {
    await page.waitForURL((u) => !u.pathname.includes('/account/login'), { timeout: 30000 });
  } catch {
    throw new Error('AnkiWeb login failed: check the secrets, or AnkiWeb may be blocking this runner');
  }
}

async function existsInAnki(page, slug) {
  await page.goto('https://ankiweb.net/search', { waitUntil: 'domcontentloaded' });
  const box = page.getByRole('textbox').first();
  await box.waitFor({ timeout: 30000 });
  await box.fill(`deck:${DECK} "neetcode.io/problems/${slug}/question"`);
  await Promise.all([
    page.waitForResponse((r) => r.url().includes('/svc/search/search'), { timeout: 30000 }),
    page.getByRole('button', { name: 'Search', exact: true }).click(),
  ]);
  await page.waitForTimeout(500);
  const hit = page.locator('table tr').filter({ hasText: `neetcode.io/problems/${slug}/question` });
  return (await hit.count()) > 0;
}

async function addCard(page, card) {
  const { front, back } = cardHtml(card);
  await page.goto('https://ankiweb.net/add', { waitUntil: 'domcontentloaded' });
  await page.locator('[contenteditable]').nth(1).waitFor({ timeout: 30000 });
  // The Basic note type has exactly the fields Front and Back. Anything else means the wrong note type.
  await page.getByText('Front', { exact: true }).waitFor({ timeout: 5000 });
  await page.getByText('Back', { exact: true }).waitFor({ timeout: 5000 });
  await page.evaluate(({ front, back }) => {
    const [f, b] = [...document.querySelectorAll('[contenteditable]')];
    const fill = (el, html) => {
      el.focus();
      document.execCommand('selectAll');
      document.execCommand('insertHTML', false, html);
    };
    fill(f, front);
    fill(b, back);
  }, { front, back });
  await page.getByRole('button', { name: 'Add', exact: true }).click();
  // After a successful add AnkiWeb clears the Front field.
  await page.waitForFunction(
    () => !(document.querySelector('[contenteditable]')?.innerText || '').trim(),
    null,
    { timeout: 20000 },
  );
}

async function main() {
  const dryRun = process.argv.includes('--dry-run');
  const table = new Map(
    JSON.parse(readFileSync(new URL('./cards.json', import.meta.url), 'utf8')).cards.map((c) => [c.slug, c]),
  );
  const slugs = process.env.SLUGS
    ? process.env.SLUGS.split(',').map((s) => s.trim()).filter(Boolean)
    : detectSlugs({ before: process.env.BEFORE || 'HEAD~1', after: process.env.AFTER || 'HEAD' });

  console.log(`Problems in this push: ${slugs.length ? slugs.join(', ') : '(none)'}`);
  if (!slugs.length) return 0;
  if (slugs.length > MAX_NEW) {
    console.error(`Refusing to sync ${slugs.length} problems at once (limit ${MAX_NEW}). Use the manual run with SLUGS.`);
    return 1;
  }
  if (dryRun) {
    for (const s of slugs) console.log(`${s}: ${table.has(s) ? 'card text in cards.json' : 'would generate card text'}`);
    return 0;
  }

  const { chromium } = await import('playwright');
  const browser = await chromium.launch();
  const failed = [];
  const added = [];
  const skipped = [];
  try {
    const page = await (await browser.newContext()).newPage();
    page.setDefaultTimeout(30000);
    await login(page);
    const examples = [...table.values()].slice(0, 3);
    for (const slug of slugs) {
      try {
        if (await existsInAnki(page, slug)) {
          skipped.push(slug);
          console.log(`${slug}: already in Anki, skipped`);
          continue;
        }
        const card = table.get(slug) ?? (await generate(slug, examples));
        await addCard(page, card);
        let confirmed = false;
        for (let i = 0; i < 3 && !confirmed; i++) {
          confirmed = await existsInAnki(page, slug);
          if (!confirmed) await page.waitForTimeout(2000);
        }
        if (!confirmed) throw new Error('card was submitted but a search did not find it');
        added.push(slug);
        console.log(`${slug}: added (${card.name})`);
      } catch (err) {
        failed.push(slug);
        console.error(`${slug}: FAILED - ${err.message}`);
      }
    }
  } finally {
    await browser.close();
  }
  console.log(`Done. added=${added.length} skipped=${skipped.length} failed=${failed.length}`);
  return failed.length ? 1 : 0;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().then(
    (code) => process.exit(code),
    (err) => {
      console.error(`FAILED - ${err.message}`);
      process.exit(1);
    },
  );
}
