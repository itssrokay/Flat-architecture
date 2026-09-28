// Vercel serverless function: POST /api/chat
// The OpenAI key lives ONLY here, as an environment variable set in the Vercel project settings:
//   OPENAI_API_KEY   (required)  your key
//   CHAT_PASSCODE    (optional, recommended) a word the page asks for once, so strangers with the link can't use your key
//   OPENAI_MODEL     (optional)  default below; change it if OpenAI renames models
//   OPENAI_BASE_URL  (optional)  default https://api.openai.com/v1
// The page sends { knowledge, state, messages, lang }; this adds the rules and forwards to OpenAI.
const DEFAULT_MODEL = 'gpt-6-luna';

const RULES = `You are the friendly home-interior guide inside "MyFlat", a 3D viewer of the user's own flat in India.
The user is a beginner (and their father may use it too), so explain simply, like a knowledgeable friend: short paragraphs or short bullet lists, no jargon without a one-line meaning.
Use ONLY the KNOWLEDGE and STATE below for facts about this flat, its designs, sizes and budgets. If something isn't there, say so and give general guidance, clearly marked as general.
Prices are 2026 Indian metro estimates in rupees; always suggest getting 2-3 local quotes for big items. Use feet-inches like the notes do.
When comparing alternatives give a small table or bullets with cost, pros, cons, and your recommendation for THIS room.
Keep answers under about 180 words unless the user asks for detail.
Reply in the language of the user's message; if STATE.lang is "hi", reply in simple Hindi (Devanagari), keeping brand names and sizes as they are.
If the user asks you to change a Customise choice of the current design, and the choice exists in STATE.customise.options, end your reply with ONE line exactly like:
ACTION: {"key":"optionId"}
(only keys/ids that exist there; several keys allowed in the same JSON). Never output ACTION otherwise.`;

const hits = new Map();   // very small per-instance rate limit: 30 requests / 10 min per IP
function limited(ip) {
  const now = Date.now(), w = (hits.get(ip) || []).filter(t => now - t < 600000);
  w.push(now); hits.set(ip, w); return w.length > 30;
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') { res.status(405).json({ error: 'POST only' }); return; }
  const key = process.env.OPENAI_API_KEY;
  if (!key) { res.status(500).json({ error: 'The chat is not set up yet: add OPENAI_API_KEY in the Vercel project settings (Settings → Environment Variables), then redeploy.' }); return; }
  const pass = process.env.CHAT_PASSCODE;
  if (pass && (req.headers['x-chat-passcode'] || '') !== pass) { res.status(401).json({ error: 'passcode' }); return; }
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0] || 'x';
  if (limited(ip)) { res.status(429).json({ error: 'Too many questions in a short time. Please wait a few minutes.' }); return; }
  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  const { knowledge = '', state = {}, messages = [], lang = 'en' } = body || {};
  const msgs = (Array.isArray(messages) ? messages : []).slice(-12)
    .filter(m => m && (m.role === 'user' || m.role === 'assistant') && typeof m.content === 'string')
    .map(m => ({ role: m.role, content: m.content.slice(0, 2000) }));
  if (!msgs.length) { res.status(400).json({ error: 'empty question' }); return; }
  const payload = {
    model: process.env.OPENAI_MODEL || DEFAULT_MODEL,
    max_completion_tokens: 900,
    messages: [
      { role: 'system', content: RULES + '\n\n=== KNOWLEDGE ===\n' + String(knowledge).slice(0, 160000) },
      { role: 'system', content: '=== STATE (what the user sees right now) ===\n' + JSON.stringify({ ...state, lang }).slice(0, 12000) },
      ...msgs,
    ],
  };
  try {
    const r = await fetch((process.env.OPENAI_BASE_URL || 'https://api.openai.com/v1') + '/chat/completions', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + key }, body: JSON.stringify(payload),
    });
    const j = await r.json().catch(() => ({}));
    if (!r.ok) { res.status(502).json({ error: 'OpenAI: ' + (j.error?.message || r.status) }); return; }
    res.status(200).json({ reply: j.choices?.[0]?.message?.content || '', model: j.model, usage: j.usage });
  } catch (e) {
    res.status(502).json({ error: 'Could not reach OpenAI: ' + (e.message || e) });
  }
};
