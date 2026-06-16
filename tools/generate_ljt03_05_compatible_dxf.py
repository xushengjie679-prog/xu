from pathlib import Path
import math

OUT = Path('cad/LJT03.05_顶尖_兼容版.dxf')

class DXF:
    def __init__(self):
        self.entities = []
    def add(self, *items):
        self.entities.extend(str(i) for i in items)
    def line(self, x1, y1, x2, y2, layer='OBJECT'):
        self.add(0,'LINE',8,layer,10,f'{x1:.3f}',20,f'{y1:.3f}',30,0,11,f'{x2:.3f}',21,f'{y2:.3f}',31,0)
    def circle(self, x, y, r, layer='OBJECT'):
        self.add(0,'CIRCLE',8,layer,10,f'{x:.3f}',20,f'{y:.3f}',30,0,40,f'{r:.3f}')
    def arc(self, x, y, r, a1, a2, layer='OBJECT'):
        self.add(0,'ARC',8,layer,10,f'{x:.3f}',20,f'{y:.3f}',30,0,40,f'{r:.3f}',50,f'{a1:.3f}',51,f'{a2:.3f}')
    def text(self, x, y, h, s, rot=0, layer='TEXT', align='LEFT'):
        # Keep DXF TEXT payload ASCII-only for mobile CAD viewers that lack Chinese SHX fonts.
        clean = s.encode('ascii', 'ignore').decode('ascii')
        self.add(0,'TEXT',8,layer,10,f'{x:.3f}',20,f'{y:.3f}',30,0,40,f'{h:.3f}',1,clean,50,f'{rot:.3f}',7,'STANDARD')
        if align == 'CENTER':
            self.add(72,1,11,f'{x:.3f}',21,f'{y:.3f}',31,0)
    def poly(self, pts, closed=False, layer='OBJECT'):
        self.add(0,'POLYLINE',8,layer,66,1,70,1 if closed else 0)
        for x,y in pts:
            self.add(0,'VERTEX',8,layer,10,f'{x:.3f}',20,f'{y:.3f}',30,0)
        self.add(0,'SEQEND')
    def arrow(self, x, y, angle, size=3.0, layer='DIM'):
        a=math.radians(angle)
        back=(x-size*math.cos(a), y-size*math.sin(a))
        p=(-math.sin(a), math.cos(a))
        pts=[(x,y),(back[0]+size*.35*p[0],back[1]+size*.35*p[1]),(back[0]-size*.35*p[0],back[1]-size*.35*p[1])]
        self.poly(pts, True, layer)
    def dim_h(self, x1, x2, y, ext_y, label, text_y=None):
        self.line(x1, ext_y, x1, y, 'DIM'); self.line(x2, ext_y, x2, y, 'DIM')
        self.line(x1, y, x2, y, 'DIM'); self.arrow(x1, y, 0); self.arrow(x2, y, 180)
        self.text((x1+x2)/2-5, text_y if text_y is not None else y+3, 3.2, label, 0, 'TEXT')
    def dim_v(self, x, y1, y2, ext_x, label):
        self.line(ext_x, y1, x, y1, 'DIM'); self.line(ext_x, y2, x, y2, 'DIM')
        self.line(x, y1, x, y2, 'DIM'); self.arrow(x, y1, 90); self.arrow(x, y2, -90)
        self.text(x-6, (y1+y2)/2-7, 3.2, label, 90, 'TEXT')
    def center_line(self, x1,y1,x2,y2):
        self.line(x1,y1,x2,y2,'CENTER')
    def hatch_rect(self, x1,y1,x2,y2,step=5):
        t=x1-(y2-y1)
        while t<x2:
            xa=max(x1,t); ya=y1+(xa-t)
            xb=min(x2,t+(y2-y1)); yb=y1+(xb-t)
            self.line(xa,ya,xb,yb,'HATCH')
            t+=step
    def roughness(self, x, y, label, rot=0):
        # simplified surface roughness symbol from lines + ASCII text
        self.line(x,y,x+5,y+8,'SYMBOL'); self.line(x+5,y+8,x+10,y,'SYMBOL')
        self.line(x+10,y,x+28,y,'SYMBOL')
        self.text(x+11,y+2,3.2,label,rot,'TEXT')
    def datum(self, x, y, letter):
        self.poly([(x,y),(x+7,y),(x+7,y+7),(x,y+7)], True, 'DIM')
        self.text(x+2.1,y+1.4,3.2,letter)
    def feature_frame(self, x, y, text):
        parts=text.split('|')
        w=[12,18,28][:len(parts)]
        h=8; xx=x
        for i,p in enumerate(parts):
            self.poly([(xx,y),(xx+w[i],y),(xx+w[i],y+h),(xx,y+h)], True, 'DIM')
            self.text(xx+2,y+2.2,3,p)
            xx += w[i]
    def save(self):
        layers=[('OBJECT',7),('CENTER',4),('DIM',2),('TEXT',7),('HATCH',8),('BORDER',7),('SYMBOL',3)]
        out=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1009','9','$DWGCODEPAGE','3','ANSI_1252','0','ENDSEC',
             '0','SECTION','2','TABLES','0','TABLE','2','LTYPE','70','1','0','LTYPE','2','CONTINUOUS','70','0','3','Solid line','72','65','73','0','40','0.0','0','ENDTAB',
             '0','TABLE','2','LAYER','70',str(len(layers))]
        for name,color in layers:
            out += ['0','LAYER','2',name,'70','0','62',str(color),'6','CONTINUOUS']
        out += ['0','ENDTAB','0','ENDSEC','0','SECTION','2','ENTITIES']
        out += self.entities
        out += ['0','ENDSEC','0','EOF']
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text('\n'.join(out), encoding='ascii')

