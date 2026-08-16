from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

PLAYER_COLORS=((58,137,255),(239,69,74),(62,194,92),(255,211,58))
ACT_NAMES=("BIG TOP","MIDWAY","BALLOONS","FINALE")

class Phase(str,Enum):
    ACT_SELECT="act_select"
    PLAYER_SELECT="player_select"
    ACT_INTRO="act_intro"
    PLAYING="playing"
    GAME_RESULT="game_result"

@dataclass
class CircusGameState:
    player_count:int=1
    selected_act:int=0
    current_player:int=0
    act_index:int=0
    throws_per_act:int=5
    scores:list[int]=field(default_factory=lambda:[0,0,0,0])
    combo:list[int]=field(default_factory=lambda:[0,0,0,0])
    throws_by_player:list[int]=field(default_factory=lambda:[0,0,0,0])
    phase:Phase=Phase.ACT_SELECT
    phase_frames:int=0
    last_message:str=""
    last_points:int=0
    last_player:int=0
    message_frames:int=0

    def set_players(self,count:int)->None:
        self.player_count=max(1,min(4,count))

    def cycle_act(self,delta:int)->None:
        self.selected_act=(self.selected_act+delta)%len(ACT_NAMES)

    def go_players(self)->None:
        self.phase=Phase.PLAYER_SELECT

    def go_acts(self)->None:
        self.phase=Phase.ACT_SELECT

    def begin(self)->None:
        self.current_player=0
        self.act_index=self.selected_act
        self.scores[:]=[0]*4
        self.combo[:]=[0]*4
        self.throws_by_player[:]=[0]*4
        self.last_message=""
        self.last_points=0
        self.last_player=0
        self.message_frames=0
        self.phase=Phase.ACT_INTRO
        self.phase_frames=42

    def begin_play(self)->None:
        self.phase=Phase.PLAYING

    def throws_remaining(self)->int:
        return max(0,self.throws_per_act-self.throws_by_player[self.current_player])

    def _advance_after_throw(self)->str:
        # Rotate immediately. Semantic dart tracking prevents retained darts from
        # repeatedly scoring; physical removal is not a turn gate.
        for step in range(1,self.player_count+1):
            player=(self.current_player+step)%self.player_count
            if self.throws_by_player[player] < self.throws_per_act:
                self.current_player=player
                return "continue"
        self.phase=Phase.GAME_RESULT
        return "game_over"

    def record_throw(self,base:int)->tuple[int,str]:
        if self.phase is not Phase.PLAYING:
            return 0,"ignored"
        scoring_player=self.current_player
        self.last_player=scoring_player
        self.throws_by_player[scoring_player]+=1
        if base>0:
            multiplier=1+min(self.combo[scoring_player],2)
            points=base*multiplier
            self.scores[scoring_player]+=points
            self.combo[scoring_player]+=1
            self.last_message="HIT"
            self.last_points=points
        else:
            points=0
            self.combo[scoring_player]=0
            self.last_message="MISS"
            self.last_points=0
        self.message_frames=18
        return points,self._advance_after_throw()

    def tick_message(self)->None:
        if self.message_frames>0:
            self.message_frames-=1

    def winner(self)->int:
        return max(range(self.player_count),key=lambda i:self.scores[i])
