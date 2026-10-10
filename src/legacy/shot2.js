const { chromium } = require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
const errs=[];p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});p.on('pageerror',e=>errs.push(String(e)));
await p.goto('file:///home/claude/portfolio/andrew-kuznetsov-portfolio.html');await p.waitForTimeout(1500);
for(const v of ['dots','velvet','hypno']){await p.click(`#pv button[data-v="${v}"]`);await p.waitForTimeout(700);await p.screenshot({path:`/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/v_${v}.png`,clip:{x:0,y:0,width:1440,height:900}});}
const m=await b.newPage({viewport:{width:400,height:820}});await m.goto('file:///home/claude/portfolio/andrew-kuznetsov-portfolio.html');await m.waitForTimeout(1500);
await m.screenshot({path:'/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/v_mob.png',clip:{x:0,y:0,width:400,height:1100}});
console.log(JSON.stringify({errs}));await b.close();})();