D=DXF()
# sheet border A3-ish
D.poly([(0,0),(420,0),(420,285),(0,285)], True, 'BORDER')
D.text(7,276,4,'5. Dingjian / Center Point (LJT03.05)')

# main view coordinates: real dimensions approximated 1:1, offset to fit sheet
ox,oy=88,150
cone_tip_x=ox; cone_base_x=ox+35
left_x=cone_base_x; left2_x=left_x+25
flange1_x=left2_x; flange2_x=flange1_x+10
body1_x=flange2_x; body2_x=body1_x+125
sec_x=body2_x-50
# axis
D.center_line(ox-8,oy,body2_x+8,oy)
# cone
D.line(cone_tip_x,oy,cone_base_x,oy+15); D.line(cone_tip_x,oy,cone_base_x,oy-15); D.line(cone_base_x,oy-15,cone_base_x,oy+15)
D.line(cone_tip_x-7,oy,cone_base_x+4,oy,'CENTER')
# 25-long dia60 cylinder
D.poly([(left_x,oy-30),(left2_x,oy-30),(left2_x,oy+30),(left_x,oy+30)], True)
# cross hole
hole_cx=(left_x+left2_x)/2
D.circle(hole_cx,oy,9); D.center_line(hole_cx-14,oy,hole_cx+14,oy); D.center_line(hole_cx,oy-14,hole_cx,oy+14)
# flange and grooves/chamfers
D.poly([(flange1_x,oy-45),(flange2_x,oy-45),(flange2_x,oy+45),(flange1_x,oy+45)], True)
D.line(flange1_x+1,oy-42,flange1_x+1,oy+42); D.line(flange2_x-1,oy-42,flange2_x-1,oy+42)
D.line(left2_x-8,oy-30,left2_x-8,oy-45); D.line(left2_x-8,oy+30,left2_x-8,oy+45)
# taper body
D.line(body1_x,oy-22.366,body2_x,oy-30); D.line(body1_x,oy+22.366,body2_x,oy+30); D.line(body2_x,oy-30,body2_x,oy+30)
# local section break curve and hatching
D.arc(sec_x-8,oy,18,270,90,'OBJECT'); D.line(sec_x,oy-30,body2_x,oy-30); D.line(sec_x,oy+30,body2_x,oy+30); D.line(sec_x,oy-30,sec_x,oy+30)
D.hatch_rect(sec_x,oy-30,body2_x,oy+30,5)
# inner M20-6H hole, depth 40, with left drill cone
D.poly([(sec_x+10,oy-12),(body2_x-5,oy-12),(body2_x-5,oy+12),(sec_x+10,oy+12)], False)
D.line(sec_x+5,oy-8,sec_x+10,oy-12); D.line(sec_x+5,oy+8,sec_x+10,oy+12); D.line(sec_x+5,oy-8,sec_x+5,oy+8)
D.center_line(sec_x+2,oy,body2_x+5,oy)

