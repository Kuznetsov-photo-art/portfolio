import re,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
def wrap(src,dst,title=None,desc='',canonical=''):
    s=open(src,encoding='utf-8').read()
    if s.lstrip().startswith('<!doctype'): open(dst,'w',encoding='utf-8').write(s); return
    i=s.index('</style>')+len('</style>')
    m=re.search(r'\n<(div|nav|header|main|section|canvas|a |button)',s[i:])
    cut=i+m.start()
    head,body=s[:cut],s[cut:]
    t=re.search(r'<title>(.*?)</title>',head).group(1)
    meta=f'''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{desc}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{desc}">
{('<link rel="canonical" href="'+canonical+'">') if canonical else ''}
<meta name="robots" content="index,follow">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
'''
    head=head.replace('<meta name="viewport" content="width=device-width,initial-scale=1">\n','')
    out=meta+head+'\n</head>\n<body>'+body+'\n</body>\n</html>\n'
    open(dst,'w',encoding='utf-8').write(out)
J=os.path.join
if os.path.exists(J(R,'src','index-src.html')):
    wrap(J(R,'src','index-src.html'),J(R,'index.html'),desc='Андрей Кузнецов — Lead Product Designer · AI & Design Systems. Портфолио: продуктовый дизайн, дизайн-системы, AI-инструменты.')
wrap(J(R,'src','cases','obzhora','obzhora-case.html'),J(R,'cases','obzhora','index.html'),desc='Кейс «Обжора» — счётчик калорий для iOS: 60+ экранов, 83+ иконок, тёмная тема. Андрей Кузнецов.')
print('ok')
