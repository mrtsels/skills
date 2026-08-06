#!/usr/bin/env node

/**
 * 微信公众号文章搜索工具
 * 通过搜狗微信搜索获取微信公众号文章
 */

const https = require('https');
const cheerio = require('cheerio');
const zlib = require('zlib');

const USER_AGENTS = [
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
  'Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/123.0.0.0 Chrome/123.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/122.0.0.0 Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  'Mozilla/5.0 (iPhone; CPU iPhone OS 16_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
  'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',
  'Mozilla/5.0 (Linux; Android 13; Mi 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
];

function getRandomUserAgent() {
  return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

const HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Encoding': 'identity',
  'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
  'Host': 'weixin.sogou.com',
  'Referer': 'https://weixin.sogou.com/',
};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function decompressBody(buffer, contentEncoding) {
  if (!contentEncoding) return buffer;
  const encoding = String(contentEncoding).toLowerCase();
  try {
    if (encoding.includes('gzip')) return zlib.gunzipSync(buffer);
    if (encoding.includes('deflate')) return zlib.inflateSync(buffer);
    if (encoding.includes('br')) return zlib.brotliDecompressSync(buffer);
  } catch {}
  return buffer;
}

async function request(options) {
  const { url, method = 'GET', headers = {}, timeoutMs = 15000, retries = 0 } = options;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      return await new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const req = https.request({
          hostname: urlObj.hostname,
          path: urlObj.pathname + urlObj.search,
          method, headers,
        }, (res) => {
          const chunks = [];
          res.on('data', (chunk) => chunks.push(chunk));
          res.on('end', () => {
            const raw = Buffer.concat(chunks);
            resolve({ statusCode: res.statusCode || 0, headers: res.headers, body: decompressBody(raw, res.headers['content-encoding']) });
          });
        });
        req.on('error', reject);
        req.setTimeout(timeoutMs, () => { req.destroy(); reject(new Error('Request timeout')); });
        req.end();
      });
    } catch (e) {
      if (attempt >= retries) throw new Error(`Request failed: ${url}: ${e.message}`);
      await sleep(300 + attempt * 300);
    }
  }
}

async function requestText(options) {
  const resp = await request(options);
  return { ...resp, text: resp.body.toString('utf-8') };
}

function extractCookies(headers) {
  const cookies = [];
  const setCookieHeader = headers['set-cookie'];
  if (setCookieHeader) setCookieHeader.forEach(c => { const v = c.split(';')[0]; if (v) cookies.push(v); });
  return cookies.join('; ');
}

async function getSogouCookie() {
  try {
    const resp = await request({
      url: 'https://v.sogou.com/v?ie=utf8&query=&p=40030600',
      headers: { 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 'Accept-Encoding': 'identity', 'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8', 'User-Agent': getRandomUserAgent() },
      timeoutMs: 10000, retries: 1,
    });
    return { cookieStr: extractCookies(resp.headers) || '' };
  } catch { return { cookieStr: '' }; }
}

async function httpGet(url, cookieStr = '') {
  const headers = { ...HEADERS, 'User-Agent': getRandomUserAgent() };
  if (cookieStr) headers['Cookie'] = cookieStr;
  const resp = await requestText({ url, headers, timeoutMs: 30000, retries: 1 });
  return resp.text;
}

function parseArticlesFromSearchHtml(html, maxResults) {
  const articles = [];
  const $ = cheerio.load(html);
  const $newsList = $('ul.news-list');
  if ($newsList.length === 0) return [];
  $newsList.find('li').each((_, element) => {
    if (articles.length >= maxResults) return false;
    const article = parseArticle($, element);
    if (article) articles.push(article);
  });
  return articles;
}

function parseArticle($, element) {
  try {
    const $elem = $(element);
    const $titleLink = $elem.find('h3 a');
    if ($titleLink.length === 0) return null;
    const title = $titleLink.text().trim();
    let url = $titleLink.attr('href') || '';
    if (url.startsWith('/')) url = `https://weixin.sogou.com${url}`;
    const summary = $elem.find('p.txt-info').text().trim();
    let datetime = '', dateText = '', source = '', timeDescription = '';
    const $sourceBox = $elem.find('.s-p');
    if ($sourceBox.length > 0) {
      const $dateScript = $sourceBox.find('.s2 script');
      if ($dateScript.length > 0) {
        const tsMatch = $dateScript.text().match(/(\d{10})/);
        if (tsMatch) {
          const date = new Date(parseInt(tsMatch[1]) * 1000);
          datetime = formatChinaDateTime(date);
          dateText = `${date.getFullYear()}年${String(date.getMonth()+1).padStart(2,'0')}月${String(date.getDate()).padStart(2,'0')}日`;
        }
      }
      source = $sourceBox.find('.all-time-y2').text().trim() || $sourceBox.find('a.account').text().trim();
    }
    return { title, url, summary, datetime, date_text: dateText, source };
  } catch { return null; }
}

function formatChinaDateTime(date) {
  const chinaTime = new Date(date.getTime() + 8 * 60 * 60 * 1000);
  return `${chinaTime.getUTCFullYear()}-${String(chinaTime.getUTCMonth()+1).padStart(2,'0')}-${String(chinaTime.getUTCDate()).padStart(2,'0')} ${String(chinaTime.getUTCHours()).padStart(2,'0')}:${String(chinaTime.getUTCMinutes()).padStart(2,'0')}:${String(chinaTime.getUTCSeconds()).padStart(2,'0')}`;
}

function parseCliArgs(args) {
  let query = '', num = 10, output = '', resolveRealUrl = false;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '-n' || args[i] === '--num') { num = parseInt(args[i+1]) || 10; i++; }
    else if (args[i] === '-o' || args[i] === '--output') { output = args[i+1] || ''; i++; }
    else if (args[i] === '-r' || args[i] === '--resolve-url') { resolveRealUrl = true; }
    else if (!args[i].startsWith('-')) { query = args[i]; }
  }
  return { query, num, output, resolveRealUrl };
}

async function searchWechatArticles(query, maxResults = 10, resolveRealUrl = false) {
  maxResults = Math.min(maxResults, 50);
  const articles = [];
  let page = 1;
  const pagesNeeded = Math.ceil(maxResults / 10);
  while (articles.length < maxResults && page <= pagesNeeded) {
    try {
      const { cookieStr } = await getSogouCookie();
      const html = await httpGet(`https://weixin.sogou.com/weixin?query=${encodeURIComponent(query)}&s_from=input&_sug_=n&type=2&page=${page}&ie=utf8`, cookieStr);
      const parsed = parseArticlesFromSearchHtml(html, maxResults - articles.length);
      if (parsed.length === 0) break;
      articles.push(...parsed);
      page++;
      if (page <= pagesNeeded) await sleep(500 + Math.random() * 1000);
    } catch (e) { console.error('请求失败:', e.message); break; }
  }
  return articles.slice(0, maxResults);
}

async function main() {
  const args = process.argv.slice(2);
  const { query, num, output, resolveRealUrl } = parseCliArgs(args);
  if (!query) {
    console.log('用法: node search_wechat.js <关键词> [-n 数量] [-o 文件] [-r]');
    process.exit(0);
  }
  const articles = await searchWechatArticles(query, num, resolveRealUrl);
  const result = { query, total: articles.length, articles };
  const jsonOutput = JSON.stringify(result, null, 2);
  if (output) { require('fs').writeFileSync(output, jsonOutput, 'utf-8'); console.error('已保存到:', output); }
  console.log(jsonOutput);
}

if (require.main === module) main();
module.exports = { searchWechatArticles };