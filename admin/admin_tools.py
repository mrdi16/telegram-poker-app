import random
from typing import List, Dict, Tuple, Optional
from game.poker_engine import Card
from game.hand_evaluator import HandEvaluator
from game.player_manager import Player
from game.table_manager import PokerTable

class AdminTools:
    def __init__(self, chip_manager, admin_logger):
        self.chip_manager = chip_manager
        self.admin_logger = admin_logger
    
    def get_all_player_cards(self, table: PokerTable) -> Dict[str, List[Card]]:
        """Получить карты всех игроков за столом"""
        player_cards = {}
        
        for player in table.player_manager.players:
            player_cards[player.username] = player.hole_cards.copy()
        
        return player_cards
    
    def calculate_win_probabilities(self, table: PokerTable, simulations: int = 1000) -> Dict[str, float]:
        """
        Расчет вероятностей выигрыша для каждого игрока методом Монте-Карло
        """
        if table.stage.name == "WAITING":
            return {}
        
        active_players = [p for p in table.player_manager.players if not p.folded]
        
        if len(active_players) < 2:
            return {player.username: 100.0 for player in active_players}
        
        win_counts = {player.username: 0 for player in active_players}
        
        for _ in range(simulations):
            # Создаем тестовую колоду
            test_deck = self._create_test_deck(table, active_players)
            
            # Раздаем оставшиеся общие карты
            test_community = table.community_cards.copy()
            cards_needed = 5 - len(test_community)
            
            for _ in range(cards_needed):
                if test_deck:
                    test_community.append(test_deck.pop())
            
            # Определяем победителя
            winner = self._simulate_showdown(active_players, test_community)
            if winner:
                win_counts[winner.username] += 1
        
        # Переводим в проценты
        probabilities = {
            username: (count / simulations) * 100 
            for username, count in win_counts.items()
        }
        
        return probabilities
    
    def _create_test_deck(self, table: PokerTable, active_players: List[Player]) -> List[Card]:
        """Создает тестовую колоду без известных карт"""
        all_known_cards = set()
        
        # Добавляем карты активных игроков
        for player in active_players:
            all_known_cards.update(player.hole_cards)
        
        # Добавляем общие карты
        all_known_cards.update(table.community_cards)
        
        # Создаем полную колоду и убираем известные карты
        full_deck = [Card(suit, rank) for suit in table.deck.cards[0].suit.__class__ 
                    for rank in table.deck.cards[0].rank.__class__]
        
        test_deck = [card for card in full_deck if card not in all_known_cards]
        random.shuffle(test_deck)
        
        return test_deck
    
    def _simulate_showdown(self, players: List[Player], community_cards: List[Card]) -> Optional[Player]:
        """Симулирует вскрытие карт и возвращает победителя"""
        best_player = None
        best_hand = None
        
        for player in players:
            hand_strength = HandEvaluator.evaluate_hand(player.hole_cards, community_cards)
            
            if not best_hand or HandEvaluator.compare_hands(hand_strength, best_hand) > 0:
                best_hand = hand_strength
                best_player = player
            elif HandEvaluator.compare_hands(hand_strength, best_hand) == 0:
                # Ничья - не считаем победителем
                best_player = None
        
        return best_player
    
    def get_table_overview(self, table: PokerTable) -> Dict:
        """Получить полную информацию о столе для админа"""
        player_cards = self.get_all_player_cards(table)
        win_probs = self.calculate_win_probabilities(table)
        
        overview = {
            'table_id': table.table_id,
            'limit': table.limit,
            'stage': table.stage.name,
            'pot': table.pot,
            'current_bet': table.current_bet,
            'community_cards': [str(card) for card in table.community_cards],
            'players': [],
            'win_probabilities': win_probs
        }
        
        for player in table.player_manager.players:
            player_info = {
                'username': player.username,
                'user_id': player.user_id,
                'chips': player.chips,
                'current_bet': player.current_bet,
                'folded': player.folded,
                'all_in': player.all_in,
                'is_admin': player.is_admin,
                'hole_cards': [str(card) for card in player.hole_cards],
                'win_probability': win_probs.get(player.username, 0),
                'stats': {
                    'hands_played': player.hands_played,
                    'hands_won': player.hands_won,
                    'win_rate': player.win_rate,
                    'biggest_win': player.biggest_win
                }
            }
            overview['players'].append(player_info)
        
        return overview
    
    def force_fold_player(self, table: PokerTable, target_username: str, admin_id: int) -> Tuple[bool, str]:
        """Принудительно заставить игрока сбросить карты"""
        player = next((p for p in table.player_manager.players if p.username == target_username), None)
        
        if not player:
            return False, f"Игрок {target_username} не найден"
        
        if player.folded:
            return False, f"Игрок {target_username} уже сбросил карты"
        
        player.folded = True
        
        # Логируем действие
        self.admin_logger.log_admin_action(
            admin_id=admin_id,
            action_type="FORCE_FOLD",
            target=target_username,
            details=f"Принудительный фолд на столе {table.table_id}"
        )
        
        # Если это текущий игрок, переходим к следующему
        if (table.current_player_index < len(table.player_manager.players) and 
            table.player_manager.players[table.current_player_index].username == target_username):
            table._next_turn()
        
        return True, f"Игрок {target_username} принудительно сбросил карты"
    
    def reset_game(self, table: PokerTable, admin_id: int) -> Tuple[bool, str]:
        """Сбросить текущую игру"""
        table.stage = table.stage.WAITING
        table.community_cards = []
        table.pot = 0
        table.current_bet = 0
        
        for player in table.player_manager.players:
            player.reset_hand()
        
        # Логируем действие
        self.admin_logger.log_admin_action(
            admin_id=admin_id,
            action_type="RESET_GAME",
            target=f"table_{table.table_id}",
            details="Сброс текущей игры"
        )
        
        return True, "Игра сброшена"