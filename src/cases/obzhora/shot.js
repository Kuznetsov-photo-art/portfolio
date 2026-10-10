const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('file:///home/claude/portfolio/cases/obzhora/obzhora-case.html',{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForTimeout(2500);
const H=await p.evaluate(()=>document.body.scrollHeight); console.log('H',H);
const stops=[0,900,1800,2700,3800,4900,6000,7200,8400,9600,10800,12000,13200,14400,15600,16800,18000];
for(const s of stops){ if(s>H) break; await p.evaluate(y=>scrollTo(0,y),s); await p.waitForTimeout(900); await p.screenshot({path:`/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/c_${String(s).padStart(5,'0')}.png`,timeout:60000}); }
await b.close();})();
