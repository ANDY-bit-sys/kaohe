from pathlib import Path
import argparse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description='生成刘锦桉的个人简介 PDF')
parser.add_argument('--output', type=Path, default=ROOT / 'output' / 'pdf' / '刘锦桉_个人简介_详细版.pdf')
OUT = parser.parse_args().output
OUT.parent.mkdir(parents=True, exist_ok=True)
(ROOT/'tmp'/'pdfs').mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont('YaHei', 'C:/Windows/Fonts/msyh.ttc', subfontIndex=0))
pdfmetrics.registerFont(TTFont('YaHeiBold', 'C:/Windows/Fonts/msyhbd.ttc', subfontIndex=0))
c = canvas.Canvas(str(OUT), pagesize=A4)
c.setTitle('刘锦桉 | 个人简介')
c.setAuthor('刘锦桉')
W, H = A4
navy, blue, ink, muted = map(HexColor, ['#14324F','#246BCE','#203449','#687B8F'])

def text(x, y, value, size=11, color=ink, bold=False):
    c.setFillColor(color)
    c.setFont('YaHeiBold' if bold else 'YaHei', size)
    c.drawString(x, y, value)

def line(y):
    c.setStrokeColor(HexColor('#DEE7F0'))
    c.setLineWidth(.7)
    c.line(48, y, W-48, y)

def section(y, number, title):
    text(48, y, number, 10, blue, True)
    text(80, y-1, title, 15, navy, True)

def paragraph(y, value, x=48, width=W-96, size=10.5, leading=19):
    row = ''
    for char in value:
        if pdfmetrics.stringWidth(row + char, 'YaHei', size) > width:
            carry = ''
            if char in '，。！？；：、）》」':
                carry, row = row[-1], row[:-1]
            text(x, y, row, size)
            y -= leading
            row = carry + char
        else:
            row += char
    if row:
        text(x, y, row, size)
        y -= leading
    return y

c.setFillColor(HexColor('#FFFFFF'))
c.rect(0, 0, W, H, fill=1, stroke=0)
c.setFillColor(navy)
c.rect(0, H-184, W, 184, fill=1, stroke=0)
c.setStrokeColor(Color(1,1,1,alpha=.12))
c.setLineWidth(1)
for offset in [0, 22, 44]:
    x = W-150+offset
    c.lines([(x,H, x,H-75-offset), (x,H-75-offset,W-42,H-75-offset), (W-42,H-75-offset,W-42,H-183)])
c.setFillColor(HexColor('#61B3FF'))
c.rect(48, H-51, 28, 3, fill=1, stroke=0)
text(48,H-73,'个人简介',12,HexColor('#BCD9F4'))
text(46,H-120,'刘锦桉',32,HexColor('#FFFFFF'),True)
text(49,H-151,'2026级 · 集成电路1班   |   广东省广州市',11,HexColor('#D7E9FA'))

sections = [
    ('关于我', '大家好，我叫刘锦桉，来自广东省广州市，是2026级集成电路1班的一名新生。带着对大学生活的期待，我希望在新的学习阶段打好专业基础，也多接触课堂之外的新鲜事物，在学习与实践中慢慢找到自己想深入探索的方向。'),
    ('我的优势：主动学习，积累专业基础', '我通过 B 站自学 C 语言，目前学习到指针章节，对 C 语言已有一定了解。此外，我还通过 B 站自学石群老师的《电路》课程，学习内容涵盖第一至第四章，逐步积累电路基础知识。我还通过 B 站自学 STM32，对单片机已有一定知识基础。这些学习经历体现了我主动学习的态度。'),
    ('项目兴趣：从好奇开始探索', '我喜欢研究一些新奇、有趣的项目。一个特别的想法、一项有意思的功能，都能引起我的兴趣，让我想进一步了解它是怎样实现的。对我来说，研究项目的乐趣不仅在于看到最终效果，也在于把不熟悉的东西一点点弄明白。我希望今后能从小项目入手，尝试把自己的想法变成实际作品，并在解决问题的过程中积累经验。'),
    ('课余爱好：在球场上享受运动', '学习之外，我还喜欢踢足球。足球吸引我的地方，既有奔跑和对抗带来的活力，也有队友之间传球、配合的乐趣。我希望在大学里继续保持这份爱好，在运动中放松身心，认识志同道合的朋友，让学习和课余生活都更加充实。'),
    ('大学期待：边学边做，逐步积累', '作为集成电路专业的新生，我还有很多知识需要学习。我希望先把基础学扎实，再通过具体项目理解知识的用途。参加这次考核，也是一次动手尝试的机会：从环境准备到作品制作，认真完成每一步，遇到问题就查资料、做验证，逐渐做到既能把作品做出来，也能讲清楚自己的思路。'),
]
y = 622
for i, (title, content) in enumerate(sections, 1):
    section(y, f'{i:02}', title)
    y = paragraph(y-28, content)
    if i < len(sections):
        line(y+4)
        y -= 22
