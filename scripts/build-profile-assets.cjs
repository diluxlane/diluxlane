// One-time artwork composition. Requires sharp; runtime analytics uses Python stdlib only.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const root = path.resolve(__dirname, '..');
const profile = path.join(root, 'assets/profile');
const code = [
  ['const ', 'dilux', ' = {'],
  ['  basedIn: ', '"Sri Lanka"', ','],
  ['  role: ', '"Student developer"', ','],
  ['  founded: ', '"Zyberlane"', ','],
  ['  building: [', '', ''],
  ['    ', '"Websites & client CMS"', ''],
  ['  ],', '', ''],
  ['  workflow: ', '"AI-assisted"', ','],
  ['  learning: [', '', ''],
  ['    ', '"Systems & automation"', ','],
  ['    ', '"Cybersecurity basics"', ''],
  ['  ],', '', ''],
  ['  beyondCode: ', '"Filmmaking"', ''],
  ['};', '', ''],
];
const esc = s => s.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="650" height="580" viewBox="0 0 650 580"><rect x="1" y="1" width="648" height="578" rx="18" fill="#101115" stroke="#303036"/><g font-family="monospace"><circle cx="30" cy="31" r="5" fill="#b41423"/><circle cx="48" cy="31" r="5" fill="#54515a"/><circle cx="66" cy="31" r="5" fill="#343139"/><text x="100" y="36" font-size="16" fill="#a8afb9">dilux.js</text><path d="M1 61H649" stroke="#303036"/>${code.map((line,i)=>`<text x="28" y="${105+i*31}" font-size="25" xml:space="preserve"><tspan fill="#c3c7d0">${esc(line[0])}</tspan><tspan fill="${i===0?'#fff':'#f1acb7'}">${esc(line[1])}</tspan><tspan fill="#c3c7d0">${esc(line[2])}</tspan></text>`).join('')}<text x="28" y="555" font-size="15" fill="#a8afb9">// building through practice &amp; review</text></g></svg>`;
async function main() {
  fs.writeFileSync(path.join(profile,'about-code.svg'),svg);
  const codeBuffer=await sharp(Buffer.from(svg)).png().toBuffer();
  const illustration=await sharp(path.join(profile,'developer.webp')).resize(450,580,{fit:'contain',background:'#0b0b0b'}).png().toBuffer();
  await sharp({create:{width:1120,height:580,channels:3,background:'#0b0b0b'}}).composite([{input:codeBuffer,left:0,top:0},{input:illustration,left:670,top:0}]).webp({quality:91}).toFile(path.join(profile,'about-wide.webp'));
  const mobileArt=await sharp(path.join(profile,'developer.webp')).resize(650,650).png().toBuffer();
  await sharp({create:{width:650,height:1230,channels:3,background:'#0b0b0b'}}).composite([{input:codeBuffer,left:0,top:0},{input:mobileArt,left:0,top:580}]).webp({quality:91}).toFile(path.join(profile,'about-mobile.webp'));
  const labels={html:'HTML',css:'CSS',javascript:'JavaScript',astro:'Astro',tailwind:'Tailwind',vite:'Vite',supabase:'Supabase',git:'Git',github:'GitHub',vercel:'Vercel',playwright:'Playwright',typescript:'TS tooling'};
  for(const [name,label] of Object.entries(labels)) {
    const raw=fs.readFileSync(path.join(root,`assets/icons/${name}.svg`),'utf8');
    let inner=raw.replace(/^.*?<svg[^>]*>/s,'').replace(/<\/svg>\s*$/,'');
    if(['github','vercel'].includes(name)) inner=inner.replace(/fill="(?:#000(?:000)?|black|currentColor)"/g,'fill="#f0f0f0"');
    const view=raw.match(/viewBox="([^"]+)"/)[1];
    const tile=`<svg xmlns="http://www.w3.org/2000/svg" width="88" height="90" viewBox="0 0 88 90" role="img"><title>${label}</title><rect x="1" y="1" width="86" height="88" rx="12" fill="#111217" stroke="#303036"/><svg x="23" y="14" width="42" height="42" viewBox="${view}" fill="#f0f0f0">${inner}</svg><text x="44" y="76" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#e5e5e9">${label}</text></svg>`;
    fs.writeFileSync(path.join(root,`assets/icons/${name}-tile.svg`),tile);
  }
  console.log('Composed responsive About artwork and 12 local labelled icon tiles.');
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
