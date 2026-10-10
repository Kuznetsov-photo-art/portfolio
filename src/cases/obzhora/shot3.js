const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1440,height:900}});
await p.goto('file:///home/claude/portfolio/cases/obzhora/obzhora-case.html',{waitUntil:'domcontentloaded',timeout:60000});
await p.waitForTimeout(2500); const S='/tmp/claude-0/-home-claude/9cb87570-c146-5b9a-9fb9-fdbe54368d2e/scratchpad/';
const ys=await p.evaluate(()=>[...document.querySelectorAll('.sec')].map(e=>e.offsetTop));
await p.click('#tgl'); await p.waitForTimeout(600);
for(const [i,y] of [[4,ys[4]+200],[5,ys[5]+300],[7,ys[7]+100]]){await p.evaluate(v=>scrollTo(0,v),y); await p.waitForTimeout(900); await p.screenshot({path:S+`s${i}.png`,timeout:60000});}
await b.close();})();
