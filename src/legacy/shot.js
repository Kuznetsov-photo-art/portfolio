const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900},deviceScaleFactor:1});
const errs=[];p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
await p.goto('file:///home/claude/portfolio/andrew-kuznetsov-portfolio.html');await p.waitForTimeout(2500);
await p.screenshot({path:'/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/full.png',fullPage:true});
const m=await b.newPage({viewport:{width:400,height:820}});await m.goto('file:///home/claude/portfolio/andrew-kuznetsov-portfolio.html');await m.waitForTimeout(2000);
await m.screenshot({path:'/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/mob.png',fullPage:true});
console.log(JSON.stringify({errs, sw:await m.evaluate(()=>document.documentElement.scrollWidth)}));await b.close();})();
