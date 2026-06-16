from pathlib import Path

OUT = Path('cad/LJT03.05_顶尖_还原工程图.dxf')

class DXF:
    def __init__(self):
        self.e=[]
    def add(self,*codes):
        self.e.extend(codes)
    def line(self,x1,y1,x2,y2,layer='OBJECT'):
        self.add('0','LINE','8',layer,'10',x1,'20',y1,'30',0,'11',x2,'21',y2,'31',0)
    def circle(self,x,y,r,layer='OBJECT'):
        self.add('0','CIRCLE','8',layer,'10',x,'20',y,'30',0,'40',r)
    def arc(self,x,y,r,a1,a2,layer='OBJECT'):
        self.add('0','ARC','8',layer,'10',x,'20',y,'30',0,'40',r,'50',a1,'51',a2)
    def text(self,x,y,h,s,rot=0,layer='TEXT'):
        self.add('0','TEXT','8',layer,'10',x,'20',y,'30',0,'40',h,'1',s,'50',rot,'7','STANDARD')
    def dim_arrow(self,x,y,ang,layer='DIM'):
        import math
        l=2.5; w=1.0
        a=math.radians(ang)
        bx=x-l*math.cos(a); by=y-l*math.sin(a)
        px=-math.sin(a); py=math.cos(a)
        self.line(x,y,bx+w*px,by+w*py,layer); self.line(x,y,bx-w*px,by-w*py,layer)
    def hatch(self,x1,y1,x2,y2,spacing=5,layer='HATCH'):
        # simple 45-degree hatch clipped approximately to rectangle
        k=0
        while x1+k < x2+(y2-y1):
            xa=x1+k; ya=y1
            xb=x1+k-(y2-y1); yb=y2
            xa=max(xa,x1); xb=max(xb,x1)
            if xa<=x2 and xb<=x2: self.line(xa,ya,xb,yb,layer)
            k += spacing
    def save(self,path):
        header=['0','SECTION','2','HEADER','9','$ACADVER','1','AC1009','0','ENDSEC','0','SECTION','2','TABLES','0','TABLE','2','LAYER','70','6']
        layers=[('OBJECT',7),('CENTER',4),('DIM',2),('TEXT',7),('HATCH',8),('BORDER',7)]
        for name,color in layers:
            header += ['0','LAYER','2',name,'70','0','62',str(color),'6','CONTINUOUS']
        header += ['0','ENDTAB','0','ENDSEC','0','SECTION','2','ENTITIES']
        data=[]
        for v in header+self.e+['0','ENDSEC','0','EOF']:
            data.append(str(v))
        path.write_text('\n'.join(data),encoding='utf-8')

