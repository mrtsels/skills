#!/usr/bin/env node
/**
 * claude-mimo-proxy
 *
 * Fixes Claude Code 2.1.154+ compatibility with third-party Anthropic-compatible
 * APIs (CCX/DeepSeek, MiMo, 智谱, etc.) that do not accept role:system in messages[].
 *
 * Claude Code >=2.1.154 sends system prompts as {"role":"system","content":"..."}
 * inside messages[]. Third-party APIs expect the old format with a top-level
 * "system" field. This proxy converts before forwarding to CCX or similar.
 *
 * Usage:
 *   node ~/.claude/claude-mimo-proxy.js &
 *
 * Env vars:
 *   PORT     - proxy listen port (default 4567)
 *   UPSTREAM - upstream proxy URL (default http://127.0.0.1:3000 for CCX)
 */

const http = require('http');
const httpUpstream = require('http');

const UPSTREAM = process.env.UPSTREAM || 'http://127.0.0.1:3000';
const PORT = parseInt(process.env.PORT || '4567', 10);
const UPSTREAM_URL = new URL(UPSTREAM);

function fixRequestBody(body) {
  try {
    const data = JSON.parse(body);
    if (!Array.isArray(data.messages)) return body;

    const systemParts = [];
    const cleanMessages = [];

    for (const msg of data.messages) {
      if (msg.role === 'system') {
        if (typeof msg.content === 'string') systemParts.push(msg.content);
        else if (Array.isArray(msg.content))
          for (const b of msg.content)
            if (typeof b === 'string') systemParts.push(b);
            else if (b.type === 'text' && b.text) systemParts.push(b.text);
      } else cleanMessages.push(msg);
    }

    if (systemParts.length > 0) {
      const existing = data.system;
      if (typeof existing === 'string') systemParts.unshift(existing);
      else if (Array.isArray(existing))
        for (const b of existing)
          if (typeof b === 'string') systemParts.unshift(b);
          else if (b.type === 'text' && b.text) systemParts.unshift(b.text);

      data.system = systemParts.join('\n\n');
      data.messages = cleanMessages;
      return JSON.stringify(data);
    }

    return body;
  } catch (e) {
    console.error('[proxy] parse error:', e.message);
    return body;
  }
}

function forwardRequest(clientReq, clientRes) {
  let body = [];
  clientReq.on('data', chunk => body.push(chunk));
  clientReq.on('end', () => {
    const rawBody = Buffer.concat(body).toString('utf8');
    const fixedBody = fixRequestBody(rawBody);

    const opts = {
      hostname: UPSTREAM_URL.hostname,
      port: UPSTREAM_URL.port,
      path: clientReq.url,
      method: clientReq.method,
      headers: { ...clientReq.headers, host: UPSTREAM_URL.host },
    };
    delete opts.headers['content-length'];
    opts.headers['content-length'] = Buffer.byteLength(fixedBody);

    const proxyReq = httpUpstream.request(opts, proxyRes => {
      clientRes.writeHead(proxyRes.statusCode, proxyRes.headers);
      proxyRes.pipe(clientRes);
    });

    proxyReq.on('error', err => {
      console.error('[proxy] forward error:', err.message);
      clientRes.writeHead(502, { 'Content-Type': 'application/json' });
      clientRes.end(JSON.stringify({
        type: 'error',
        error: { type: 'proxy_error', message: err.message }
      }));
    });

    proxyReq.write(fixedBody);
    proxyReq.end();
  });
}

const server = http.createServer((req, res) => {
  console.log(`[proxy] ${new Date().toISOString()} ${req.method} ${req.url}`);
  forwardRequest(req, res);
});

server.listen(PORT, '127.0.0.1', () => {
  console.log(`[proxy] listening on :${PORT} → ${UPSTREAM}`);
  console.log(`[proxy] Set ANTHROPIC_BASE_URL=http://127.0.0.1:${PORT}`);
});

server.on('error', err => {
  if (err.code === 'EADDRINUSE')
    console.error(`[proxy] Port ${PORT} already in use (lsof -i :${PORT})`);
  else console.error('[proxy]', err);
  process.exit(1);
});
