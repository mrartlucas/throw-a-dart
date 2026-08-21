from __future__ import annotations
import time
import numpy as np
import pygame
from pydartsnut import Dartsnut
from throw_a_dart.semantic_darts import DartSample, SemanticDartTracker
from throw_a_dart.target_engine import TargetBehavior, TargetField
from throw_a_dart.game_state import SHOWS, PLAYER_COLORS, TEST_MODE, CircusGameState, Phase
from throw_a_dart.pixel_ui import draw_centered, draw_text, draw_right, draw_chevron, draw_up_marker

WIDTH, HEIGHT, PLAY_H = 128, 160, 128
FPS = 30
BLACK=(0,0,0); CREAM=(250,238,199); RED=(225,48,52); DARK_RED=(111,19,31); GOLD=(255,194,45)
YELLOW=(255,225,88); TEAL=(32,190,181); BLUE=(55,137,217); DARK_BLUE=(20,46,79); PURPLE=(104,61,151)
BROWN=(116,63,35); INK=(24,21,27); WHITE=(255,255,255); DIM=(118,118,118)


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
        pygame.draw.polygon(surface,RED,((x,0),(x+12,0),(x+25,17),(x+12,17),(x+12,17)))
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
    output=[]
    for dart_index,x,y in rows:
        if 0<=int(x)<128 and 0<=int(y)<128:
            output.append(DartSample(int(dart_index),int(x),int(y)))
    return tuple(output)


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


def draw_star_row(surface,stars,y=148):
    # Tiny 3-slot progress readout. Filled stars are represented as compact
    # diamond/star marks so they survive on the 64x32 display.
    start=25
    for i in range(3):
        color=GOLD if i<stars else DIM
        x=start+i*7
        pygame.draw.rect(surface,color,(x,y+1,3,1))
        pygame.draw.rect(surface,color,(x+1,y,1,3))


def draw_show_menu(surface,game):
    lower_clear(surface,PURPLE)
    draw_centered(surface,'SHOWS',32,130,PURPLE)
    label=game.selected_show_spec.menu_name
    advance=3 if len(label)>10 else 4
    draw_centered(surface,label,32,139,WHITE,advance=advance)
    draw_chevron(surface,2,142,TEAL,False)
    draw_chevron(surface,59,142,TEAL,True)
    draw_centered(surface,'A NEXT',32,153,TEAL,advance=4)


def draw_act_menu(surface,game):
    lower_clear(surface,PURPLE)
    draw_centered(surface,'ACTS',32,130,PURPLE)
    label=game.selected_act_spec.menu_name
    advance=3 if len(label)>10 else 4
    draw_centered(surface,label,32,139,WHITE,advance=advance)
    draw_chevron(surface,2,142,TEAL,False)
    draw_chevron(surface,59,142,TEAL,True)
    draw_star_row(surface,game.stars_for_selected(),147)
    draw_text(surface,'A NEXT',3,153,TEAL,advance=4)
    draw_right(surface,'B BACK',60,153,TEAL,advance=4)


def draw_player_menu(surface,game):
    lower_clear(surface,PURPLE)
    draw_centered(surface,'PLAYERS',32,130,CREAM)
    xs=(8,23,38,53)
    for index,x in enumerate(xs):
        color=YELLOW if index+1==game.player_count else WHITE
        draw_centered(surface,str(index+1),x,139,color,sx=1,sy=2)
    draw_up_marker(surface,xs[game.player_count-1],150,YELLOW)
    draw_text(surface,'A START',3,153,TEAL,advance=4)
    draw_right(surface,'B BACK',60,153,TEAL,advance=4)


def draw_throw_ready(surface,game):
    lower_clear(surface,PLAYER_COLORS[game.current_player])
    draw_centered(surface,'THROW',32,133,YELLOW,sx=2,sy=2,advance=7)
    draw_centered(surface,'READY',32,145,TEAL,sx=2,sy=2,advance=7)


def draw_game_status(surface,game):
    color=PLAYER_COLORS[game.current_player]
    lower_clear(surface,color)
    draw_text(surface,f'P{game.current_player+1}',2,130,color)
    draw_right(surface,f'D{game.throws_remaining()}',61,130,GOLD)
    draw_centered(surface,f'S{game.scores[game.current_player]:04d}',32,140,WHITE)
    multiplier=1+min(game.combo[game.current_player],2) if game.combo[game.current_player] else 1
    draw_text(surface,f'X{multiplier}',2,152,GOLD)
    draw_right(surface,f'A{game.act_index+1}',61,152,CREAM)


def draw_result_callout(surface,game):
    color=PLAYER_COLORS[game.last_player]
    lower_clear(surface,color)
    draw_text(surface,f'P{game.last_player+1}',2,130,color)
    if game.last_points:
        draw_centered(surface,'HIT',32,136,TEAL,sx=2,sy=2,advance=7)
        draw_centered(surface,f'+{game.last_points}',32,149,GOLD)
    else:
        draw_centered(surface,'MISS',32,140,RED,sx=2,sy=2,advance=7)


