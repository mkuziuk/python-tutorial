import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { posix, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)));
const DIST = resolve(ROOT, 'dist');

function walk(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = resolve(directory, entry.name);
    return entry.isDirectory() ? walk(path) : [path];
  });
}

function decodeHtml(value) {
  return value
    .replace(/&#x([0-9a-f]+);/gi, (_, number) =>
      String.fromCodePoint(Number.parseInt(number, 16)),
    )
    .replace(/&#([0-9]+);/g, (_, number) =>
      String.fromCodePoint(Number.parseInt(number, 10)),
    )
    .replace(/&(amp|quot|apos|lt|gt);/g, (_, entity) => {
      const entities = { amp: '&', quot: '"', apos: "'", lt: '<', gt: '>' };
      return entities[entity];
    });
}

function attributes(tag) {
  const result = new Map();
  const pattern = /([^\s=/>]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'=<>`]+)))?/g;
  for (const match of tag.matchAll(pattern)) {
    result.set(
      match[1].toLowerCase(),
      decodeHtml(match[2] ?? match[3] ?? match[4] ?? ''),
    );
  }
  return result;
}

function canonicalUrl(html) {
  for (const match of html.matchAll(/<link\b[^>]*>/gi)) {
    const attrs = attributes(match[0]);
    const relations = (attrs.get('rel') ?? '').toLowerCase().split(/\s+/);
    if (relations.includes('canonical') && attrs.has('href')) {
      return new URL(attrs.get('href'));
    }
  }
  return undefined;
}

function outputRoute(relativePath) {
  if (relativePath === 'index.html') return '/';
  if (relativePath.endsWith('/index.html')) {
    return `/${relativePath.slice(0, -'index.html'.length)}`;
  }
  return `/${relativePath}`;
}

function anchorTargets(html) {
  const targets = new Set();
  for (const match of html.matchAll(/<[^>]+>/g)) {
    const attrs = attributes(match[0]);
    if (attrs.has('id')) targets.add(attrs.get('id'));
    if (/^<a\b/i.test(match[0]) && attrs.has('name')) {
      targets.add(attrs.get('name'));
    }
  }
  return targets;
}

function anchorLinks(html) {
  const links = [];
  for (const match of html.matchAll(/<a\b[^>]*>/gi)) {
    const attrs = attributes(match[0]);
    if (attrs.has('href')) links.push(attrs.get('href'));
  }
  return links;
}

function decodeUrlPath(pathname) {
  try {
    const decoded = pathname
      .split('/')
      .map((segment) => decodeURIComponent(segment))
      .join('/');
    return decoded.includes('\\') ? undefined : decoded;
  } catch {
    return undefined;
  }
}

function decodeFragment(hash) {
  try {
    return decodeURIComponent(hash.slice(1));
  } catch {
    return undefined;
  }
}

if (!existsSync(DIST)) {
  console.error('Generated site not found. Run `pnpm build` before `pnpm test:links`.');
  process.exit(1);
}

const files = walk(DIST);
const relativeFiles = new Set(
  files.map((file) => relative(DIST, file).split('\\').join('/')),
);
const pages = files
  .filter((file) => file.endsWith('.html'))
  .map((file) => {
    const relativePath = relative(DIST, file).split('\\').join('/');
    const html = readFileSync(file, 'utf8');
    return {
      anchors: anchorTargets(html),
      canonical: canonicalUrl(html),
      html,
      relativePath,
      route: outputRoute(relativePath),
    };
  });

if (pages.length === 0) {
  console.error('No generated HTML pages found in dist/.');
  process.exit(1);
}

const referencePage = pages.find(
  (page) =>
    page.canonical &&
    page.route !== '/' &&
    page.canonical.pathname.endsWith(page.route),
);
const rootPage = pages.find((page) => page.route === '/' && page.canonical);
const origin = (
  referencePage?.canonical ??
  rootPage?.canonical ??
  new URL('https://example.invalid')
).origin;
let basePath = '';

if (referencePage) {
  basePath = referencePage.canonical.pathname.slice(0, -referencePage.route.length);
} else if (rootPage) {
  basePath = rootPage.canonical.pathname.replace(/\/$/, '');
}

basePath = basePath === '/' ? '' : basePath.replace(/\/$/, '');

const pagesByFile = new Map(pages.map((page) => [page.relativePath, page]));
const filesByCanonicalPath = new Map(
  pages
    .filter((page) => page.canonical?.origin === origin)
    .map((page) => [page.canonical.pathname, page.relativePath]),
);
const problems = [];
let checkedLinks = 0;

function publicUrl(route) {
  return new URL(`${basePath}${route}`, `${origin}/`);
}

function relativeTarget(pathname) {
  if (basePath) {
    if (pathname === basePath || pathname === `${basePath}/`) return '';
    if (!pathname.startsWith(`${basePath}/`)) return undefined;
    pathname = pathname.slice(basePath.length);
  }
  return decodeUrlPath(pathname.replace(/^\//, ''));
}

function targetFile(pathname) {
  if (filesByCanonicalPath.has(pathname)) {
    return filesByCanonicalPath.get(pathname);
  }

  const relativePath = relativeTarget(pathname);
  if (relativePath === undefined) return undefined;

  const cleanPath = posix.normalize(relativePath || '.').replace(/^\.\/$/, '');
  if (cleanPath === '..' || cleanPath.startsWith('../')) return undefined;

  const candidates = pathname.endsWith('/')
    ? [posix.join(cleanPath, 'index.html')]
    : [cleanPath, `${cleanPath}.html`, posix.join(cleanPath, 'index.html')];
  return candidates.find((candidate) => relativeFiles.has(candidate));
}

for (const page of pages) {
  const sourceUrl = page.canonical ?? publicUrl(page.route);
  for (const href of anchorLinks(page.html)) {
    if (!href.trim()) continue;

    let target;
    try {
      target = new URL(href, sourceUrl);
    } catch {
      problems.push(`${page.relativePath}: invalid URL ${JSON.stringify(href)}`);
      continue;
    }

    if (!['http:', 'https:'].includes(target.protocol) || target.origin !== origin) {
      continue;
    }

    checkedLinks += 1;
    const file = targetFile(target.pathname);
    if (!file) {
      const detail =
        basePath && !target.pathname.startsWith(`${basePath}/`)
          ? `escapes site base ${basePath}/`
          : 'target does not exist';
      problems.push(`${page.relativePath}: ${JSON.stringify(href)} (${detail})`);
      continue;
    }

    if (!target.hash || !file.endsWith('.html')) continue;
    const fragment = decodeFragment(target.hash);
    const targetPage = pagesByFile.get(file);
    if (fragment === undefined || !targetPage?.anchors.has(fragment)) {
      problems.push(
        `${page.relativePath}: ${JSON.stringify(href)} (fragment not found in ${file})`,
      );
    }
  }
}

if (problems.length > 0) {
  console.error(
    `Found ${problems.length} broken internal link${problems.length === 1 ? '' : 's'}:`,
  );
  for (const problem of problems) console.error(`- ${problem}`);
  process.exit(1);
}

console.log(
  `Checked ${checkedLinks} internal links across ${pages.length} generated pages (base: ${basePath || '/'}).`,
);
