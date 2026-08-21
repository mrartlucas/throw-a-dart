from __future__ import annotations

import time

import numpy as np
import pygame
from pydartsnut import Dartsnut

from throw_a_dart.audio_ui import ArcadeAudio
from throw_a_dart.game_state import SHOWS, PLAYER_COLORS, TEST_MODE, READY_HOLD_FRAMES, CircusGameState, Phase
from throw_a_dart.pixel_ui import draw_centered, draw_text, draw_right, draw_chevron, draw_up_marker
from throw_a_dart.semantic_darts import DartSample, SemanticDartTracker
from throw_a_dart.target_engine import TargetBehavior, TargetField
from throw_a_dart.ui_lab import FX_NAMES, SPEED_NAMES, draw_animation_lab, draw_test_lab_menu

WIDTH, HEIGHT, PLAY_H = 128, 160, 128
FPS = 30
BLACK=(0,0,0); CREAM=(250,238,199); RED=(225,48,52); DARK_RED=(111,19,31); GOLD=(255,194,45)
YELLOW=(255,225,88); TEAL=(32,190,181); BLUE=(55,137,217); DARK_BLUE=(20,46,79); PURPLE=(104,61,151)
BROWN=(116,63,35); INK=(24,21,27); WHITE=(255,255,255); DIM=(118,118,118)

FONT_LAB_OPTIONS=(
    ("PIXEL","pixel",0,False),
    ("DEFAULT","pygame",10,False),
    ("DEFAULT BOLD","pygame",10,True),
    ("LARGE DEFAULT","pygame",11,False),
)


def submit(engine,surface):
    frame=np.transpose(pygame.surfarray.array3d(surface),(1,0,2))
    engine.update_frame_buffer(frame)


def protect_lower(surface):
    pygame.draw.rect(surface,BLACK,(64,128,64,32))


def lower_clear(surface,border=PURPLE):
    pygame.draw.rect(surface,INK,(0,128,64,32))
    pygame.draw.rect(surface,border,(0,128,64,32),1)


