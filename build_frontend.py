from pathlib import Path

root = Path(__file__).resolve().parent
source = root.parent / '校园交易平台_合并版_列表原型.html'
html = source.read_text(encoding='utf-8')
start = html.index('let products=[')
end = html.index('const isMine =', start)
html = html[:start] + '''let products=[];
const currentUser = {id:'demo-gaoyu',name:'小高同学'};
const examples = {
  '数据库系统概论 · 第六版':['books','#e7ebe5','小高同学',59],
  '头戴式无线耳机，支持蓝牙连接':['headphones','#e9e8e5','阿木',399],
  '书桌暖光台灯，带原装电源':['lamp','#eee7dc','橙子汽水',89],
  '复古数码相机，含电池和充电器':['camera','#e2e6e8','一颗栗子',650],
  '校园通勤自行车，刹车正常':['bike','#e8eadf','慢慢骑',580],
  '奶油绿机械键盘 · 无线版':['keyboard','#ebeae5','不熬夜选手',249],
  '帆布双肩包，全新未使用':['bag','#e7e4dd','山野来信',129],
  '汪曾祺《人间草木》':['books2','#f1e7db','风吹书页',38]
};
function fromApi(p) {
  const demo=examples[p.title] || ['box','#eee6dc',p.owner_id===currentUser.id?currentUser.name:'示例卖家',null];
  return {id:p.id,ownerId:p.owner_id,title:p.title,cat:p.category,condition:p.condition,campus:p.campus,price:Number(p.price),desc:p.description,photo:p.image_data,status:p.status,time:p.created_at.replace('T',' ').slice(0,16),art:demo[0],bg:demo[1],seller:demo[2],original:demo[3]};
}
async function api(path, options={}) {
  const response=await fetch('/api'+path, {headers:{'Content-Type':'application/json'},...options});
  if (!response.ok) throw new Error('请求失败（'+response.status+'）');
  return response.json();
}
async function refreshProducts() {
  const [visible,own]=await Promise.all([api('/products?include_sold=true'),api('/products?mine=true')]);
  products=[...new Map([...visible,...own].map(p=>[p.id,fromApi(p)])).values()];
}
''' + html[end:]
start=html.index('function toggleListing(id) {')
end=html.index('function prepareForm(p)',start)
html=html[:start]+'''async function toggleListing(id) {
  const p=products.find(p=>p.id===id);
  if(!p || !isMine(p) || p.status==='sold') return;
  try {
    await api('/products/'+id+'/status',{method:'PATCH',body:JSON.stringify({status:p.status==='on_sale'?'off_shelf':'on_sale'})});
    await refreshProducts(); render(); renderMine();
    toast('商品状态已保存。');
  } catch(error) { toast('操作失败，请检查后端服务是否正常。'); }
}
''' + html[end:]
html=html.replace("$('#publishForm').onsubmit = e => {", "$('#publishForm').onsubmit = async e => {")
start=html.index('  if (editingId !== null) {',html.index("$('#publishForm').onsubmit"))
end=html.index('\n};',start)
html=html[:start]+'''  const payload={title,description:desc,category:fields.cat,condition:fields.condition,campus:fields.campus,price:fields.price,image_data:fields.photo||null};
  const button=$('#submitListing'); button.disabled=true;
  try {
    const editing=editingId!==null;
    const result=await api('/products'+(editing?'/'+editingId:''),{method:editing?'PUT':'POST',body:JSON.stringify(payload)});
    await refreshProducts();
    e.target.reset(); clearPhoto(); editingId=null; formMode='publish';
    if(editing){ render(); mineFilter='all'; navigate('#mine','#',true); toast('修改已保存，商品状态保持不变。'); }
    else { reset(true); navigate('#item-'+result.id,history.state?.from||'#',true); toast('发布成功，已保存到数据库。'); }
  } catch(error) { $('#publishError').textContent='保存失败，请检查服务和填写内容后重试。'; }
  finally { button.disabled=false; }
''' + html[end:]
html=html.replace('仅本次浏览保留修改，刷新后恢复示例。','商品修改会保存在本机数据库。')
html=html.replace('仅作本地演示，刷新页面后商品与草稿会清除。','发布后商品保存在本机数据库；未提交的草稿不会保存。')
html=html.replace('Codex × DSH 合并原型 · 商品图为示意插画 · 未连接数据库','本机演示 · 示例商品图为示意插画')
html=html.replace('本次选择的商品照片 · 仅本地预览','商品照片')
html=html.replace('图片只在本页预览。','发布后图片保存在本机数据库。')
html=html.replace('原型不会上传文件。','发布时可不选择照片。')
html=html.replace('商品可能已下架，当前页面发布的示例商品也会在刷新后清除。','商品可能已下架或不存在。')
html=html.replace('nav();\nrender();\nshowRoute();','nav();\nrefreshProducts().then(()=>{render();showRoute();}).catch(()=>{ $(\'#grid\').innerHTML=\'<div class="empty"><h3>无法连接数据库</h3><p>请检查本机后端和 SQL Server 是否启动，然后刷新页面。</p></div>\'; });')
(root / 'index.html').write_text(html,encoding='utf-8')
print('已生成连接数据库的页面。')
