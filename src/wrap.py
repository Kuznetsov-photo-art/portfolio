import re,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # repo root
def wrap(src,dst,title=None,desc='',canonical='',image='',og_title='',og_desc='',theme='#0a0a0a'):
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
<meta name="theme-color" content="{theme}">
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Andrew Kuznetsov">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{og_title or t}">
<meta property="og:description" content="{og_desc or desc}">
{('<meta property="og:url" content="'+canonical+'">') if canonical else ''}
{('<meta property="og:image" content="'+image+'">'+chr(10)+'<meta property="og:image:width" content="1200">'+chr(10)+'<meta property="og:image:height" content="630">'+chr(10)+'<meta name="twitter:card" content="summary_large_image">'+chr(10)+'<meta name="twitter:image" content="'+image+'">') if image else ''}
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
    wrap(J(R,'src','index-src.html'),J(R,'index.html'),desc='Андрей Кузнецов — Lead Product Designer · AI & Design Systems. Портфолио: продуктовый дизайн, дизайн-системы, AI-инструменты', canonical='https://andrewkuznetsov.com/', image='https://andrewkuznetsov.com/assets/og/og-home.jpg',
     og_title='Портфолио продуктового дизайнера', og_desc='14 лет в дизайне: дизайн-системы, финтех, медтех и AI-продукты. Сбер, ВТБ, VK, YouGile, Lab4U, Финам')
wrap(J(R,'src','cases','obzhora','obzhora-case.html'),J(R,'cases','obzhora','index.html'),desc='Кейс «Обжора» — счётчик калорий для iOS: 60+ экранов, 83+ иконок, тёмная тема. Андрей Кузнецов', canonical='https://andrewkuznetsov.com/cases/obzhora/', image='https://andrewkuznetsov.com/assets/og/og-obzhora.jpg',
     og_title='Кейс «Обжора» — счётчик калорий для iOS', og_desc='60+ экранов, 83+ иконок, светлая и тёмная тема — от концепции до UI-кита')
if os.path.exists(J(R,'src','cases','finam','finam-case.html')):
    os.makedirs(J(R,'cases','finam'),exist_ok=True)
    wrap(J(R,'src','cases','finam','finam-case.html'),J(R,'cases','finam','index.html'),desc='Кейс FinamX & Limex — AI-платформа для трейдеров на два рынка: веб, мобильное приложение и мультибрендовая дизайн-система. Андрей Кузнецов', canonical='https://andrewkuznetsov.com/cases/finam/', image='https://andrewkuznetsov.com/assets/og/og-finam.jpg',
     og_title='Кейс FinamX & Limex — AI-платформа для трейдеров', og_desc='Веб, мобильное приложение и одна дизайн-система на два бренда и две темы', theme='#0b0a10')
print('ok')
