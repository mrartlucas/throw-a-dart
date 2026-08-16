from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

PLAYER_COLORS=((58,137,255),(239,69,74),(62,194,92),(255,211,58))
ACT_NAMES=("BIG TOP","MIDWAY","BALLOONS","FINALE")

class Phase(str,Enum):
    PLAYER_SELECT="player_select"; ACT_INTRO="act_intro"; PLAYING="playing"; WAIT_REMOVE="wait_remove"; GAME_RESULT="game_result"

@dataclass
class CircusGameState:
    player_count:int=1
    current_player:int=0
    act_index:int=0
    throws_per_act:int=5
    scores:list[int]=field(default_factory=lambda:[0,0,0,0])
    combo:list[int]=field(default_factory=lambda:[0,0,0,0])
    throws_by_player:list[int]=field(default_factory=lambda:[0,0,0,0])
    phase:Phase=Phase.PLAYER_SELECT
    phase_frames:int=0
    last_message:str=""
    last_points:int=0

    def set_players(self,count:int)->None: self.player_count=max(1,min(4,count))
    def begin(self)->None:
        self.current_player=0; self.act_index=0; self.scores[:]=[0]*4; self.combo[:]=[0]*4; self.throws_by_player[:]=[0]*4
        self.phase=Phase.ACT_INTRO; self.phase_frames=50
    def begin_play(self)->None: self.phase=Phase.PLAYING
    def throws_remaining(self)->int: return max(0,self.throws_per_act-self.throws_by_player[self.current_player])

    def record_throw(self,base:int)->int:
        self.throws_by_player[self.current_player]+=1
        if base>0:
            mult=1+min(self.combo[self.current_player],2); pts=base*mult
            self.scores[self.current_player]+=pts; self.combo[self.current_player]+=1; self.last_message="HIT"; self.last_points=pts
        else:
            pts=0; self.combo[self.current_player]=0; self.last_message="MISS"; self.last_points=0
        self.phase=Phase.WAIT_REMOVE
        return pts

    def after_removal(self)->str:
        for step in range(1,self.player_count+1):
            p=(self.current_player+step)%self.player_count
            if self.throws_by_player[p] < self.throws_per_act:
                self.current_player=p; self.phase=Phase.PLAYING; return "continue"
        if self.act_index < len(ACT_NAMES)-1:
            self.act_index+=1; self.current_player=0; self.throws_by_player[:]=[0]*4; self.combo[:]=[0]*4
            self.phase=Phase.ACT_INTRO; self.phase_frames=45; return "next_act"
        self.phase=Phase.GAME_RESULT; return "game_over"

    def winner(self)->int:
        return max(range(self.player_count),key=lambda i:self.scores[i])
