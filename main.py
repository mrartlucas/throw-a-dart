from __future__ import annotations
import math, time
import numpy as np
import pygame
from pydartsnut import Dartsnut
from throw_a_dart.semantic_darts import DartSample, SemanticDartTracker
from throw_a_dart.target_engine import TargetBehavior, TargetField
from throw_a_dart.game_state import ACT_NAMES, PLAYER_COLORS, CircusGameState, Phase

WIDTH, HEIGHT, PLAY_H = 128, 160, 128
LOWER_Y, LOWER_W = 128, 64
FPS = 30
BLACK=(0,0,0); CREAM=(250,238,199); RED=(225,48,52); DARK_RED=(111,19,31); GOLD=(255,194,45)
YELLOW=(255,225,88); TEAL=(32,190,181); BLUE=(55,137,217); DARK_BLUE=(20,46,79); PURPLE=(104,61,151)
BROWN=(116,63,35); INK=(24,21,27); WHITE=(255,255,255)

def text(s,f,v,x,y,c=WHITE,center=False):
    im=f.render(v,False,c); s.blit(im,(x-im.get_width()//2 if center else x,y))

def submit(engine,s):
    frame=np.transpose(pygame.surfarray.array3d(s),(1,0,2)); engine.update_frame_buffer(frame)

def protect_lower(s): pygame.draw.rect(s,BLACK,(64,128,64,32))

def loading(engine,s,big,small,p):
    s.fill(BLACK); pygame.draw.rect(s,DARK_BLUE,(0,0,128,128))
    for y in range(0,128,16): pygame.draw.polygon(s,DARK_RED if (y//16)%2==0 else PURPLE,((0,y),(64,y+18),(128,y),(128,y+8),(64,y+26),(0,y+8)))
    pygame.draw.rect(s,INK,(8,46,112,38)); text(s,big,"THROW A DART",64,50,GOLD,True); text(s,small,"LOADING...",64,70,CREAM,True)
    pygame.draw.rect(s,WHITE,(13,94,102,8),1); pygame.draw.rect(s,TEAL,(15,96,int(98*p),4))
    pygame.draw.rect(s,INK,(0,128,64,32)); text(s,small,"LOADING",32,132,CREAM,True); pygame.draw.rect(s,WHITE,(5,146,54,6),1); pygame.draw.rect(s,TEAL,(7,148,int(50*p),2))
    protect_lower(s); submit(engine,s)

def bg(s,tick):
    pygame.draw.rect(s,CREAM,(0,0,128,128)); pygame.draw.rect(s,DARK_RED,(0,0,128,17))
    for x in range(-16,144,24): pygame.draw.polygon(s,RED,((x,0),(x+12,0),(x+25,17),(x+12,17)))
    pygame.draw.line(s,GOLD,(0,17),(127,17),2); pygame.draw.rect(s,(241,219,171),(0,19,128,88))
    for y in (35,53,71,89): pygame.draw.line(s,(220,193,145),(0,y),(127,y),1)
    pygame.draw.rect(s,BROWN,(0,107,128,21))
    for x in range(0,128,16): pygame.draw.line(s,(82,43,27),(x,107),(x,127),1)
    for x in range(5,128,12): pygame.draw.circle(s,YELLOW if ((tick//12)+x//12)%2 else WHITE,(x,20),1)

def draw_target(s,t,tiny):
    if not t.visible or t.hit: return
    x,y,r=int(t.x),int(t.y),t.radius
    if t.behavior is TargetBehavior.RISING:
        col=GOLD if t.value>=75 else (244,73,83) if t.value<=50 else (70,154,240)
        pygame.draw.ellipse(s,INK,(x-r-1,y-r-2,(r+1)*2,(r+2)*2)); pygame.draw.ellipse(s,col,(x-r,y-r-1,r*2,(r+1)*2)); pygame.draw.polygon(s,col,((x-2,y+r-1),(x+2,y+r-1),(x,y+r+4)))
    elif t.behavior is TargetBehavior.POPUP:
        pygame.draw.rect(s,BROWN,(x-r-3,y+r-2,(r+3)*2,5)); pygame.draw.circle(s,INK,(x,y),r+2); pygame.draw.circle(s,CREAM,(x,y),r); pygame.draw.circle(s,RED,(x,y+1),3); pygame.draw.circle(s,BLUE,(x-4,y-3),1); pygame.draw.circle(s,BLUE,(x+4,y-3),1)
    else:
        pygame.draw.circle(s,INK,(x,y),r+2); pygame.draw.circle(s,CREAM,(x,y),r); pygame.draw.circle(s,RED,(x,y),max(3,r-3)); pygame.draw.circle(s,WHITE,(x,y),max(2,r-7)); pygame.draw.circle(s,GOLD,(x,y),max(2,r-9))
    if t.behavior is not TargetBehavior.POPUP: text(s,tiny,str(t.value),x,y-4,INK,True)

def lower_base(s,color): pygame.draw.rect(s,INK,(0,128,64,32)); pygame.draw.line(s,color,(0,128),(63,128),1)

def read_samples(rows):
    out=[]
    for i,x,y in rows:
        if 0<=int(x)<128 and 0<=int(y)<128: out.append(DartSample(int(i),int(x),int(y)))
    return tuple(out)

def main():
    engine=Dartsnut(); pygame.init(); pygame.display.set_mode((128,160)); s=pygame.Surface((128,160)); clock=pygame.time.Clock()
    title=pygame.font.Font(None,23); big=pygame.font.Font(None,17); small=pygame.font.Font(None,12); tiny=pygame.font.Font(None,10)
    for p in (.12,.38,.65,.88,1.0): loading(engine,s,big,small,p); time.sleep(.035)
    game=CircusGameState(); field=TargetField(); tracker=SemanticDartTracker()
    try: engine.reset_blocking_state()
    except Exception: pass
    tracker.baseline(read_samples(engine.get_active_darts()))
    running=True; tick=0
    while running and engine.running:
        for e in pygame.event.get():
            if e.type==pygame.QUIT: running=False
        buttons=engine.get_button_events(); hits=read_samples(engine.get_dart_hits()); active=read_samples(engine.get_active_darts())
        if game.phase is Phase.PLAYER_SELECT:
            tracker.baseline(active)
            if buttons.get('btn_left') or buttons.get('btn_down'): game.set_players(game.player_count-1 if game.player_count>1 else 4)
            if buttons.get('btn_right') or buttons.get('btn_up'): game.set_players(game.player_count+1 if game.player_count<4 else 1)
            if buttons.get('btn_a'): game.begin(); field.start_act(0); tracker.baseline(active)
        elif game.phase is Phase.ACT_INTRO:
            tracker.baseline(active); game.phase_frames-=1
            if game.phase_frames<=0: game.begin_play()
        elif game.phase is Phase.PLAYING:
            field.update(game.act_index)
            semantic=tracker.observe(hits,active)
            if semantic:
                d=semantic[0]; game.record_throw(field.hit_test(d.x,d.y).points)
        elif game.phase is Phase.WAIT_REMOVE:
            tracker.baseline(active)
            if not active:
                tr=game.after_removal()
                if tr=='next_act': field.start_act(game.act_index); tracker.baseline(())
        elif game.phase is Phase.GAME_RESULT:
            tracker.baseline(active)
            if buttons.get('btn_a'): game.begin(); field.start_act(0)
            elif buttons.get('btn_b'): game=CircusGameState(player_count=game.player_count); field.reset()

        s.fill(BLACK); bg(s,tick)
        if game.phase is Phase.PLAYER_SELECT:
            pygame.draw.rect(s,INK,(8,32,112,64)); text(s,title,'BULLSEYE',64,37,GOLD,True); text(s,big,'BIG TOP CIRCUS',64,56,CREAM,True); text(s,small,'TARGET ENGINE TEST',64,77,TEAL,True)
            lower_base(s,PLAYER_COLORS[game.player_count-1]); text(s,small,'PLAYERS',32,130,CREAM,True); text(s,big,f'< {game.player_count} >',32,140,PLAYER_COLORS[game.player_count-1],True); text(s,tiny,'A START',32,153,TEAL,True)
        elif game.phase is Phase.ACT_INTRO:
            text(s,small,f'ACT {game.act_index+1}',64,35,DARK_RED,True); text(s,title,ACT_NAMES[game.act_index],64,53,INK,True); text(s,small,('HIT THE BULLSEYES','TRACK THE MOVERS','POP + BALLOONS','EVERYTHING MOVES')[game.act_index],64,77,PURPLE,True)
            lower_base(s,PLAYER_COLORS[game.current_player]); text(s,big,f'P{game.current_player+1}',5,132,PLAYER_COLORS[game.current_player]); text(s,small,'GET READY',32,145,CREAM,True)
        elif game.phase in (Phase.PLAYING,Phase.WAIT_REMOVE):
            for t in field.targets: draw_target(s,t,tiny)
            col=PLAYER_COLORS[game.current_player]; pygame.draw.rect(s,INK,(3,3,21,11)); text(s,small,f'P{game.current_player+1}',13,4,col,True)
            lower_base(s,col); text(s,small,f'P{game.current_player+1}',3,131,col); text(s,tiny,f'A{game.act_index+1}',48,132,CREAM); text(s,small,f'S{game.scores[game.current_player]:04d}',3,141,WHITE); text(s,tiny,f'D{game.throws_remaining()}',44,142,GOLD)
            if game.phase is Phase.WAIT_REMOVE:
                text(s,tiny,f'+{game.last_points}' if game.last_points else 'MISS',3,152,TEAL if game.last_points else RED); text(s,tiny,'REMOVE',39,152,CREAM)
            else:
                text(s,tiny,f'x{min(3,1+game.combo[game.current_player]) if game.combo[game.current_player] else 1}',3,152,GOLD); text(s,tiny,'THROW',35,152,TEAL)
        else:
            w=game.winner(); pygame.draw.rect(s,INK,(10,31,108,68)); text(s,title,'SHOW OVER!',64,37,GOLD,True); text(s,big,f'P{w+1} WINS',64,58,PLAYER_COLORS[w],True); text(s,big,str(game.scores[w]),64,77,WHITE,True)
            lower_base(s,PLAYER_COLORS[w])
            for p in range(game.player_count): text(s,tiny,f'P{p+1} {game.scores[p]}',2,130+p*6,PLAYER_COLORS[p])
            text(s,tiny,'A AGAIN',35,153,TEAL)
        protect_lower(s); submit(engine,s); pygame.display.flip(); tick+=1; clock.tick(FPS)
    try: engine.close()
    except Exception: pass
    pygame.quit()

if __name__=='__main__': main()
