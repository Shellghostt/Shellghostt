#!/usr/bin/env python3
"""Generate a full-color vector logo footer; Python standard library only."""
from html import escape
from pathlib import Path
import argparse
import json
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'Assets'/'profile'
ET.register_namespace('', 'http://www.w3.org/2000/svg')
CYCLE=14.0


def text(x,y,value,size=12,cls='name',anchor='middle'):
    return f'<text x="{x:g}" y="{y:g}" class="{cls}" text-anchor="{anchor}" font-size="{size}">{escape(value)}</text>'


def vector(icon,size):
    """Keep paths, colors, transforms and gradients from the source SVG."""
    root=ET.fromstring(icon['svg'])
    for key in ('width','height','style','class','role','aria-labelledby'):
        root.attrib.pop(key,None)
    root.set('width',str(size));root.set('height',str(size))
    ids={e.get('id'):icon['id']+'-'+e.get('id') for e in root.iter() if e.get('id')}
    for node in root.iter():
        for key,value in list(node.attrib.items()):
            if key=='id':node.set(key,ids[value])
            else:
                for old,new in ids.items():
                    value=value.replace('url(#'+old+')','url(#'+new+')')
                    if value=='#'+old:value='#'+new
                node.set(key,value)
    return ET.tostring(root,encoding='unicode')


def underline_opacity(t,index):
    phase=((t-index*2)%CYCLE)/CYCLE
    keys=((0,1),(.10,1),(.143,0),(.95,0),(1,1))
    for (t0,v0),(t1,v1) in zip(keys,keys[1:]):
        if t0<=phase<=t1:return v0+(v1-v0)*(phase-t0)/(t1-t0)
    return 0


def build(mobile=False,frame=None):
    icons=json.loads((ART/'toolbox-logos.json').read_text())
    w,h=(420,328) if mobile else (850,202)
    parts=[text(w/2,25,'TOOLBOX',10,'heading'),
           f'<path class="rule" d="M22 21H{w/2-65:g}M{w/2+65:g} 21H{w-22}"/>']
    css=[]
    for i,icon in enumerate(icons):
        size=56 if mobile else 64
        if icon['id']=='linux':size+=8
        if mobile:
            row=0 if i<4 else 1;col=i if row==0 else i-4
            cx=(57+102*col) if row==0 else (108+102*col)
            cy=88+row*130;label_y=140+row*130
        else:cx=80+i*115;cy=99;label_y=159
        x=cx-size/2;y=cy-size/2
        cls='logo ink' if icon['monochrome'] else 'logo'
        parts += [f'<g class="{cls}" id="brand-{icon["id"]}">',
                  f'<g transform="translate({x:g} {y:g})"><g class="float f{i}">',
                  vector(icon,size),'</g></g>',text(cx,label_y,icon['label'],11 if mobile else 12),
                  f'<path class="underline u{i}" d="M{cx-9:g} {label_y+15:g}h18"/>','</g>']
        css += [f'.f{i}{{animation-delay:{-i*.6:g}s}}',f'.u{i}{{animation-delay:{i*2-CYCLE:g}s}}']
        if frame is not None:
            phase=((frame+i*.6)/7)%1
            dy=-3*(1-abs(phase*2-1))
            css += [f'.f{i}{{animation:none;transform:translateY({dy:.4f}px)}}',
                    f'.u{i}{{animation:none;opacity:{underline_opacity(frame,i):.4f}}}']
    parts.append(text(w/2,318 if mobile else 199,'BUILD. COMMIT. REPEAT.',9,'signature'))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc">
<title id="title">Claude, Codex, GitHub, GitLab, Git, Arch Linux and Linux</title>
<desc id="desc">Original vector shapes and full-color artwork with a slow float and a small travelling underline. The logos remain at full opacity. Reduced-motion preferences disable the movement.</desc>
<style>
text{{font-family:ui-monospace,'DejaVu Sans Mono',Consolas,monospace;font-weight:400}}
.heading{{fill:#a0a8b2;letter-spacing:3px}}.name{{fill:#e6edf3;letter-spacing:.6px}}.signature{{fill:#68737d;letter-spacing:1.7px}}.rule{{fill:none;stroke:#29313a}}.ink{{color:#f5f5f5}}
.underline{{fill:none;stroke:#a7c9aa;stroke-width:1.5;opacity:0;animation:underline 14s linear infinite}}
.float{{animation:float 7s linear infinite}}
@keyframes float{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}
@keyframes underline{{0%,10%{{opacity:1}}14.3%,95%{{opacity:0}}100%{{opacity:1}}}}
@media(prefers-color-scheme:light){{.heading{{fill:#64707a}}.name{{fill:#24292f}}.signature{{fill:#78838b}}.rule{{stroke:#d8dee4}}.ink{{color:#181717}}.underline{{stroke:#526d5b}}}}
{''.join(css)}
@media(prefers-reduced-motion:reduce){{.float,.underline{{animation:none;transform:none}}.underline{{opacity:0}}}}
</style>
{''.join(parts)}
</svg>
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frame',type=float,help='Static animation time for previews')
    p.add_argument('--output',type=Path,help='Preview directory; defaults to Assets/profile')
    args=p.parse_args();out=args.output or ART;out.mkdir(parents=True,exist_ok=True)
    for mobile in (False,True):
        suffix='-mobile' if mobile else ''
        dest=out/f'toolbox-footer{suffix}.svg'
        dest.write_text(build(mobile,args.frame),encoding='utf-8');print(dest)


if __name__=='__main__':main()