def main():
    engine=Dartsnut()
    pygame.init()
    pygame.display.set_mode((128,160))
    surface=pygame.Surface((128,160))
    clock=pygame.time.Clock()
    title_font=pygame.font.Font(None,23)
    tiny=pygame.font.Font(None,10)

    for progress in (.08,.2,.34,.49,.63,.78,.9,1.0):
        loading(engine,surface,progress)
        time.sleep(.025)

    game=CircusGameState()
    field=TargetField()
    tracker=SemanticDartTracker()
    try:
        engine.reset_blocking_state()
    except Exception:
        pass
    tracker.baseline(read_samples(engine.get_active_darts()))

    running=True
    tick=0
    while running and engine.running:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
        buttons=engine.get_button_events()
        hits=read_samples(engine.get_dart_hits())
        active=read_samples(engine.get_active_darts())

        if game.phase is Phase.SHOW_SELECT:
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'):
                game.cycle_show(-1)
            if buttons.get('btn_right') or buttons.get('btn_up'):
                game.cycle_show(1)
            if buttons.get('btn_a'):
                game.go_acts()

        elif game.phase is Phase.ACT_SELECT:
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'):
                game.cycle_act(-1)
            if buttons.get('btn_right') or buttons.get('btn_up'):
                game.cycle_act(1)
            if buttons.get('btn_b'):
                game.go_shows()
            elif buttons.get('btn_a'):
                game.go_players()

        elif game.phase is Phase.PLAYER_SELECT:
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'):
                game.set_players(game.player_count-1 if game.player_count>1 else 4)
            if buttons.get('btn_right') or buttons.get('btn_up'):
                game.set_players(game.player_count+1 if game.player_count<4 else 1)
            if buttons.get('btn_b'):
                game.go_acts()
            elif buttons.get('btn_a'):
                game.begin()
                field.start_act(game.mechanic_profile, difficulty=game.difficulty_rank)
                tracker.baseline(active)

        elif game.phase is Phase.ACT_INTRO:
            tracker.baseline(active)
            game.phase_frames-=1
            if game.phase_frames<=0:
                game.begin_play()

        elif game.phase is Phase.PLAYING:
            field.update(game.mechanic_profile, difficulty=game.difficulty_rank)
            semantic=tracker.observe(hits,active)
            if semantic:
                dart=semantic[0]
                _,transition=game.record_throw(field.hit_test(dart.x,dart.y).points)
                if transition=='game_over':
                    tracker.baseline(active)
            else:
                game.tick_presentation()

        elif game.phase is Phase.GAME_RESULT:
            tracker.baseline(active)
            if buttons.get('btn_a'):
                game.begin()
                field.start_act(game.mechanic_profile, difficulty=game.difficulty_rank)
            elif buttons.get('btn_b'):
                game.go_shows()
                field.reset()

        surface.fill(BLACK)
        bg(surface,tick)

        if game.phase in (Phase.SHOW_SELECT,Phase.ACT_SELECT,Phase.PLAYER_SELECT):
            draw_main_title(surface,title_font)
            if game.phase is Phase.SHOW_SELECT:
                draw_show_menu(surface,game)
            elif game.phase is Phase.ACT_SELECT:
                draw_act_menu(surface,game)
            else:
                draw_player_menu(surface,game)

        elif game.phase is Phase.ACT_INTRO:
            font=pygame.font.Font(None,14)
            show_label=font.render(SHOWS[game.show_index].menu_name,False,DARK_RED)
            surface.blit(show_label,(64-show_label.get_width()//2,32))
            act_label=font.render(f'ACT {game.act_index+1}',False,PURPLE)
            surface.blit(act_label,(64-act_label.get_width()//2,48))
            label=pygame.font.Font(None,17).render(game.active_act_spec.name,False,INK)
            surface.blit(label,(64-label.get_width()//2,65))
            lower_clear(surface,PLAYER_COLORS[game.current_player])
            draw_text(surface,f'P{game.current_player+1}',2,130,PLAYER_COLORS[game.current_player])
            draw_centered(surface,'GET READY',32,142,CREAM,advance=4)

        elif game.phase is Phase.PLAYING:
            for target in field.targets:
                draw_target(surface,target,tiny)
            for impact in field.impacts:
                draw_impact(surface,impact)
            color=PLAYER_COLORS[game.current_player]
            pygame.draw.rect(surface,INK,(3,3,21,11))
            font=pygame.font.Font(None,12)
            badge=font.render(f'P{game.current_player+1}',False,color)
            surface.blit(badge,(13-badge.get_width()//2,4))

            if game.message_frames>0:
                draw_result_callout(surface,game)
            elif game.ready_visible():
                draw_throw_ready(surface,game)
            else:
                draw_game_status(surface,game)

        elif game.phase is Phase.GAME_RESULT:
            winner=game.winner()
            stars=game.stars[game.show_index][game.act_index]
            pygame.draw.rect(surface,INK,(10,28,108,74))
            label=title_font.render('SHOW OVER!',False,GOLD)
            surface.blit(label,(64-label.get_width()//2,34))
            font=pygame.font.Font(None,17)
            label=font.render(f'P{winner+1} WINS',False,PLAYER_COLORS[winner])
            surface.blit(label,(64-label.get_width()//2,57))
            label=font.render(str(game.scores[winner]),False,WHITE)
            surface.blit(label,(64-label.get_width()//2,74))
            for i in range(3):
                col=GOLD if i<stars else DIM
                pygame.draw.circle(surface,col,(54+i*10,92),3,1 if i>=stars else 0)
            lower_clear(surface,PLAYER_COLORS[winner])
            draw_centered(surface,'RESULT',32,130,CREAM)
            draw_centered(surface,f'P{winner+1} {game.scores[winner]}',32,140,PLAYER_COLORS[winner])
            draw_text(surface,'A AGAIN',3,153,TEAL,advance=4)
            draw_right(surface,'B MENU',60,153,TEAL,advance=4)

        protect_lower(surface)
        submit(engine,surface)
        pygame.display.flip()
        tick+=1
        clock.tick(FPS)

    try:
        engine.close()
    except Exception:
        pass
    pygame.quit()

if __name__=='__main__':
    main()
