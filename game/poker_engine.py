import random
from enum import Enum
from typing import List, Tuple, Optional

class Suit(Enum):
    HEARTS = '♥'
    DIAMONDS = '♦' 
    CLUBS = '♣'
    SPADES = '♠'

class Rank:
    def __init__(self, symbol: str, value: int):
        self.symbol = symbol
        self.value = value
    
    def __str__(self):
        return self.symbol
    
    def __eq__(self, other):
        return self.value == other.value

# Создаем ранги
TWO = Rank('2', 2)
THREE = Rank('3', 3)
FOUR = Rank('4', 4)
FIVE = Rank('5', 5)
SIX = Rank('6', 6)
SEVEN = Rank('7', 7)
EIGHT = Rank('8', 8)
NINE = Rank('9', 9)
TEN = Rank('10', 10)
JACK = Rank('J', 11)
QUEEN = Rank('Q', 12)
KING = Rank('K', 13)
ACE = Rank('A', 14)

# Список всех рангов
ALL_RANKS = [TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE]

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank.symbol}{self.suit.value}"
    
    def __repr__(self):
        return str(self)
    
    def __eq__(self, other):
        return self.rank.value == other.rank.value and self.suit == other.suit

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.reset()
    
    def reset(self):
        self.cards = [Card(suit, rank) for suit in Suit for rank in ALL_RANKS]
        self.shuffle()
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def deal(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None
    
    def __len__(self):
        return len(self.cards)

class GameStage(Enum):
    WAITING = "waiting"
    PREFLOP = "preflop" 
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"
    SHOWDOWN = "showdown"

class PlayerAction(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call" 
    RAISE = "raise"
    ALL_IN = "all_in"

class HandRank(Enum):
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10