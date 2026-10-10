const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
const errs=[];p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
const S='/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/';
await p.goto('file:///home/claude/portfolio/andrew-kuznetsov-portfolio.html');await p.waitForTimeout(900);
await p.screenshot({path:S+'p1.png'});await p.waitForTimeout(3000);
const h=await p.evaluate(()=>document.getElementById('focus').offsetTop);
for(const [i,f] of [[0,.1],[1,.45],[2,.8]]){await p.evaluate((y)=>window.scrollTo({top:y,behavior:'instant'}),h+f*(await p.evaluate(()=>document.getElementById('focus').offsetHeight-innerHeight)));await p.waitForTimeout(800);await p.screenshot({path:S+`f${i}.png`});}
console.log(JSON.stringify({errs}));await b.close();})();
