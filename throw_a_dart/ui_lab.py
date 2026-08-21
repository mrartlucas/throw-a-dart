from __future__ import annotations

import pygame

from throw_a_dart.pixel_ui import draw_centered, draw_right, draw_text

BLACK=(0,0,0)
WHITE=(255,255,255)
INK=(24,21,27)
CREAM=(250,238,199)
GOLD=(255,194,45)
YELLOW=(255,225,88)
TEAL=(32,190,181)
PURPLE=(104,61,151)
DIM=(118,118,118)
PLAYER_BLUE=(58,137,255)
RED=(225,48,52)
GREEN=(62,194,92)

LAB_CHOICES=("FONT LAB","ANIMATION LAB")
FX_NAMES=(
    "COLOR BORDER",
    "CHASE BORDER",
    "TEXT POP",
    "BOUNCE",
    "FLASH INVERT",
    "COLOR PULSE",
    "COMBO",
)
SPEED_NAMES=("SLOW","MED","FAST")
SPEED_DIVISORS=(7,4,2)


def _font(size:int,bold:bool=False):
    font=pygame.font.Font(None,size)
    font.set_bold(bold)
    return font


def _center(surface,text,center_x,y,font,color):
    image=font.render(text,False,color)
    surface.blit(image,(center_x-image.get_width()//2,y))


def _lower_clear(surface,border=PURPLE,fill=INK):
    pygame.draw.rect(surface,fill,(0,128,64,32))
    pygame.draw.rect(surface,border,(0,128,64,32),1)
    pygame.draw.rect(surface,BLACK,(64,128,64,32))


def _phase(tick:int,speed_index:int)->int:
    return tick//SPEED_DIVISORS[speed_index]


def draw_test_lab_menu(surface,choice:int):
    surface.fill(BLACK)
    pygame.draw.rect(surface,INK,(0,0,128,128))
    _center(surface,"THROW A WAY GAMES",64,9,_font(15,True),GOLD)
    _center(surface,"TEST LAB",64,27,_font(23,True),WHITE)
    _center(surface,"CABINET UI TUNING",64,50,_font(12),DIM)

    for index,label in enumerate(LAB_CHOICES):
        y=72+index*23
        selected=index==choice
        if selected:
            pygame.draw.rect(surface,PURPLE,(12,y-3,104,19),1)
        _center(surface,label,64,y,_font(16,selected),TEAL if selected else CREAM)

    _lower_clear(surface,PURPLE)
    draw_centered(surface,"TEST LAB",32,130,CREAM,advance=4)
    draw_centered(surface,"FONT" if choice==0 else "ANIM",32,139,WHITE,sy=2,advance=4)
    draw_text(surface,"L/R",2,153,TEAL,advance=4)
    draw_right(surface,"A GO",61,153,GOLD,advance=4)


def _draw_top_border(surface,color,width=2):
    pygame.draw.rect(surface,color,(0,0,128,128),width)


def _draw_lower_border(surface,color,width=1):
    pygame.draw.rect(surface,color,(0,128,64,32),width)


def _draw_chase(surface,phase:int,color,lower:bool=False):
    if lower:
        x0,y0,w,h=0,128,64,32
        segment=8
        perimeter=2*(w+h)-4
    else:
        x0,y0,w,h=0,0,128,128
        segment=16
        perimeter=2*(w+h)-4
    start=(phase*segment)%perimeter
    for offset in range(0,segment,2):
        p=(start+offset)%perimeter
        if p<w:
            x,y=x0+p,y0
        elif p<w+h-1:
            x,y=x0+w-1,y0+(p-w)+1
        elif p<2*w+h-2:
            x,y=x0+w-2-(p-(w+h-1)),y0+h-1
        else:
            x,y=x0,y0+h-2-(p-(2*w+h-2))
        pygame.draw.rect(surface,color,(x,y,2,2))


def _draw_ready_text(surface,top_color=WHITE,lower_a=WHITE,lower_b=GOLD,top_y=48,lower_shift=0,top_size=27):
    pygame.draw.rect(surface,INK,(15,38,98,48))
    _center(surface,"THROW",64,top_y,_font(top_size,True),top_color)
    _center(surface,"READY",64,top_y+20,_font(top_size,True),top_color)
    draw_centered(surface,"THROW",32,132+lower_shift,lower_a,sx=2,sy=2,advance=7)
    draw_centered(surface,"READY",32,144-lower_shift,lower_b,sx=2,sy=2,advance=7)


def draw_animation_lab(surface,effect_index:int,speed_index:int,tick:int,preview_frames:int):
    phase=_phase(tick,speed_index)
    preview=preview_frames>0

    surface.fill(BLACK)
    top_bg=INK
    lower_bg=INK
    top_fg=WHITE
    lower_a=WHITE
    lower_b=GOLD
    border=PURPLE
    top_y=48
    lower_shift=0
    top_size=27

    if preview:
        if effect_index==0:  # COLOR BORDER
            palette=(PLAYER_BLUE,GOLD,TEAL,WHITE,RED,GREEN)
            border=palette[phase%len(palette)]
        elif effect_index==1:  # CHASE BORDER
            border=DIM
        elif effect_index==2:  # TEXT POP
            intro=max(0,45-preview_frames)
            if intro<6:
                top_size=20
            elif intro<11:
                top_size=34
            else:
                top_size=27
        elif effect_index==3:  # BOUNCE
            lower_shift=(-1,0,1,0)[phase%4]
            top_y=48+(-2,0,2,0)[phase%4]
        elif effect_index==4:  # FLASH INVERT
            inverted=(phase%2)==1
            if inverted:
                top_bg=CREAM
                lower_bg=WHITE
                top_fg=INK
                lower_a=INK
                lower_b=PURPLE
                border=GOLD
            else:
                border=WHITE
        elif effect_index==5:  # COLOR PULSE
            palette=(WHITE,YELLOW,GOLD,TEAL,PLAYER_BLUE)
            top_fg=palette[phase%len(palette)]
            lower_a=top_fg
            lower_b=palette[(phase+2)%len(palette)]
            border=top_fg
        elif effect_index==6:  # COMBO
            palette=(PLAYER_BLUE,GOLD,TEAL,WHITE)
            border=palette[phase%len(palette)]
            top_fg=palette[(phase+1)%len(palette)]
            lower_a=top_fg
            lower_b=palette[(phase+2)%len(palette)]
            intro=max(0,45-preview_frames)
            if intro<5:
                top_size=21
            elif intro<10:
                top_size=33
            else:
                top_size=27

    pygame.draw.rect(surface,top_bg,(0,0,128,128))
    _lower_clear(surface,border,lower_bg)

    _center(surface,"ANIMATION LAB",64,4,_font(15,True),GOLD)
    _center(surface,f"{effect_index+1}/7  {FX_NAMES[effect_index]}",64,19,_font(12,True),TEAL)
    _center(surface,f"SPEED {SPEED_NAMES[speed_index]}",64,30,_font(11),CREAM)

    if preview:
        _draw_ready_text(
            surface,
            top_color=top_fg,
            lower_a=lower_a,
            lower_b=lower_b,
            top_y=top_y,
            lower_shift=lower_shift,
            top_size=top_size,
        )
        if effect_index==1:
            _draw_top_border(surface,PURPLE,1)
            _draw_lower_border(surface,PURPLE,1)
            _draw_chase(surface,phase,GOLD,False)
            _draw_chase(surface,phase,TEAL,True)
        elif effect_index==6:
            _draw_top_border(surface,border,1)
            _draw_lower_border(surface,border,1)
            _draw_chase(surface,phase,GOLD,False)
            _draw_chase(surface,phase+2,TEAL,True)
        else:
            _draw_top_border(surface,border,2)
            _draw_lower_border(surface,border,1)
    else:
        pygame.draw.rect(surface,PURPLE,(10,46,108,46),1)
        _center(surface,"PRESS A",64,55,_font(24,True),WHITE)
        _center(surface,"TO PREVIEW",64,76,_font(14),CREAM)
        draw_centered(surface,"FX TEST",32,130,CREAM,advance=4)
        draw_centered(surface,FX_NAMES[effect_index].split()[0],32,139,WHITE,sy=2,advance=4)

    if preview:
        draw_centered(surface,"READY",32,153,TEAL,advance=4)
    else:
        draw_text(surface,"L/R FX",2,153,TEAL,advance=3)
        draw_right(surface,"U/D SPD",61,153,GOLD,advance=3)

    pygame.draw.rect(surface,BLACK,(64,128,64,32))


def speed_divisor(speed_index:int)->int:
    return SPEED_DIVISORS[speed_index]
