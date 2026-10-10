const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const m=await b.newPage({viewport:{width:400,height:820}});
const errs=[];m.on('pageerror',e=>errs.push(String(e)));
await m.goto('file:///home/claude/portfolio/andrew-kuznetsov-portfolio.html',{waitUntil:'domcontentloaded'});await m.waitForTimeout(4500);
await m.screenshot({path:'/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/6mob.png',fullPage:true,timeout:60000,animations:'disabled'});
console.log(JSON.stringify({errs,sw:await m.evaluate(()=>document.documentElement.scrollWidth)}));await b.close();})();