# dimensions and annotations
D.dim_h(cone_tip_x, body2_x, 55, oy-30, '190')
D.dim_h(body1_x, body2_x, 83, oy-22.366, '125')
D.dim_h(left_x, left2_x, 86, oy-30, '25')
D.dim_h(flange1_x, flange2_x, 86, oy-45, '10')
D.dim_h(sec_x, body2_x, 105, oy-30, '50')
D.dim_h(sec_x+10, body2_x-5, 121, oy-12, '40')
D.dim_v(43, oy-30, oy+30, cone_tip_x-5, '%%c60js6')
D.dim_v(70, oy-15, oy+15, cone_base_x, '%%c30')
D.dim_v(flange2_x+38, oy-45, oy+45, flange2_x+5, '%%c90')
D.dim_v(flange2_x+16, oy-22.366, oy+22.366, body1_x, '%%c44.732')
D.dim_v(body2_x+20, oy-10, oy+10, body2_x, 'M20-6H')
D.text(cone_tip_x+10,oy+20,3.5,'60%%d')
D.text(flange2_x+13,oy-35,3.2,'4x1'); D.text(flange1_x-16,oy-43,3.2,'2x1')
D.text(body1_x+58,oy+42,3.2,'Rest taper 5%%d (1:19.002)')
# roughness and feature control frames
D.roughness(75,222,'Ra1.6'); D.roughness(100,210,'Ra0.8'); D.roughness(194,223,'Ra1.6'); D.roughness(body2_x+16,188,'Ra3.2')
D.feature_frame(75,246,'RUN|0.025|A-B')
D.line(135,246,135,220,'DIM'); D.arrow(135,220,-90,2.5)
D.feature_frame(92,66,'RUN|0.025|C')
D.datum(body1_x+9,oy+39,'A'); D.arrow(body1_x+20,oy+36,-90)
D.datum(left_x-19,oy-36,'B'); D.datum(cone_tip_x-26,oy-37,'C')
D.line(left_x-13,oy-18,left_x-1,oy-8,'DIM'); D.arrow(left_x-1,oy-8,35,2.5)

# lower section view: circle with 18H9 slot and 54 tolerance
cx,cy=116,54; rr=27
D.circle(cx,cy,rr); D.center_line(cx-34,cy,cx+47,cy); D.center_line(cx,cy-34,cx,cy+34)
# clipped hatching by chord approximation
for t in range(-24,29,6):
    x1=cx+t; y1=cy-26
    x2=cx+t+52; y2=cy+26
    D.line(max(cx-26,x1), max(cy-26,y1), min(cx+26,x2), min(cy+26,y2),'HATCH')
# side flat / slot
D.line(cx+24,cy+9,cx+42,cy+9); D.line(cx+24,cy-9,cx+42,cy-9); D.line(cx+42,cy-9,cx+42,cy+9)
D.dim_h(cx-27,cx+27,18,cy-27,'54 0/-0.2')
D.dim_v(cx+55,cy-9,cy+9,cx+42,'18H9')
D.roughness(cx+43,cy+30,'Ra3.2'); D.roughness(cx+50,cy-42,'Ra6.3')

# technical requirements - ASCII pinyin/English to avoid mobile font garbling
rx,ry=318,134
D.text(rx,ry+43,5,'Jishu Yaoqiu / Technical Requirements')
req=[
 '1. Tip quenched, hardness 40-45HRC.',
 '2. Unmarked chamfer C1.',
 '3. Unmarked size tolerance: GB/T 1804-2000-m.',
 '4. Unmarked geometric tolerance: GB/T 1184-1996-K.',
 'Chinese original is documented in README.'
]
for i,s in enumerate(req): D.text(rx-28,ry+27-i*10,3.1,s)
D.roughness(350,82,'Ra12.5')
D.text(382,82,7,'V')

# title block and revision grid
x0,y0=214,0; x1b=420; y1b=70
D.poly([(x0,y0),(x1b,y0),(x1b,y1b),(x0,y1b)], True, 'BORDER')
for y in [15,30,45,70]: D.line(x0,y,x1b,y,'BORDER')
for x in [300,350]: D.line(x,y0,x,y1b,'BORDER')
D.text(316,53,3.5,'Hefei University of Technology')
D.text(327,32,4.5,'Dingjian / Center Point')
D.text(318,10,5,'LJT03.05')
D.text(236,52,6,'45')
# left title/revision grid
for x in range(214,301,12): D.line(x,0,x,70,'BORDER')
for y in range(0,71,10): D.line(214,y,300,y,'BORDER')
D.text(216,43,2.4,'Mark Qty Zone Change Sign Date')
D.text(216,33,2.4,'Design Draw Check Process')
D.text(216,13,2.4,'Stage Mass Scale')
D.text(304,17,2.5,'Sheets  Page')
# small projection symbols
D.poly([(370,8),(380,5),(380,11)], True, 'SYMBOL'); D.line(382,8,392,8,'SYMBOL'); D.circle(399,8,6,'SYMBOL'); D.circle(399,8,2,'SYMBOL'); D.center_line(391,8,407,8); D.center_line(399,0,399,16)

D.save()
print(OUT)