d=DXF()
# Border and title
for off in (0,): d.line(0,0,420,0,'BORDER'); d.line(420,0,420,285,'BORDER'); d.line(420,285,0,285,'BORDER'); d.line(0,285,0,0,'BORDER')
d.text(6,277,4,'5. 顶尖（LJT03.05）')
# Main axis and part layout scaled 1:1-ish, offset
ox,oy=90,150
axis_y=oy
d.line(ox-10,axis_y,ox+220,axis_y,'CENTER')
# 60 deg cone and shank shoulder/flange/body
cone_tip=(ox,axis_y); cone_base_x=ox+35; cone_r=15
for sx in [1,-1]: d.line(cone_tip[0],cone_tip[1],cone_base_x,axis_y+sx*cone_r,'OBJECT')
d.line(cone_base_x,axis_y-cone_r,cone_base_x,axis_y+cone_r,'OBJECT')
# left cylinder block 25 long dia 60
x1=cone_base_x; x2=x1+25; r=30
d.line(x1,axis_y-r,x2,axis_y-r); d.line(x1,axis_y+r,x2,axis_y+r); d.line(x2,axis_y-r,x2,axis_y+r); d.line(x1,axis_y-r,x1,axis_y+r)
# cross hole circle
d.circle((x1+x2)/2,axis_y,9); d.line((x1+x2)/2-14,axis_y,(x1+x2)/2+14,axis_y,'CENTER'); d.line((x1+x2)/2,axis_y-14,(x1+x2)/2,axis_y+14,'CENTER')
# flange 10 long dia 90
xf1=x2; xf2=xf1+10; rf=45
d.line(xf1,axis_y-rf,xf2,axis_y-rf); d.line(xf1,axis_y+rf,xf2,axis_y+rf); d.line(xf1,axis_y-rf,xf1,axis_y+rf); d.line(xf2,axis_y-rf,xf2,axis_y+rf)
# taper body to right 125 long, dia 44.732 at left to dia 60 at right
xb1=xf2; xb2=xb1+125; r1=22.366; r2=30
d.line(xb1,axis_y-r1,xb2,axis_y-r2); d.line(xb1,axis_y+r1,xb2,axis_y+r2); d.line(xb2,axis_y-r2,xb2,axis_y+r2)
# sectioned right end and internal thread/hole
sec_x=xb2-50; d.line(sec_x,axis_y-r2,sec_x,axis_y+r2); d.hatch(sec_x,axis_y-r2,xb2,axis_y+r2,4)
d.line(sec_x+10,axis_y-12,xb2-5,axis_y-12); d.line(sec_x+10,axis_y+12,xb2-5,axis_y+12); d.line(sec_x+10,axis_y-12,sec_x+10,axis_y+12); d.line(xb2-5,axis_y-12,xb2-5,axis_y+12)
d.line(sec_x+5,axis_y-8,sec_x+10,axis_y-12); d.line(sec_x+5,axis_y+8,sec_x+10,axis_y+12); d.line(sec_x+5,axis_y-8,sec_x+5,axis_y+8)
# dimensions labels
d.text(ox+5,axis_y+20,4,'60°'); d.text(ox-22,axis_y+34,4,'φ30',90); d.text(ox-58,axis_y+40,4,'φ60js6',90)
d.text(x1+8,axis_y-57,4,'25'); d.text(xf1+2,axis_y-57,4,'10'); d.text(xb1+62,axis_y-57,4,'125'); d.text(ox+100,axis_y-83,4,'190')
d.text(xf2+14,axis_y+33,4,'φ44.732',90); d.text(xf2+28,axis_y+38,4,'φ90',90); d.text(xf2+70,axis_y+48,4,'其余锥度 5° (1:19.002)')
d.text(xb2-26,axis_y-27,4,'40'); d.text(sec_x+18,axis_y-39,4,'50'); d.text(xb2+8,axis_y+9,4,'M20-6H',90)
# GD&T/surface text approximations
d.text(76,245,4,'↗  0.025   A-B'); d.text(78,226,4,'Ra1.6'); d.text(105,213,4,'Ra0.8'); d.text(135,254,4,'Ra1.6',90)
d.text(xf2+10,axis_y+45,4,'A'); d.text(ox+32,axis_y-30,4,'B'); d.text(ox-30,axis_y-42,4,'C')
d.text(100,85,4,'↗  0.025   C')
d.text(xb2-18,axis_y+58,4,'Ra1.6'); d.text(xb2+12,axis_y+28,4,'Ra3.2',90)
# Lower section view
cx,cy=115,55; rr=27
d.circle(cx,cy,rr); d.hatch(cx-rr,cy-rr,cx+rr,cy+rr,4); d.line(cx-rr-5,cy,cx+rr+5,cy,'CENTER'); d.line(cx,cy-rr-5,cx,cy+rr+5,'CENTER')
d.line(cx+rr-4,cy+9,cx+rr+14,cy+9); d.line(cx+rr-4,cy-9,cx+rr+14,cy-9); d.line(cx+rr+14,cy-9,cx+rr+14,cy+9)
d.text(cx-20,cy-42,4,'54  0/-0.2'); d.text(cx+34,cy-2,4,'18H9',90); d.text(cx+34,cy+28,4,'Ra3.2',90); d.text(cx+48,cy-32,4,'Ra6.3')
# Technical requirements
rx,ry=332,128
d.text(rx,ry+50,5,'技术要求')
d.text(rx-35,ry+34,3.5,'1. 顶尖端部淬火，硬度为40～45HRC。')
d.text(rx-35,ry+22,3.5,'2. 未注倒角C1。')
d.text(rx-35,ry+10,3.5,'3. 未注尺寸公差按GB/T 1804-2000-m。')
d.text(rx-35,ry-2,3.5,'4. 未注几何公差按GB/T 1184-1996-K。')
# Title block simplified
x0,y0=215,0; w,h=205,70
for yy in [0,15,30,45,70]: d.line(x0,y0+yy,x0+w,y0+yy,'BORDER')
for xx in [x0,300,350,420]: d.line(xx,y0,xx,y0+h,'BORDER')
d.text(320,52,4,'合肥工业大学'); d.text(325,31,5,'顶尖'); d.text(317,10,5,'LJT03.05'); d.text(238,52,6,'45')
# revision table left
d.line(215,0,300,0,'BORDER');
for i in range(7): d.line(215+i*12,0,215+i*12,70,'BORDER')
for yy in range(0,71,10): d.line(215,yy,300,yy,'BORDER')
d.text(217,43,2.8,'标记 处数 分区 更改文件号 签名 年月日')
d.text(217,26,2.8,'设计  制图  审核  工艺')
# general roughness
d.text(360,86,4,'Ra12.5  √')
OUT.parent.mkdir(exist_ok=True)
d.save(OUT)
print(OUT)
