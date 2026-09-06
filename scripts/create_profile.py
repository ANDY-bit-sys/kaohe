from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'pdf' / '刘锦桉_个人简介_详细版.pdf'
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
    text(80, y-1, title, 16, navy, True)

def paragraph(y, value):
    row = ''
    for char in value:
        if pdfmetrics.stringWidth(row + char, 'YaHei', 11) > W-96:
            carry = ''
            if char in '，。！？；：、）》」':
                carry, row = row[-1], row[:-1]
            text(48, y, row, 11)
            y -= 21
            row = carry + char
        else:
            row += char
    if row:
        text(48, y, row, 11)
        y -= 21
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
    ('项目兴趣：从好奇开始探索', '我喜欢研究一些新奇、有趣的项目。一个特别的想法、一项有意思的功能，都能引起我的兴趣，让我想进一步了解它是怎样实现的。对我来说，研究项目的乐趣不仅在于看到最终效果，也在于把不熟悉的东西一点点弄明白。我希望今后能从小项目入手，尝试把自己的想法变成实际作品，并在解决问题的过程中积累经验。'),
    ('课余爱好：在球场上享受运动', '学习之外，我还喜欢踢足球。足球吸引我的地方，既有奔跑和对抗带来的活力，也有队友之间传球、配合的乐趣。我希望在大学里继续保持这份爱好，在运动中放松身心，认识志同道合的朋友，让学习和课余生活都更加充实。'),
    ('大学期待：边学边做，逐步积累', '作为集成电路专业的新生，我还有很多知识需要学习。我希望先把基础学扎实，再通过具体项目理解知识的用途。参加这次考核，也是一次动手尝试的机会：从环境准备到作品制作，认真完成每一步，遇到问题就查资料、做验证，逐渐做到既能把作品做出来，也能讲清楚自己的思路。'),
]
y = 622
for i, (title, content) in enumerate(sections, 1):
    section(y, f'{i:02}', title)
    y = paragraph(y-31, content)
    if i < len(sections):
        line(y+4)
        y -= 25
assert y >= 65, y
line(60)
text(48,39,'刘锦桉  /  个人简介',9,muted)
text(235,39,'GitHub: github.com/ANDY-bit-sys',8,muted)
c.linkURL('https://github.com/ANDY-bit-sys', (235,35,W-48,51), relative=0)
c.save()

with pdfplumber.open(OUT) as pdf:
    assert len(pdf.pages) == 1
    extracted = pdf.pages[0].extract_text()
    for value in ['刘锦桉','广州市','2026级','集成电路1班','足球']:
        assert value in extracted, value
    pdf.pages[0].to_image(resolution=120).save(str(ROOT/'tmp'/'pdfs'/'profile_preview.png'))
print(OUT)
print(extracted)
