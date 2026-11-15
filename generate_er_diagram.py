from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, ElementTree
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

out=Path(__file__).resolve().parent.parent
W,H=1600,1060
tables={
 'users':(70,240,330,['Users · 用户','PK  id : nvarchar(40)','      display_name : nvarchar(50)','      is_demo : bit']),
 'products':(585,240,390,['Products · 商品','PK  id : int','FK  owner_id : nvarchar(40)','      title : nvarchar(45)','      category : nvarchar(30)','      condition : nvarchar(20)','      price : decimal(8,2)','      campus : nvarchar(20)','      description : nvarchar(1000)','      image_data : nvarchar(max) 可空','      status : varchar(12)','      created_at : datetime2(7)']),
 'orders':(1120,240,390,['Orders · 订单','PK  id : int','FK  product_id : int','FK  buyer_id : nvarchar(40)','FK  seller_id : nvarchar(40)','      price : decimal(8,2)','      status : varchar(12)','      created_at : datetime2(7)','      updated_at : datetime2(7)']),
 'favorites':(585,820,390,['Favorites · 收藏','PK, FK  user_id : nvarchar(40)','PK, FK  product_id : int','             created_at : datetime2(7)']),
}
row=32
edges=[
 ('发布',[(400,310),(585,310)],(492,293),'1','0..N'),
 ('对应商品',[(975,330),(1120,330)],(1048,312),'1','0..N'),
 ('买家',[(150,240),(150,75),(1230,75),(1230,240)],(680,57),'1','0..N'),
 ('卖家',[(280,240),(280,135),(1370,135),(1370,240)],(825,117),'1','0..N'),
 ('用户收藏',[(140,368),(140,880),(585,880)],(350,863),'1','0..N'),
 ('商品被收藏',[(780,624),(780,820)],(845,715),'1','0..N'),
]
fig,ax=plt.subplots(figsize=(16,10.6),dpi=150)
plt.rcParams['font.sans-serif']=['Microsoft YaHei','SimHei','DejaVu Sans']
ax.set_xlim(0,W); ax.set_ylim(H,0); ax.axis('off'); fig.patch.set_facecolor('white')
root=Element('mxfile',host='app.diagrams.net'); page=SubElement(root,'diagram',name='E-R 逻辑关系图'); model=SubElement(page,'mxGraphModel',dx=str(W),dy=str(H),page='1',pageWidth=str(W),pageHeight=str(H)); cells=SubElement(model,'root'); SubElement(cells,'mxCell',id='0');SubElement(cells,'mxCell',id='1',parent='0')
def vertex(id,value,x,y,w,h,style):
    c=SubElement(cells,'mxCell',id=id,value=value,style=style,vertex='1',parent='1'); SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),**{'as':'geometry'})
vertex('title','同学集市 · E-R 逻辑关系图',70,5,850,45,'text;html=1;fontSize=24;fontStyle=1;align=left;')
ax.text(70,35,'同学集市 · E-R 逻辑关系图',fontsize=19,weight='bold',va='center',color='#222222')
for key,(x,y,w,lines) in tables.items():
    h=row*len(lines)
    ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='#555555',linewidth=1.1,zorder=3))
    ax.add_patch(Rectangle((x,y),w,row,facecolor='#f2f2f2',edgecolor='#555555',linewidth=1.1,zorder=4))
    vertex(key+'-box','',x,y,w,h,'rounded=0;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#555555;')
    vertex(key+'-heading',lines[0],x,y,w,row,'rounded=0;html=1;fillColor=#f2f2f2;strokeColor=#555555;align=left;spacingLeft=10;fontStyle=1;fontSize=15;')
    ax.text(x+10,y+row/2,lines[0],fontsize=12,weight='bold',va='center',zorder=5)
    for i,line in enumerate(lines[1:],1):
        vertex(key+'-'+str(i),line,x+8,y+i*row,w-16,row,'text;html=1;align=left;fontSize=13;')
        ax.text(x+12,y+i*row+row/2,line,fontsize=9.5,va='center',zorder=5,color='#333333')
for i,(label,points,pos,first,last) in enumerate(edges):
    xs,ys=zip(*points); ax.plot(xs,ys,color='#555555',lw=1.3,zorder=1)
    ax.text(*pos,label,fontsize=10,ha='center',va='center',bbox=dict(facecolor='white',edgecolor='none',pad=2),zorder=6)
    # Cardinalities are explicit labels close to each endpoint.
    a,b=points[0],points[-1]
    if i in (2,3): ax.text(a[0]+10,a[1]-10,first,fontsize=9);ax.text(b[0]+8,b[1]-10,last,fontsize=9)
    elif i==4: ax.text(a[0]+8,a[1]+16,first,fontsize=9);ax.text(b[0]-42,b[1]-8,last,fontsize=9)
    elif i==5: ax.text(a[0]+8,a[1]+16,first,fontsize=9);ax.text(b[0]+8,b[1]-8,last,fontsize=9)
    else: ax.text(a[0]+8,a[1]-8,first,fontsize=9);ax.text(b[0]-38,b[1]-8,last,fontsize=9)
    edge=SubElement(cells,'mxCell',id='edge'+str(i),value='',style='endArrow=none;startArrow=none;strokeColor=#555555;strokeWidth=1.4;html=1;',edge='1',parent='1')
    g=SubElement(edge,'mxGeometry',relative='1',**{'as':'geometry'});SubElement(g,'mxPoint',x=str(a[0]),y=str(a[1]),**{'as':'sourcePoint'});SubElement(g,'mxPoint',x=str(b[0]),y=str(b[1]),**{'as':'targetPoint'})
    if len(points)>2:
        arr=SubElement(g,'Array',**{'as':'points'})
        for x,y in points[1:-1]:SubElement(arr,'mxPoint',x=str(x),y=str(y))
    vertex('label'+str(i),label,pos[0]-50,pos[1]-12,100,24,'text;html=1;align=center;fillColor=#ffffff;fontSize=13;')
    for suffix,point,val in [('a',a,first),('b',b,last)]:
        vertex('card'+str(i)+suffix,val,point[0]+(6 if suffix=='a' else -40),point[1]-25,42,20,'text;html=1;fontSize=12;')
note='PK 主键    FK 外键    1 恰好一个    0..N 零个或多个'
ax.text(70,1010,note,fontsize=10,color='#555555')
vertex('legend',note,70,985,900,35,'text;html=1;align=left;fontSize=13;fontColor=#555555;')
fig.subplots_adjust(left=.01,right=.99,top=.99,bottom=.01)
fig.savefig(out/'课程设计_数据库ER图.png',dpi=150,facecolor='white');plt.close(fig)
ElementTree(root).write(out/'课程设计_数据库ER图.drawio',encoding='utf-8',xml_declaration=True)
