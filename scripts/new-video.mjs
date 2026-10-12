#!/usr/bin/env node
import { cpSync, mkdirSync, existsSync, readFileSync, writeFileSync, copyFileSync } from 'node:fs';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const slug = process.argv[2];
if (!slug || slug === '--help') {
  console.log('Usage: npm run new-video -- <lowercase-project-slug>');
  process.exit(slug ? 0 : 1);
}
if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) throw new Error('Use a lowercase kebab-case slug, not a path.');
const dest = join(root, 'video-projects', slug);
if (existsSync(dest)) throw new Error(`Project already exists: ${slug}. Choose a new name.`);
const gsap = join(root, 'node_modules/gsap/dist/gsap.min.js');
if (!existsSync(gsap)) throw new Error('Run npm ci in the kit root first.');
cpSync(join(root, 'examples/starter'), dest, { recursive: true, errorOnExist: true });
mkdirSync(join(dest, 'assets'), { recursive: true });
mkdirSync(join(dest, 'compositions'), { recursive: true });
mkdirSync(join(dest, 'renders'), { recursive: true });
copyFileSync(gsap, join(dest, 'assets/gsap.min.js'));
// ExploreAI brand kit: tokens, logo, background, and the brand DESIGN file.
const brand = ['brand-token.css', 'exploreai-logo.png', 'exploreai-background.png'];
const missing = brand.filter((file) => !existsSync(join(root, 'assets', file)));
for (const file of brand) if (!missing.includes(file)) copyFileSync(join(root, 'assets', file), join(dest, 'assets', file));
if (existsSync(join(root, 'assets/fonts'))) cpSync(join(root, 'assets/fonts'), join(dest, 'assets/fonts'), { recursive: true });
copyFileSync(join(root, 'DESIGN.exploreai.md'), join(dest, 'DESIGN.md'));
if (missing.length) console.warn(`Brand assets not found in assets/: ${missing.join(', ')}`);
const meta = JSON.parse(readFileSync(join(dest, 'meta.json'), 'utf8'));
meta.name = slug;
writeFileSync(join(dest, 'meta.json'), JSON.stringify(meta, null, 2) + '\n');
console.log(`Created video-projects/${slug}. Run HyperFrames from that folder.`);
