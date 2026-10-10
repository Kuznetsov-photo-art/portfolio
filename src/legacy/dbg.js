const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('file:///home/claude/portfolio/andrew-kuznetsov-portfolio.html');await p.waitForTimeout(4000);
console.log(await p.evaluate(()=>{window.scrollTo({top:2000,behavior:'instant'});return {sy:scrollY,ft:document.getElementById('focus').offsetTop,fh:document.getElementById('focus').offsetHeight,sh:document.documentElement.scrollHeight,bodyCls:document.body.className,pre:!!document.getElementById('pre'),ov:getComputedStyle(document.body).overflow}}));
await p.waitForTimeout(500);console.log(await p.evaluate(()=>scrollY));await b.close();})();
