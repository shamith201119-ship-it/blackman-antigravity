export default function handler(req, res) {
  // Returns config with the GitHub token (kept server-side, never exposed in source)
  res.setHeader('Content-Type', 'application/javascript');
  const token = process.env.GH_TOKEN || '';
  res.send(`window.__GH_TOKEN__ = ${JSON.stringify(token)};`);
}
