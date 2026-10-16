// Check workflow scripts before launching them with the Workflow tool.
//   node tools/workflows/check.mjs [files...]          parse each script the way the Workflow runtime runs it
//                                                       (an async body with args / agent / parallel / ... in scope)
//   node tools/workflows/check.mjs --dry [files...]    also RUN it with stub hooks (every agent returns a dummy object
//                                                       built from its schema, child workflows return []) - catches
//                                                       ReferenceErrors and bad args handling; spends nothing. It also
//                                                       runs each script WITHOUT args.branch / args.trailer and fails
//                                                       it unless it refuses to start (no commits under an old session)
// Default files: tools/workflows/*.js and tools/workflows/templates/*.js. (node --check alone does not catch a
// top-level return / await mismatch the runtime would reject.)
import fs from 'fs'
import path from 'path'
import url from 'url'

const here = path.dirname(url.fileURLToPath(import.meta.url))
const argv = process.argv.slice(2)
const dry = argv.includes('--dry')
let files = argv.filter((a) => !a.startsWith('--'))
if (!files.length) {
  files = [here, path.join(here, 'templates')].flatMap((d) => fs.readdirSync(d).filter((f) => f.endsWith('.js')).map((f) => path.join(d, f)))
}
const AF = Object.getPrototypeOf(async function () {}).constructor
const dummy = (s) => {
  if (!s) return 'x'
  if (s.type === 'object') return Object.fromEntries(Object.entries(s.properties || {}).map(([k, v]) => [k, dummy(v)]))
  if (s.type === 'array') return []
  if (s.type === 'number' || s.type === 'integer') return 0
  if (s.type === 'boolean') return false
  return 'x'
}
// sample args that every script in this folder accepts (unknown keys are ignored)
const SAMPLE = { first_round: 99, n_rounds: 1, track: 'dry', focus: 'dry run', round: 99, state: 's', lenses: [{ key: 'k', brief: 'LENS: b' }],
  top_n: 2, exclude: [], targets: ['dry-id'], slice: 'r99-A', items: [{ id: 'dry-id', name: 'dry', note: 'n' }], lead: 20, gen: 99, id: 'dry-id', winner: 'w',
  short: 'dry', slug: 'dry-id', new_mechanism: 'm', claim: 'c', context: 'c', task: 't', design: 'd', request: 'r', date: '2026-01-01',
  branch: 'dry-branch', trailer: 'Dry-Run: a\nDry-Run: b' }
let bad = 0
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8')
  if (!/^export const meta = \{/m.test(src)) { console.log('FAIL (no "export const meta = {" header)', f); bad++; continue }
  let fn
  try { fn = new AF('args', 'agent', 'parallel', 'pipeline', 'phase', 'log', 'workflow', 'budget', src.replace(/^export const meta/m, 'const meta')) }
  catch (e) { console.log('PARSE FAIL', f, e.message); bad++; continue }
  if (!dry) { console.log('parse ok', f); continue }
  let n = 0
  const agent = async (p, o) => { n++; if (typeof p !== 'string' || !p.length) throw new Error('empty prompt'); return o && o.schema ? dummy(o.schema) : 'x' }
  const parallel = async (th) => Promise.all(th.map((t) => Promise.resolve().then(t).catch(() => null)))
  const pipeline = async (items, ...stages) => Promise.all(items.map(async (it, i) => { let r = it; for (const s of stages) { r = await s(r, it, i) } return r }))
  const workflow = async () => []
  try {
    await fn(SAMPLE, agent, parallel, pipeline, () => {}, () => {}, workflow, { total: null, spent: () => 0, remaining: () => Infinity })
    console.log(`dry ok (${n} agent calls)`, f)
  } catch (e) { console.log('DRY FAIL', f, e.message); bad++; continue }
  const { branch, trailer, ...noSession } = SAMPLE
  n = 0
  const refused = await fn(noSession, agent, parallel, pipeline, () => {}, () => {}, workflow, { total: null, spent: () => 0, remaining: () => Infinity })
    .then(() => false, (e) => /args\.branch and args\.trailer are required/.test(e.message) && n === 0)
  if (refused) console.log('  refuses to start without branch / trailer: ok')
  else { console.log('DRY FAIL (starts without args.branch / args.trailer: it would commit under another session)', f); bad++ }
}
process.exit(bad ? 1 : 0)
