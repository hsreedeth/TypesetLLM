import React, {useEffect, useState} from 'react';
import {AbsoluteFill, continueRender, delayRender, Easing, interpolate, staticFile, useCurrentFrame} from 'remotion';

const ease = Easing.bezier(.22, 1, .36, 1);
const tween = (f: number, a: number, b: number, x: number, y: number) => interpolate(f, [a,b], [x,y], {easing: ease, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
const show = (f: number, at: number) => tween(f, at, at + 15, 0, 1);
const card: React.CSSProperties = {background:'#fffdf9', border:'2px solid #d9d7d1', borderRadius:24, boxShadow:'0 28px 70px rgba(13,38,92,.12)'};
const mono: React.CSSProperties = {fontFamily:'Menlo, Consolas, monospace'};
export const McpDemo: React.FC = () => {
  const f = useCurrentFrame();
  const [fontHandle] = useState(() => delayRender('Loading Inter'));
  useEffect(() => {let active=true; new FontFace('Inter Demo', `url(${staticFile('Inter-Variable.ttf')})`, {weight:'100 900'}).load().then(face => {document.fonts.add(face); if(active) continueRender(fontHandle);}).catch(() => {if(active) continueRender(fontHandle);}); return () => {active=false;};}, [fontHandle]);
  const x=tween(f,0,95,0,-36)+tween(f,165,245,0,-20), y=tween(f,0,95,0,-9)+tween(f,165,245,0,-10), scale=tween(f,0,95,1,1.045)+tween(f,165,245,0,.02);
  const outro=interpolate(f,[255,269],[1,0],{extrapolateLeft:'clamp',extrapolateRight:'clamp'});
  return <AbsoluteFill style={{background:'radial-gradient(circle at 75% 25%, #fff0ca, #f7f6f2 55%)', fontFamily:'Inter Demo, sans-serif', color:'#1c2840', overflow:'hidden'}}>
    <div style={{opacity:outro*tween(f,0,12,0,1)}}>
      <div style={{position:'absolute',left:94,top:67,color:'#092c79',fontSize:28,fontWeight:700}}>TypesetLLM <span style={{fontWeight:400}}>· MCP</span></div>
      <div style={{position:'absolute',right:94,top:73,color:'#687185',fontSize:19}}>Markdown → PDF</div>
      <div style={{position:'absolute',left:90,right:90,top:130,height:2,background:'#092c79'}}/>
      <div style={{position:'absolute',left:160,top:210,width:1690,transform:`translate(${x}px,${y}px) scale(${scale})`,transformOrigin:'left top'}}>
        <div style={{fontSize:48,fontWeight:650,letterSpacing:'-.045em'}}>One command. One prompt. A finished PDF.</div>
        <div style={{display:'flex',gap:34,marginTop:40}}>
          <div style={{width:920}}>
            <div style={{...card,height:240,overflow:'hidden'}}>
              <div style={{height:54,padding:'16px 24px',background:'#f0eee8',borderBottom:'1px solid #dad8d0',fontSize:19,color:'#657086'}}>Terminal <span style={{float:'right'}}>● ● ●</span></div>
              <div style={{padding:'28px 30px',fontSize:25,...mono}}><span style={{color:'#588c73'}}>$ </span><span style={{opacity:show(f,18)}}>codex mcp add typesetllm --url</span><br/><span style={{opacity:show(f,26),color:'#092c79'}}>  https://typesetllm.onrender.com/mcp</span></div>
              <div style={{padding:'0 31px',fontSize:21,color:'#34815b',opacity:show(f,48)}}>✓ TypesetLLM connected</div>
            </div>
            <div style={{...card,marginTop:28,height:275,padding:'27px 30px',overflow:'hidden'}}>
              <div style={{fontSize:20,color:'#6d7786',marginBottom:20}}>Codex</div>
              <div style={{background:'#f4f4f1',borderRadius:18,padding:'20px 24px',fontSize:24,lineHeight:1.4,opacity:show(f,76),transform:`translateY(${tween(f,76,98,20,0)}px)`}}>Use TypesetLLM to convert <b>report.md</b> into a PDF and save it here.</div>
              <div style={{marginTop:18,color:'#092c79',fontSize:21,opacity:show(f,119)}}>↗ convert_markdown_to_pdf</div>
            </div>
            <div style={{...card,marginTop:28,height:110,padding:'24px 30px',opacity:show(f,162),display:'flex',alignItems:'center',gap:20}}><div style={{background:'#dff2e4',borderRadius:16,padding:'12px 16px',color:'#2d7650',fontWeight:700,fontSize:23}}>✓</div><div><b style={{fontSize:23}}>report.pdf saved</b><div style={{fontSize:18,color:'#6e7786',marginTop:4}}>Rendered on TypesetLLM · downloaded by Codex</div></div></div>
          </div>
          <div style={{width:610,height:745,position:'relative'}}>
            <div style={{...card,position:'absolute',inset:0,padding:'32px 35px',background:'#f3f1eb',opacity:show(f,76)}}><div style={{fontSize:18,color:'#667186',marginBottom:26}}>report.md</div><div style={{fontSize:35,fontWeight:650}}>Quarterly report</div><div style={{width:'85%',height:14,background:'#d7d9d8',marginTop:33,borderRadius:7}}/><div style={{width:'93%',height:14,background:'#d7d9d8',marginTop:17,borderRadius:7}}/><div style={{marginTop:49,fontSize:19,...mono,lineHeight:1.8,color:'#535f73'}}>| Metric | Value |<br/>| Growth | 24% |<br/><br/>$E = mc^2$<br/><br/>```python<br/>print('ready')<br/>```</div></div>
            <div style={{...card,position:'absolute',inset:0,padding:'36px 43px',background:'white',opacity:show(f,185),transform:`translateY(${tween(f,185,221,46,0)}px)`,boxShadow:'0 35px 80px rgba(13,38,92,.2)'}}><div style={{fontSize:17,color:'#677185',marginBottom:30}}>report.pdf <span style={{float:'right',color:'#2f8158'}}>✓ PDF</span></div><div style={{fontFamily:'Georgia, serif',fontSize:37,fontWeight:700,color:'#9f3025'}}>Quarterly report</div><div style={{height:2,background:'#9f3025',margin:'20px 0 31px'}}/><div style={{fontFamily:'Georgia, serif',fontSize:20,lineHeight:1.45}}>A polished summary of this quarter’s results, with structured data and technical notes.</div><div style={{marginTop:31,fontFamily:'Georgia, serif',fontSize:24,fontWeight:700}}>Performance</div><div style={{marginTop:11,display:'grid',gridTemplateColumns:'1fr 1fr',fontFamily:'Georgia, serif',fontSize:19,borderTop:'2px solid #a32e25',borderBottom:'1px solid #d4c9bd'}}><span style={{padding:13,fontWeight:700}}>Metric</span><span style={{padding:13,fontWeight:700}}>Value</span><span style={{padding:13,borderTop:'1px solid #ddd7cf'}}>Growth</span><span style={{padding:13,borderTop:'1px solid #ddd7cf'}}>24%</span></div><div style={{marginTop:29,textAlign:'center',fontFamily:'Georgia, serif',fontSize:28,fontStyle:'italic'}}>E = mc²</div><div style={{marginTop:30,borderLeft:'4px solid #a32e25',background:'#f5f4f0',padding:'15px 21px',...mono,fontSize:17,color:'#394b5c'}}>print('ready')</div></div>
          </div>
        </div>
      </div>
      <div style={{position:'absolute',left:92,bottom:42,color:'#6d7786',fontSize:18}}>Connect → ask → download</div>
    </div>
  </AbsoluteFill>;
};
