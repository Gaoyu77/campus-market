from pathlib import Path

path = Path(__file__).with_name('index.html')
s = path.read_text(encoding='utf-8')
def replace(old, new):
    global s
    if old not in s:
        raise ValueError('未找到：' + old[:80])
    s = s.replace(old, new, 1)

replace('<main class="wrap">', '''<main class="wrap">
<div class="demo-bar"><label for="demoUser">演示身份</label><select id="demoUser"><option value="demo-gaoyu">小高同学</option><option value="demo-2">小张同学</option></select><button id="myOrders" class="quiet">我的订单</button></div>
<section id="ordersPage" class="mine-page" hidden><div class="item-breadcrumb"><a href="#" class="back-list">← 返回列表</a><span>/</span><span>我的订单</span></div><div class="mine-heading"><div><h1>我的订单</h1><p>买入和卖出的预约记录</p></div></div><div id="orderList"></div></section>''')
replace('</style>', '''.demo-bar {display:flex; align-items:center; gap:12px; padding:12px 0; font-size:13px; border-bottom:1px solid var(--border)}
.demo-bar select {padding:7px; border:1px solid var(--border); background:white; color:var(--text)}
.order-row {padding:20px 0; border-bottom:1px solid var(--border)}
.order-row p {color:var(--muted); margin:8px 0; font-size:13px}
.order-row button {margin-right:8px}
</style>''')
replace("const currentUser = {id:'demo-gaoyu',name:'小高同学'};", "let currentUser = {id:sessionStorage.getItem('marketUser')||'demo-gaoyu',name:''};\nconst names={'demo-gaoyu':'小高同学','demo-2':'小张同学'}; currentUser.name=names[currentUser.id]||names['demo-gaoyu'];")
replace("headers:{'Content-Type':'application/json'},...options", "headers:{'Content-Type':'application/json','X-Demo-User':currentUser.id},...options")
replace("const statusText = p => ({on_sale:'在售',off_shelf:'已下架',sold:'已售出'}[p.status]);", "const statusText = p => ({on_sale:'在售',off_shelf:'已下架',reserved:'已预订',sold:'已售出'}[p.status]);")
replace("['off_shelf','已下架'],['sold','已售出']", "['off_shelf','已下架'],['reserved','已预订'],['sold','已售出']")
replace("p.status==='sold'?'':'<button data-edit", "(p.status==='sold'||p.status==='reserved')?'':'<button data-edit")
replace("if (edit && (!p || !isMine(p) || p.status==='sold'))", "if (edit && (!p || !isMine(p) || p.status==='sold' || p.status==='reserved'))")
replace("$('.detail-header-label').textContent = isMinePage", "const isOrders = location.hash === '#orders';\n  $('.detail-header-label').textContent = isOrders ? '我的订单 · 同学集市' : isMinePage")
replace("isDetail || isPublish || isMinePage);", "isDetail || isPublish || isMinePage || location.hash === '#orders');")
replace("$('#listPage').hidden = isDetail || isPublish || isMinePage;", "$('#listPage').hidden = isDetail || isPublish || isMinePage || isOrders;\n  $('#ordersPage').hidden = !isOrders;")
replace("  if (isMinePage) {\n    renderMine();", "  if (isOrders) { renderOrders(); document.title='我的订单 · 同学集市'; window.scrollTo(0,0);\n  } else if (isMinePage) {\n    $('.mine-account').innerHTML=esc(currentUser.name)+' · 演示账号<span>商品修改会保存在本机数据库。</span>'; renderMine();")
replace("(p.status==='sold'?'商品已售出':isMine(p)?'管理我的闲置':'联系卖家 ↗')", "(p.status==='sold'?'商品已售出':p.status==='reserved'?'商品已预订':isMine(p)?'管理我的闲置':['demo-gaoyu','demo-2'].includes(p.ownerId)?'预约购买':'该示例暂不支持预约')")
replace("(p.status==='sold'?'disabled':'')+'>'", "((p.status==='sold'||p.status==='reserved'||(!isMine(p)&&!['demo-gaoyu','demo-2'].includes(p.ownerId)))?'disabled':'')+'>'")
replace("$('#itemContact').onclick = () => isMine(p) ? navigate('#mine') : toast('这是本地原型，暂不发送真实消息。');", "$('#itemContact').onclick = async () => { if(isMine(p)){navigate('#mine');return;} try {await api('/products/'+p.id+'/reserve',{method:'POST'}); await refreshProducts(); navigate('#orders'); toast('预约成功，可在订单中查看。');} catch(e){toast('预约失败，商品可能已被预订。'); await refreshProducts(); showRoute();} };")
replace("'原型演示：联系按钮不发送消息，收藏仅在本次浏览中保留。'", "'演示交易无需付款，收藏仅在本次浏览中保留。'")
replace("$('#myItems').onclick =", """async function renderOrders(){
  const box=$('#orderList'); box.textContent='正在加载订单…';
  try { const rows=await api('/orders');
    box.innerHTML=rows.length?rows.map(o=>'<article class="order-row"><strong>'+esc(o.title)+'</strong><p>订单号 '+o.id+' · '+(o.buyer_id===currentUser.id?'我买入':'我卖出')+' · ¥'+o.price+' · '+({reserved:'已预订',cancelled:'已取消',completed:'已完成'}[o.status])+'</p><p>买家：'+esc(names[o.buyer_id]||o.buyer_id)+' · 卖家：'+esc(names[o.seller_id]||o.seller_id)+'</p>'+(o.status==='reserved'?'<button class="quiet" data-order="'+o.id+'" data-action="cancel">取消预约</button>'+(o.seller_id===currentUser.id?'<button class="publish" data-order="'+o.id+'" data-action="complete">确认完成</button>':''):'')+'</article>').join(''):'<p>还没有订单。</p>';
  }catch(e){box.textContent='订单加载失败，请检查后端服务。';}
}
$('#orderList').onclick=async e=>{const b=e.target.closest('[data-order]');if(!b)return;b.disabled=true;try{await api('/orders/'+b.dataset.order+'/'+b.dataset.action,{method:'POST'});await refreshProducts();await renderOrders();toast('订单状态已更新。');}catch(e){toast('操作失败，订单可能已经变化。');await renderOrders();}};
$('#demoUser').value=currentUser.id;
$('#demoUser').onchange=async e=>{currentUser={id:e.target.value,name:names[e.target.value]};sessionStorage.setItem('marketUser',currentUser.id);saved.clear();try{await refreshProducts();navigate('#','#',true);render();toast('已切换为'+currentUser.name);}catch(err){toast('切换失败，请检查后端。');}};
$('#myOrders').onclick=()=>navigate('#orders');
$('#myItems').onclick =""")
path.write_text(s,encoding='utf-8')
