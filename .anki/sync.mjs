// Adds an AnkiWeb card for every NeetCode problem that appears in a push.
// Usage (repo root): node .anki/sync.mjs [--dry-run]
// Env: BEFORE, AFTER (push shas), SLUGS (comma list, overrides the diff),
//      ANKIWEB_EMAIL, ANKIWEB_PASSWORD.
import { execFileSync } from 'node:child_process';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const ROOT = 'Data Structures & Algorithms';
const DECK = 'NeetCode';
const MAX_NEW = 15;

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
    for (const s of slugs) console.log(`${s}: ${table.has(s) ? 'card text in cards.json' : 'MISSING from cards.json'}`);
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
    for (const slug of slugs) {
      try {
        if (await existsInAnki(page, slug)) {
          skipped.push(slug);
          console.log(`${slug}: already in Anki, skipped`);
          continue;
        }
        const card = table.get(slug);
        if (!card) throw new Error('no card text in .anki/cards.json for this problem, add an entry and re-run');
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
