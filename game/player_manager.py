from typing import List, Optional
from .poker_engine import PlayerAction

class Player:
    def __init__(self, user_id: int, username: str, chips: float = 1000, is_admin: bool = False):
        self.user_id = user_id
        self.username = username
        self.chips = chips
        self.hole_cards: List[Card] = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
        self.is_admin = is_admin
        
        # Статистика
        self.hands_played = 0
        self.hands_won = 0
        self.biggest_win = 0
        
    @property
    def win_rate(self) -> float:
        return (self.hands_won / self.hands_played * 100) if self.hands_played > 0 else 0
    
    def reset_hand(self):
        self.hole_cards = []
        self.current_bet = 0
        self.folded = False
        self.all_in = False
    
    def bet(self, amount: float) -> float:
        actual_bet = min(amount, self.chips)
        self.chips -= actual_bet
        self.current_bet += actual_bet
        
        if self.chips == 0:
            self.all_in = True
        
        return actual_bet
    
    def can_act(self) -> bool:
        return not (self.folded or self.all_in)
    
    def __str__(self):
        return f"{self.username} (${self.chips})"

class PlayerManager:
    def __init__(self):
        self.players: List[Player] = []
    
    def add_player(self, user_id: int, username: str, chips: float = 1000, is_admin: bool = False) -> bool:
        if not any(p.user_id == user_id for p in self.players):
            self.players.append(Player(user_id, username, chips, is_admin))
            return True
        return False
    
    def get_player(self, user_id: int) -> Optional[Player]:
        return next((p for p in self.players if p.user_id == user_id), None)
    
    def remove_player(self, user_id: int) -> bool:
        player = self.get_player(user_id)
        if player:
            self.players.remove(player)
            return True
        return False
    
    def get_active_players(self) -> List[Player]:
        return [p for p in self.players if not p.folded]