assert y >= 65, y
line(60)
text(48,39,'刘锦桉  /  个人简介',9,muted)
text(235,39,'GitHub: github.com/ANDY-bit-sys',8,muted)
c.linkURL('https://github.com/ANDY-bit-sys', (235,35,430,51), relative=0)
text(W-77,39,'1 / 2',8,muted)
c.showPage()

# Keep the detailed introduction intact and give the two games a readable
# portfolio page with real screenshots and clickable play links.
c.setFillColor(HexColor('#FFFFFF'))
c.rect(0,0,W,H,fill=1,stroke=0)
c.setFillColor(navy)
c.rect(0,H-125,W,125,fill=1,stroke=0)
text(48,H-44,'刘锦桉  /  项目作品',12,HexColor('#BCD9F4'))
text(46,H-85,'把有趣的想法变成小游戏',23,HexColor('#FFFFFF'),True)
text(49,H-108,'两款大肥鱼游戏 · 可在浏览器中打开体验',10,HexColor('#D7E9FA'))

projects = [
    {
        'name':'大肥鱼木鱼',
        'kind':'交互解压小游戏',
        'image':'dafeyu-muyu.png',
        'description':'这是一款以大肥鱼角色为主题的木鱼小游戏。点击木鱼或按下空格，就能敲击木鱼、听到音效，并看到功德计数逐次累积。',
        'features':'体验重点：点击与键盘操作、敲击音效、功德计数。',
        'note':'用简单的操作和即时反馈，让小游戏成为学习之余的放松方式。',
        'url':'https://andy-bit-sys.github.io/dafeyu-muyu/',
    },
    {
        'name':'大肥鱼饭店',
        'kind':'餐厅经营小游戏 · 大肥鱼的小饭馆',
        'image':'dafeyu-restaurant.png',
        'description':'这是一款餐厅经营小游戏。玩家挑选每日菜单，拖放食材让豆包做菜，再由大肥鱼取餐、为客人送餐，在经营小店的过程中体验料理与服务的配合。',
        'features':'体验重点：每日菜单、食材搭配、做菜与送餐。',
        'note':'把食材、角色和顾客连接起来，让一家小饭馆逐渐运转起来。',
        'url':'https://andy-bit-sys.github.io/whales-little-kitchen/?v=achievement-rules-1009',
    },
]

for index, project in enumerate(projects):
    top = H-165-index*275
    section(top, f'{index+1:02}',project['name'])
    text(80,top-24,project['kind'],9,muted)
    image_y=top-223
    c.setFillColor(HexColor('#F5F8FC'))
    c.setStrokeColor(HexColor('#DEE7F0'))
    c.roundRect(48,image_y,208,179,7,stroke=1,fill=1)
    c.drawImage(str(ROOT/'assets'/'previews'/project['image']),54,image_y+6,
                width=196,height=167,preserveAspectRatio=True,anchor='c',mask='auto')
    content_y=paragraph(top-54,project['description'],x=277,width=W-325,size=10,leading=18)
    content_y=paragraph(content_y-7,project['features'],x=277,width=W-325,size=9.5,leading=17)
    content_y=paragraph(content_y-6,project['note'],x=277,width=W-325,size=9.5,leading=17)
    assert content_y >= image_y-2, (project['name'],content_y,image_y)
    text(48,image_y-22,'在线试玩：'+project['name']+'  ↗',10,blue,True)
    c.linkURL(project['url'], (46,image_y-28,260,image_y-8),relative=0)
    if index==0:
        line(image_y-33)

text(48,88,'更多作品与学习记录，可在我的个人网站查看。',9,muted)
line(60)
text(48,39,'刘锦桉  /  项目作品',9,muted)
text(235,39,'个人网站：andy-bit-sys.github.io/kaohe/',8,blue)
c.linkURL('https://andy-bit-sys.github.io/kaohe/',(233,35,474,51),relative=0)
text(W-77,39,'2 / 2',8,muted)
c.save()

with pdfplumber.open(OUT) as pdf:
    assert len(pdf.pages) == 2
    extracted = '\n'.join(page.extract_text() for page in pdf.pages)
    for value in ['刘锦桉','广州市','2026级','集成电路1班','足球','B 站','C 语言','指针','石群','第一至第四章','STM32','单片机已有一定知识基础','大肥鱼木鱼','大肥鱼饭店','每日菜单']:
        assert value in extracted, value
    links = [link.get('uri') for page in pdf.pages for link in page.hyperlinks]
    for project in projects:
        assert project['url'] in links, project['url']
    for index,page in enumerate(pdf.pages,1):
        page.to_image(resolution=120).save(str(ROOT/'tmp'/'pdfs'/f'profile_preview_{index}.png'))
print(OUT)
print(extracted)
