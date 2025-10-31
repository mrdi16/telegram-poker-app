import time
from typing import List, Dict, Optional, Tuple
from .poker_engine import Deck, GameStage, PlayerAction, ALL_RANKS
from .player_manager import PlayerManager, Player
from .hand_evaluator import HandEvaluator

class PokerTable:
    def __init__(self, table_id: int, limit: int = 100, is_private: bool = False, password: str = None):
        self.table_id = table_id
        self.limit = limit
        self.is_private = is_private
        self.password = password
        
        self.player_manager = PlayerManager()
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.current_bet = 0
        self.stage = GameStage.WAITING
        self.dealer_position = 0
        self.current_player_index = 0
        self.last_action_time = 0
        
        # Конфигурация стола
        self.blinds = self._get_blinds()
        self.action_timeout = 60  # 60 секунд на ход
    
    def _get_blinds(self) -> Tuple[float, float]:
        blinds_config = {
            100: (0.1, 0.2),
            1000: (1, 2),
            10000: (10, 20)
        }
        return blinds_config.get(self.limit, (1, 2))
    
    def start_hand(self) -> Tuple[bool, str]:
        if len(self.player_manager.players) < 2:
            return False, "Нужно минимум 2 игрока для начала игры"
        
        self.stage = GameStage.PREFLOP
        self.deck.reset()
        self.community_cards = []
        self.pot = 0
        self.current_bet = self.blinds[1]  # big blind
        
        # Сброс состояния игроков и раздача карт
        for player in self.player_manager.players:
            player.reset_hand()
            player.hole_cards = [self.deck.deal(), self.deck.deal()]
        
        self._post_blinds()
        self.current_player_index = (self.dealer_position + 3) % len(self.player_manager.players)
        self.last_action_time = time.time()
        
        return True, "Раздача началась!"
    
    def _post_blinds(self):
        players = self.player_manager.players
        n = len(players)
        
        # Small blind
        sb_player = players[(self.dealer_position + 1) % n]
        sb_bet = sb_player.bet(self.blinds[0])
        
        # Big blind  
        bb_player = players[(self.dealer_position + 2) % n]
        bb_bet = bb_player.bet(self.blinds[1])
        
        self.pot += sb_bet + bb_bet
    
    def make_action(self, player: Player, action: PlayerAction, amount: float = 0) -> Tuple[bool, str]:
        if not self._is_player_turn(player):
            return False, "Не ваш ход"
        
        if not player.can_act():
            return False, "Игрок не может совершать действия"
        
        success = False
        message = ""
        
        if action == PlayerAction.FOLD:
            player.folded = True
            success = True
            message = f"{player.username} сбросил карты"
            
        elif action == PlayerAction.CHECK:
            if player.current_bet < self.current_bet:
                return False, "Нельзя чек, нужно уравнять"
            success = True
            message = f"{player.username} чек"
            
        elif action == PlayerAction.CALL:
            call_amount = self.current_bet - player.current_bet
            if call_amount > player.chips:
                return False, "Недостаточно фишек"
            actual_bet = player.bet(call_amount)
            self.pot += actual_bet
            success = True
            message = f"{player.username} уравнял {actual_bet}"
            
        elif action == PlayerAction.RAISE:
            if amount <= self.current_bet:
                return False, "Ставка должна быть больше текущей"
            if amount > player.chips:
                return False, "Недостаточно фишек"
            actual_bet = player.bet(amount - player.current_bet)
            self.current_bet = amount
            self.pot += actual_bet
            success = True
            message = f"{player.username} поднял до {amount}"
            
        elif action == PlayerAction.ALL_IN:
            all_in_amount = player.chips
            player.bet(all_in_amount)
            if player.current_bet > self.current_bet:
                self.current_bet = player.current_bet
            self.pot += all_in_amount
            success = True
            message = f"{player.username} ва-банк на {all_in_amount}"
        
        if success:
            self._next_turn()
            self.last_action_time = time.time()
        
        return success, message
    
    def _is_player_turn(self, player: Player) -> bool:
        current_player = self.player_manager.players[self.current_player_index]
        return current_player.user_id == player.user_id
    
    def _next_turn(self):
        players = self.player_manager.players
        active_players = [p for p in players if p.can_act()]
        
        if len(active_players) <= 1:
            self._end_hand()
            return
        
        # Переход к следующему активному игроку
        for i in range(1, len(players) + 1):
            next_index = (self.current_player_index + i) % len(players)
            if players[next_index].can_act():
                self.current_player_index = next_index
                break
        
        # Проверка окончания раунда
        if self._is_round_complete():
            self._next_round()
    
    def _is_round_complete(self) -> bool:
        active_players = [p for p in self.player_manager.players if p.can_act()]
        
        if len(active_players) <= 1:
            return True
        
        # Все активные игроки поставили одинаково
        current_bets = [p.current_bet for p in active_players]
        return all(bet == current_bets[0] for bet in current_bets)
    
    def _next_round(self):
        if self.stage == GameStage.PREFLOP:
            self.stage = GameStage.FLOP
            self.deck.deal()  # Сжигаем карту
            self.community_cards = [self.deck.deal() for _ in range(3)]
            
        elif self.stage == GameStage.FLOP:
            self.stage = GameStage.TURN
            self.deck.deal()  # Сжигаем карту
            self.community_cards.append(self.deck.deal())
            
        elif self.stage == GameStage.TURN:
            self.stage = GameStage.RIVER
            self.deck.deal()  # Сжигаем карту
            self.community_cards.append(self.deck.deal())
            
        elif self.stage == GameStage.RIVER:
            self._end_hand()
            return
        
        # Сброс текущих ставок для нового раунда
        for player in self.player_manager.players:
            player.current_bet = 0
        self.current_bet = 0
        
        # Первый активный игрок после дилера начинает новый раунд
        players = self.player_manager.players
        for i in range(1, len(players) + 1):
            next_index = (self.dealer_position + i) % len(players)
            if players[next_index].can_act():
                self.current_player_index = next_index
                break
    
    def _end_hand(self):
        # Определение победителя и распределение банка
        active_players = self.player_manager.get_active_players()
        
        if len(active_players) == 1:
            # Один игрок не сбросил карты - он победитель
            winner = active_players[0]
            winner.chips += self.pot
            winner.hands_played += 1
            winner.hands_won += 1
            if self.pot > winner.biggest_win:
                winner.biggest_win = self.pot
        else:
            # Показываем карты и определяем победителя по комбинациям
            best_hand = None
            winners = []
            
            for player in active_players:
                hand_strength = HandEvaluator.evaluate_hand(player.hole_cards, self.community_cards)
                
                if not best_hand or HandEvaluator.compare_hands(hand_strength, best_hand) > 0:
                    best_hand = hand_strength
                    winners = [player]
                elif HandEvaluator.compare_hands(hand_strength, best_hand) == 0:
                    winners.append(player)
            
            # Распределение банка между победителями
            win_amount = self.pot / len(winners)
            for winner in winners:
                winner.chips += win_amount
                winner.hands_played += 1
                winner.hands_won += 1
                if win_amount > winner.biggest_win:
                    winner.biggest_win = win_amount
        
        # Подготовка к следующей раздаче
        self.stage = GameStage.WAITING
        self.dealer_position = (self.dealer_position + 1) % len(self.player_manager.players)
        self.pot = 0
        self.current_bet = 0
        
        # Автоматически начинаем следующую раздачу через 5 секунд
        # (в реальной реализации это будет через таймер)
    
    def check_timeouts(self):
        """Проверяет таймауты и автоматически фолдит игроков"""
        if self.stage == GameStage.WAITING:
            return
        
        if time.time() - self.last_action_time > self.action_timeout:
            current_player = self.player_manager.players[self.current_player_index]
            if current_player.can_act():
                current_player.folded = True
                self._next_turn()
                self.last_action_time = time.time()