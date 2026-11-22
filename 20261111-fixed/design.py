"""Editable design tokens and step illustrations. Illustrations are conceptual, not device screenshots."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io

TOKENS={'background':'#F5F0E8','surface':'#FFFFFF','ink':'#26364A','muted':'#566272','primary':'#416A93','sky':'#E9F2FA','cream':'#FBF3DC','lavender':'#EDF1FA','radius':15,'touch_height':60,'content_width':1020}

def css(big=False):
    t=TOKENS;size=23 if big else 20
    return f'''<style>
.stApp {{background:{t['background']};color:{t['ink']};}}
.block-container {{max-width:{t['content_width']}px;}}
.stButton>button,.stFormSubmitButton>button {{min-height:{t['touch_height']}px;border-radius:{t['radius']}px;}}
.stButton>button p {{font-size:{size}px!important;}}
.st-key-bottom_nav {{position:sticky;bottom:0;z-index:50;background:#FFFFFFF5;border-top:1px solid #DEE5EC;padding:10px 0 4px;margin-top:24px;}}
.st-key-bottom_nav [data-testid="stHorizontalBlock"] {{flex-wrap:nowrap!important;gap:4px!important;}}
.st-key-bottom_nav [data-testid="stColumn"] {{min-width:0!important;flex:1 1 0!important;}}
.st-key-bottom_nav button {{padding:8px 2px;min-height:58px;border:0;box-shadow:none;background:transparent;}}
.st-key-bottom_nav button p {{font-size:17px!important;font-weight:600!important;}}
.st-key-topbar img {{object-fit:contain;}}
.st-key-topicrows button {{border:0;border-bottom:1px solid #DFE6ED;border-radius:0;background:transparent;box-shadow:none;text-align:left;}}
@media(max-width:600px) {{.st-key-bottom_nav button p {{font-size:14px!important;}}}}
</style>'''

def step_picture(title,step,total):
    """Concept illustration: phone + current step, not fabricated app UI."""
    im=Image.new('RGB',(720,420),'#EDF3F8');d=ImageDraw.Draw(im)
    d.rounded_rectangle((220,24,500,396),radius=30,fill='white',outline='#416A93',width=6)
    d.rounded_rectangle((315,38,405,46),radius=4,fill='#B9C9D8')
    d.ellipse((300,90,420,210),fill='#E9F2FA')
    font=ImageFont.truetype('DejaVuSans.ttf',56)
    d.text((360,150),str(step+1),font=font,anchor='mm',fill='#26364A')
    for i in range(3):d.rounded_rectangle((255,240+i*28,465-(i%2)*50,251+i*28),radius=5,fill='#D5E1ED')
    for i in range(total):
        x=245+i*(230/max(total,1));d.ellipse((x,348,x+12,360),fill='#416A93' if i<=step else '#DEE5EC')
    buf=io.BytesIO();im.save(buf,'PNG');return buf.getvalue()