def loading(engine,surface,progress):
    surface.fill(BLACK)
    pygame.draw.rect(surface,DARK_BLUE,(0,0,128,128))
    for y in range(0,128,16):
        pygame.draw.polygon(surface,DARK_RED if (y//16)%2==0 else PURPLE,((0,y),(64,y+18),(128,y),(128,y+8),(64,y+26),(0,y+8)))
    pygame.draw.rect(surface,INK,(8,46,112,38))
    font=pygame.font.Font(None,17)
    title=font.render('THROW A DART',False,GOLD)
    surface.blit(title,(64-title.get_width()//2,51))
    pygame.draw.rect(surface,WHITE,(13,94,102,8),1)
    pygame.draw.rect(surface,TEAL,(15,96,int(98*progress),4))
    lower_clear(surface,PURPLE)
    draw_centered(surface,'LOADING',32,131,CREAM)
    pygame.draw.rect(surface,WHITE,(5,146,54,6),1)
    pygame.draw.rect(surface,TEAL,(7,148,int(50*progress),2))
    protect_lower(surface)
    submit(engine,surface)


def bg(surface,tick):
    pygame.draw.rect(surface,CREAM,(0,0,128,128))
    pygame.draw.rect(surface,DARK_RED,(0,0,128,17))
    for x in range(-16,144,24):
        pygame.draw.polygon(surface,RED,((x,0),(x+12,0),(x+25,17),(x+12,17)))
    pygame.draw.line(surface,GOLD,(0,17),(127,17),2)
    pygame.draw.rect(surface,(241,219,171),(0,19,128,88))
    for y in (35,53,71,89):
        pygame.draw.line(surface,(220,193,145),(0,y),(127,y),1)
    pygame.draw.rect(surface,BROWN,(0,107,128,21))
    for x in range(0,128,16):
        pygame.draw.line(surface,(82,43,27),(x,107),(x,127),1)
    for x in range(5,128,12):
        pygame.draw.circle(surface,YELLOW if ((tick//12)+x//12)%2 else WHITE,(x,20),1)


def draw_target(surface,target,tiny):
    if not target.visible or target.hit:
        return
    x,y,r=int(target.x),int(target.y),target.radius
    if target.behavior is TargetBehavior.RISING:
        col=GOLD if target.value>=75 else (244,73,83) if target.value<=50 else (70,154,240)
        pygame.draw.ellipse(surface,INK,(x-r-1,y-r-2,(r+1)*2,(r+2)*2))
        pygame.draw.ellipse(surface,col,(x-r,y-r-1,r*2,(r+1)*2))
        pygame.draw.polygon(surface,col,((x-2,y+r-1),(x+2,y+r-1),(x,y+r+4)))
    elif target.behavior is TargetBehavior.POPUP:
        pygame.draw.rect(surface,BROWN,(x-r-3,y+r-2,(r+3)*2,5))
        pygame.draw.circle(surface,INK,(x,y),r+2)
        pygame.draw.circle(surface,CREAM,(x,y),r)
        pygame.draw.circle(surface,RED,(x,y+1),3)
        pygame.draw.circle(surface,BLUE,(x-4,y-3),1)
        pygame.draw.circle(surface,BLUE,(x+4,y-3),1)
    else:
        pygame.draw.circle(surface,INK,(x,y),r+2)
        pygame.draw.circle(surface,CREAM,(x,y),r)
        pygame.draw.circle(surface,RED,(x,y),max(3,r-3))
        pygame.draw.circle(surface,WHITE,(x,y),max(2,r-7))
        pygame.draw.circle(surface,GOLD,(x,y),max(2,r-9))
    if target.behavior is not TargetBehavior.POPUP:
        image=tiny.render(str(target.value),False,INK)
        surface.blit(image,(x-image.get_width()//2,y-4))


def draw_impact(surface,impact):
    x,y=int(impact.x),int(impact.y)
    if impact.hit:
        radius=3+impact.age//2
        color=WHITE if impact.age<3 else GOLD
        pygame.draw.circle(surface,color,(x,y),radius,1)
        if impact.age<7:
            arm=4+impact.age
            pygame.draw.line(surface,color,(x-arm,y),(x-2,y),1)
            pygame.draw.line(surface,color,(x+2,y),(x+arm,y),1)
            pygame.draw.line(surface,color,(x,y-arm),(x,y-2),1)
            pygame.draw.line(surface,color,(x,y+2),(x,y+arm),1)
    else:
        arm=3+min(4,impact.age//2)
        pygame.draw.line(surface,RED,(x-arm,y-arm),(x+arm,y+arm),1)
        pygame.draw.line(surface,RED,(x+arm,y-arm),(x-arm,y+arm),1)


def read_samples(rows):
    return tuple(DartSample(int(i),int(x),int(y)) for i,x,y in rows if 0<=int(x)<128 and 0<=int(y)<128)


def draw_main_title(surface,title_font):
    pygame.draw.rect(surface,INK,(8,29,112,69))
    image=title_font.render('BULLSEYE',False,GOLD)
    surface.blit(image,(64-image.get_width()//2,34))
    small=pygame.font.Font(None,17)
    image=small.render('BIG TOP CIRCUS',False,CREAM)
    surface.blit(image,(64-image.get_width()//2,56))
    if TEST_MODE:
        image=pygame.font.Font(None,12).render('TEST - ALL UNLOCKED',False,TEAL)
        surface.blit(image,(64-image.get_width()//2,80))


def draw_star_icon(surface,x,y,filled):
    color=GOLD if filled else DIM
    pygame.draw.rect(surface,color,(x+1,y,1,1)); pygame.draw.rect(surface,color,(x,y+1,3,1)); pygame.draw.rect(surface,color,(x+1,y+2,1,1))


def draw_dart_icon(surface,x,y,active,color):
    ink=color if active else DIM
    pygame.draw.line(surface,ink,(x,y),(x+2,y+2),1); pygame.draw.line(surface,ink,(x+2,y+2),(x+3,y+2),1); pygame.draw.rect(surface,ink,(x,y+1,1,2))


def live_stars(game):
    return game.stars_for_hits(game.hits_by_player[game.current_player],game.throws_per_act)


def draw_show_menu(surface,game):
    lower_clear(surface,PURPLE)
    draw_centered(surface,'SHOWS',32,130,PURPLE,advance=4)
    draw_centered(surface,game.selected_show_spec.menu_name,32,139,WHITE,sy=2,advance=4)
    draw_chevron(surface,2,142,TEAL,False); draw_chevron(surface,59,142,TEAL,True)
    draw_text(surface,'A NEXT',3,153,TEAL,advance=4)
    if TEST_MODE: draw_right(surface,'B LAB',60,153,DIM,advance=4)


def draw_act_menu(surface,game):
    lower_clear(surface,PURPLE)
    draw_centered(surface,'ACTS',32,130,PURPLE)
    draw_centered(surface,game.selected_act_spec.menu_name,32,139,WHITE,advance=4)
    draw_chevron(surface,2,141,TEAL,False); draw_chevron(surface,59,141,TEAL,True)
    for i in range(3): draw_star_icon(surface,25+i*7,147,i<game.stars_for_selected())
    draw_text(surface,'A NEXT',3,153,TEAL,advance=4); draw_right(surface,'B BACK',60,153,TEAL,advance=4)


def draw_player_menu(surface,game):
    lower_clear(surface,PURPLE); draw_centered(surface,'PLAYERS',32,130,CREAM)
    xs=(8,23,38,53)
    for index,x in enumerate(xs):
        draw_centered(surface,str(index+1),x,138,YELLOW if index+1==game.player_count else WHITE,sx=1,sy=2)
    draw_up_marker(surface,xs[game.player_count-1],149,YELLOW)
    draw_text(surface,'A START',3,153,TEAL,advance=4); draw_right(surface,'B BACK',60,153,TEAL,advance=4)


def ready_border_color(tick,player_color):
    palette=(player_color,GOLD,TEAL,WHITE)
    return palette[(tick//4)%len(palette)]


def draw_ready_main_border(surface,game,tick):
    color=ready_border_color(tick,PLAYER_COLORS[game.current_player])
    pygame.draw.rect(surface,color,(0,0,128,128),2)
    accent=GOLD if (tick//3)%2==0 else WHITE
    for x,y in ((2,2),(119,2),(2,119),(119,119)):
        pygame.draw.rect(surface,accent,(x,y,7,2)); pygame.draw.rect(surface,accent,(x,y,2,7))


def draw_throw_ready(surface,game,tick):
    player_color=PLAYER_COLORS[game.current_player]
    lower_clear(surface,ready_border_color(tick,player_color)); pygame.draw.rect(surface,player_color,(2,130,60,28),1)
    bounce=(tick//3)%2
    draw_centered(surface,'THROW',32,132+bounce,WHITE if (tick//4)%2==0 else YELLOW,sx=2,sy=2,advance=7)
    draw_centered(surface,'READY',32,144-bounce,GOLD if (tick//4)%2==0 else TEAL,sx=2,sy=2,advance=7)


def draw_game_status(surface,game):
    color=PLAYER_COLORS[game.current_player]; lower_clear(surface,color)
    stars=live_stars(game)
    for i in range(3): draw_star_icon(surface,2+i*5,130,i<stars)
    draw_centered(surface,f'ACT {game.act_index+1}',32,130,CREAM,advance=3)
    used=game.throws_per_act-game.throws_remaining()
    for i in range(game.throws_per_act): draw_dart_icon(surface,44+i*4,130,i>=used,color)
    draw_centered(surface,f'{game.scores[game.current_player]:04d}',32,138,WHITE,sx=2,sy=2,advance=8)
    multiplier=1+min(game.combo[game.current_player],2) if game.combo[game.current_player] else 1
    draw_text(surface,f'P{game.current_player+1}',2,153,color,advance=4); draw_right(surface,f'X{multiplier}',61,153,GOLD,advance=4)


def draw_result_callout(surface,game):
    color=PLAYER_COLORS[game.last_player]; lower_clear(surface,color); draw_text(surface,f'P{game.last_player+1}',2,130,color)
    if game.last_points:
        draw_centered(surface,'HIT',32,136,TEAL,sx=2,sy=2,advance=7); draw_centered(surface,f'+{game.last_points}',32,149,GOLD)
    else:
        draw_centered(surface,'MISS',32,140,RED,sx=2,sy=2,advance=7)


def pygame_font(size,bold=False):
    font=pygame.font.Font(None,size); font.set_bold(bold); return font


def blit_center(surface,text,center_x,y,font,color):
    image=font.render(text,False,color); surface.blit(image,(center_x-image.get_width()//2,y))


def draw_lab_system_text(surface,choice,row,text,y,color,center=32):
    _,kind,base,bold=FONT_LAB_OPTIONS[choice]
    if kind=='pixel':
        draw_centered(surface,text,center,y,color,sx=2 if row=='middle' else 1,sy=2 if row=='middle' else 1,advance=8 if row=='middle' else 4)
    else:
        blit_center(surface,text,center,y,pygame_font(base+8 if row=='middle' else base,bold),color)


def draw_font_lab(surface,choice,tick,ready_frames):
    surface.fill(BLACK); pygame.draw.rect(surface,INK,(0,0,128,128))
    blit_center(surface,'UI FONT LAB',64,4,pygame_font(15,True),GOLD); blit_center(surface,'UI ONLY - TITLES USE ART',64,17,pygame_font(10),DIM)
    ys=(30,52,75,98)
    for index,(name,kind,base,bold) in enumerate(FONT_LAB_OPTIONS):
        selected=index==choice; color=TEAL if selected else CREAM
        if selected: pygame.draw.rect(surface,PURPLE,(3,ys[index]-2,122,20),1)
        label=pygame_font(9,True).render(f'{index+1} {name}',False,color); surface.blit(label,(7,ys[index]))
        if kind=='pixel': draw_text(surface,'ABC 123 SCORE',7,ys[index]+9,WHITE,advance=4)
        else: surface.blit(pygame_font(base+2,bold).render('ABC 123 SCORE',False,WHITE),(7,ys[index]+8))
    if ready_frames>0:
        border=ready_border_color(tick,TEAL); pygame.draw.rect(surface,border,(0,0,128,128),2); pygame.draw.rect(surface,INK,(17,48,94,34))
        _,kind,base,bold=FONT_LAB_OPTIONS[choice]
        if kind=='pixel': draw_centered(surface,'THROW READY',64,59,WHITE,sx=2,sy=2,advance=7)
        else: blit_center(surface,'THROW READY',64,56,pygame_font(base+11,bold),WHITE)
    lower_clear(surface,ready_border_color(tick,TEAL) if ready_frames>0 else PURPLE)
    if ready_frames>0:
        draw_lab_system_text(surface,choice,'small','THROW',133,WHITE); draw_lab_system_text(surface,choice,'middle','READY',140,GOLD)
    else:
        draw_lab_system_text(surface,choice,'small','SHOWS',130,CREAM); draw_lab_system_text(surface,choice,'middle','0425',138,WHITE)
        draw_text(surface,'L/R',2,153,TEAL,advance=4); draw_right(surface,'A READY',61,153,GOLD,advance=4)
    protect_lower(surface)


def draw_result(surface,game):
    winner=game.winner(); stars=game.result_stars
    pygame.draw.rect(surface,INK,(10,28,108,74))
    label=pygame_font(27).render('SHOW OVER!',False,GOLD); surface.blit(label,(64-label.get_width()//2,31))
    label=pygame_font(20).render(f'P{winner+1} WINS',False,PLAYER_COLORS[winner]); surface.blit(label,(64-label.get_width()//2,58))
    label=pygame_font(22).render(str(game.scores[winner]),False,WHITE); surface.blit(label,(64-label.get_width()//2,77))
    for i in range(3): pygame.draw.circle(surface,GOLD if i<stars else DIM,(54+i*10,92),3,0 if i<stars else 1)
    lower_clear(surface,PLAYER_COLORS[winner]); draw_centered(surface,'RESULT',32,130,CREAM,advance=4)
    draw_centered(surface,f'{game.scores[winner]:04d}',32,138,WHITE,sx=2,sy=2,advance=8)
    draw_text(surface,'A AGAIN',3,153,TEAL,advance=4); draw_right(surface,'B MENU',60,153,TEAL,advance=4)


def main():
    pygame.mixer.pre_init(22050,-16,1,256); pygame.init()
    engine=Dartsnut(); pygame.display.set_mode((128,160)); surface=pygame.Surface((128,160)); clock=pygame.time.Clock()
    title_font=pygame.font.Font(None,23); tiny=pygame.font.Font(None,10); audio=ArcadeAudio()
    for progress in (.08,.2,.34,.49,.63,.78,.9,1.0): loading(engine,surface,progress); time.sleep(.025)

    game=CircusGameState(); field=TargetField(); tracker=SemanticDartTracker()
    try: engine.reset_blocking_state()
    except Exception: pass
    tracker.baseline(read_samples(engine.get_active_darts()))

    running=True; tick=0; lab_mode=None; lab_choice=0; font_choice=0; font_ready_frames=0; fx_choice=0; fx_speed=1; fx_preview_frames=0; ready_was_displayed=False

    while running and engine.running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
        buttons=engine.get_button_events(); hits=read_samples(engine.get_dart_hits()); active=read_samples(engine.get_active_darts())

        if lab_mode=='menu':
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'): lab_choice=(lab_choice-1)%2; audio.move()
            if buttons.get('btn_right') or buttons.get('btn_up'): lab_choice=(lab_choice+1)%2; audio.move()
            if buttons.get('btn_a'): lab_mode='font' if lab_choice==0 else 'anim'; audio.select()
            elif buttons.get('btn_b'): lab_mode=None; audio.back()

        elif lab_mode=='font':
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'): font_choice=(font_choice-1)%len(FONT_LAB_OPTIONS); audio.move()
            if buttons.get('btn_right') or buttons.get('btn_up'): font_choice=(font_choice+1)%len(FONT_LAB_OPTIONS); audio.move()
            if buttons.get('btn_a'): font_ready_frames=READY_HOLD_FRAMES; audio.ready()
            if buttons.get('btn_b'): lab_mode='menu'; font_ready_frames=0; audio.back()
            if font_ready_frames>0: font_ready_frames-=1

        elif lab_mode=='anim':
            tracker.baseline(active)
            if buttons.get('btn_left'): fx_choice=(fx_choice-1)%len(FX_NAMES); fx_preview_frames=0; audio.move()
            if buttons.get('btn_right'): fx_choice=(fx_choice+1)%len(FX_NAMES); fx_preview_frames=0; audio.move()
            if buttons.get('btn_up'): fx_speed=(fx_speed+1)%len(SPEED_NAMES); fx_preview_frames=0; audio.move()
            if buttons.get('btn_down'): fx_speed=(fx_speed-1)%len(SPEED_NAMES); fx_preview_frames=0; audio.move()
            if buttons.get('btn_a'): fx_preview_frames=READY_HOLD_FRAMES; audio.ready()
            if buttons.get('btn_b'): lab_mode='menu'; fx_preview_frames=0; audio.back()
            if fx_preview_frames>0: fx_preview_frames-=1

        elif game.phase is Phase.SHOW_SELECT:
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'): game.cycle_show(-1); audio.move()
            if buttons.get('btn_right') or buttons.get('btn_up'): game.cycle_show(1); audio.move()
            if buttons.get('btn_a'): game.go_acts(); audio.select()
            elif TEST_MODE and buttons.get('btn_b'): lab_mode='menu'; lab_choice=0; audio.select()

        elif game.phase is Phase.ACT_SELECT:
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'): game.cycle_act(-1); audio.move()
            if buttons.get('btn_right') or buttons.get('btn_up'): game.cycle_act(1); audio.move()
            if buttons.get('btn_b'): game.go_shows(); audio.back()
            elif buttons.get('btn_a'): game.go_players(); audio.select()

        elif game.phase is Phase.PLAYER_SELECT:
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'): game.set_players(game.player_count-1 if game.player_count>1 else 4); audio.move()
            if buttons.get('btn_right') or buttons.get('btn_up'): game.set_players(game.player_count+1 if game.player_count<4 else 1); audio.move()
            if buttons.get('btn_b'): game.go_acts(); audio.back()
            elif buttons.get('btn_a'): game.begin(); field.start_act(game.mechanic_profile,difficulty=game.difficulty_rank); tracker.baseline(active); audio.select()

        elif game.phase is Phase.ACT_INTRO:
            tracker.baseline(active); game.phase_frames-=1
            if game.phase_frames<=0: game.begin_play()

        elif game.phase is Phase.PLAYING:
            field.update(game.mechanic_profile,difficulty=game.difficulty_rank); semantic=tracker.observe(hits,active)
            if semantic:
                dart=semantic[0]; _,transition=game.record_throw(field.hit_test(dart.x,dart.y).points)
                if transition=='game_over': tracker.baseline(active)
            else: game.tick_presentation()

        elif game.phase is Phase.GAME_RESULT:
            tracker.baseline(active)
            if buttons.get('btn_a'): game.begin(); field.start_act(game.mechanic_profile,difficulty=game.difficulty_rank); audio.select()
            elif buttons.get('btn_b'): game.go_shows(); field.reset(); audio.back()

        ready_displayed=(lab_mode is None and game.phase is Phase.PLAYING and game.message_frames==0 and game.ready_visible())
        if ready_displayed and not ready_was_displayed: audio.ready()
        ready_was_displayed=ready_displayed

        if lab_mode=='menu': draw_test_lab_menu(surface,lab_choice)
        elif lab_mode=='font': draw_font_lab(surface,font_choice,tick,font_ready_frames)
        elif lab_mode=='anim': draw_animation_lab(surface,fx_choice,fx_speed,tick,fx_preview_frames)
        else:
            surface.fill(BLACK); bg(surface,tick)
            if game.phase in (Phase.SHOW_SELECT,Phase.ACT_SELECT,Phase.PLAYER_SELECT):
                draw_main_title(surface,title_font)
                if game.phase is Phase.SHOW_SELECT: draw_show_menu(surface,game)
                elif game.phase is Phase.ACT_SELECT: draw_act_menu(surface,game)
                else: draw_player_menu(surface,game)
            elif game.phase is Phase.ACT_INTRO:
                font=pygame.font.Font(None,14); show_label=font.render(SHOWS[game.show_index].menu_name,False,DARK_RED); surface.blit(show_label,(64-show_label.get_width()//2,32))
                act_label=font.render(f'ACT {game.act_index+1}',False,PURPLE); surface.blit(act_label,(64-act_label.get_width()//2,48))
                label=pygame.font.Font(None,17).render(game.active_act_spec.name,False,INK); surface.blit(label,(64-label.get_width()//2,65))
                lower_clear(surface,PLAYER_COLORS[game.current_player]); draw_text(surface,f'P{game.current_player+1}',2,130,PLAYER_COLORS[game.current_player]); draw_centered(surface,'GET READY',32,139,CREAM,sy=2,advance=4)
            elif game.phase is Phase.PLAYING:
                for target in field.targets: draw_target(surface,target,tiny)
                for impact in field.impacts: draw_impact(surface,impact)
                if game.message_frames>0: draw_result_callout(surface,game)
                elif game.ready_visible(): draw_ready_main_border(surface,game,tick); draw_throw_ready(surface,game,tick)
                else: draw_game_status(surface,game)
            elif game.phase is Phase.GAME_RESULT: draw_result(surface,game)
            protect_lower(surface)

        submit(engine,surface); pygame.display.flip(); tick+=1; clock.tick(FPS)

    try: engine.close()
    except Exception: pass
    pygame.quit()


if __name__=='__main__':
    main()
