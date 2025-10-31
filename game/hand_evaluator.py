from typing import List, Tuple
from .poker_engine import Card, HandRank, ALL_RANKS, ACE, KING, QUEEN, JACK, TEN

class HandEvaluator:
    @staticmethod
    def evaluate_hand(hole_cards: List[Card], community_cards: List[Card]) -> Tuple[HandRank, List[int]]:
        all_cards = hole_cards + community_cards
        all_cards.sort(key=lambda x: x.rank.value, reverse=True)
        
        # Проверяем комбинации от самой старшей к младшей
        if HandEvaluator._is_royal_flush(all_cards):
            return HandRank.ROYAL_FLUSH, [10]
        elif result := HandEvaluator._is_straight_flush(all_cards):
            return HandRank.STRAIGHT_FLUSH, [result]
        elif result := HandEvaluator._is_four_of_a_kind(all_cards):
            return HandRank.FOUR_OF_A_KIND, result
        elif result := HandEvaluator._is_full_house(all_cards):
            return HandRank.FULL_HOUSE, result
        elif result := HandEvaluator._is_flush(all_cards):
            return HandRank.FLUSH, result
        elif result := HandEvaluator._is_straight(all_cards):
            return HandRank.STRAIGHT, [result]
        elif result := HandEvaluator._is_three_of_a_kind(all_cards):
            return HandRank.THREE_OF_A_KIND, result
        elif result := HandEvaluator._is_two_pair(all_cards):
            return HandRank.TWO_PAIR, result
        elif result := HandEvaluator._is_one_pair(all_cards):
            return HandRank.ONE_PAIR, result
        else:
            return HandRank.HIGH_CARD, [c.rank.value for c in all_cards[:5]]

    @staticmethod
    def _is_royal_flush(cards: List[Card]) -> bool:
        royal_ranks = {ACE.value, KING.value, QUEEN.value, JACK.value, TEN.value}
        
        # Группируем карты по мастям
        suits = {}
        for card in cards:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card.rank.value)
        
        # Проверяем есть ли масть с королевским стритом
        for suit, ranks in suits.items():
            if len(set(ranks) & royal_ranks) >= 5:
                # Проверяем что это именно стрит-флеш
                suit_cards = [c for c in cards if c.suit == suit]
                suit_cards.sort(key=lambda x: x.rank.value, reverse=True)
                
                # Упрощенная проверка на стрит-флеш
                if len(suit_cards) >= 5:
                    return True
        return False

    @staticmethod
    def _is_straight_flush(cards: List[Card]) -> int:
        # Группируем по мастям
        suits = {}
        for card in cards:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card.rank.value)
        
        # Для каждой масти ищем стрит
        for suit, ranks in suits.items():
            if len(ranks) >= 5:
                unique_ranks = sorted(set(ranks), reverse=True)
                # Проверяем возможные стриты
                for i in range(len(unique_ranks) - 4):
                    if unique_ranks[i] - unique_ranks[i+4] == 4:
                        return unique_ranks[i]
                
                # Проверяем стрит с тузом как 1 (A-2-3-4-5)
                if set([14, 2, 3, 4, 5]).issubset(set(unique_ranks)):
                    return 5
        return 0

    @staticmethod
    def _is_four_of_a_kind(cards: List[Card]) -> List[int]:
        rank_count = {}
        for card in cards:
            rank_count[card.rank.value] = rank_count.get(card.rank.value, 0) + 1
        
        for rank, count in rank_count.items():
            if count == 4:
                # Находим кикер (самую старшую карту кроме каре)
                kicker = max(r for r in rank_count.keys() if r != rank)
                return [rank, kicker]
        return []

    @staticmethod
    def _is_full_house(cards: List[Card]) -> List[int]:
        rank_count = {}
        for card in cards:
            rank_count[card.rank.value] = rank_count.get(card.rank.value, 0) + 1
        
        # Ищем тройку и пару
        three_of_kind = None
        pair = None
        
        for rank, count in sorted(rank_count.items(), key=lambda x: (x[1], x[0]), reverse=True):
            if count >= 3 and three_of_kind is None:
                three_of_kind = rank
            elif count >= 2 and pair is None and rank != three_of_kind:
                pair = rank
        
        if three_of_kind and pair:
            return [three_of_kind, pair]
        return []

    @staticmethod
    def _is_flush(cards: List[Card]) -> List[int]:
        suits = {}
        for card in cards:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card.rank.value)
        
        for suit, ranks in suits.items():
            if len(ranks) >= 5:
                # Возвращаем 5 старших карт флеша
                return sorted(ranks, reverse=True)[:5]
        return []

    @staticmethod
    def _is_straight(cards: List[Card]) -> int:
        unique_ranks = sorted(set(c.rank.value for c in cards), reverse=True)
        
        # Проверяем обычные стриты
        for i in range(len(unique_ranks) - 4):
            if unique_ranks[i] - unique_ranks[i+4] == 4:
                return unique_ranks[i]
        
        # Проверяем стрит с тузом как 1
        if set([14, 2, 3, 4, 5]).issubset(set(unique_ranks)):
            return 5
        
        return 0

    @staticmethod
    def _is_three_of_a_kind(cards: List[Card]) -> List[int]:
        rank_count = {}
        for card in cards:
            rank_count[card.rank.value] = rank_count.get(card.rank.value, 0) + 1
        
        for rank, count in sorted(rank_count.items(), key=lambda x: x[0], reverse=True):
            if count == 3:
                # Находим два кикера
                kickers = sorted([r for r in rank_count.keys() if r != rank], reverse=True)[:2]
                return [rank] + kickers
        return []

    @staticmethod
    def _is_two_pair(cards: List[Card]) -> List[int]:
        rank_count = {}
        for card in cards:
            rank_count[card.rank.value] = rank_count.get(card.rank.value, 0) + 1
        
        pairs = []
        for rank, count in sorted(rank_count.items(), key=lambda x: x[0], reverse=True):
            if count >= 2 and len(pairs) < 2:
                pairs.append(rank)
        
        if len(pairs) == 2:
            # Находим кикер
            kicker = max(r for r in rank_count.keys() if r not in pairs)
            return pairs + [kicker]
        return []

    @staticmethod
    def _is_one_pair(cards: List[Card]) -> List[int]:
        rank_count = {}
        for card in cards:
            rank_count[card.rank.value] = rank_count.get(card.rank.value, 0) + 1
        
        for rank, count in sorted(rank_count.items(), key=lambda x: x[0], reverse=True):
            if count == 2:
                # Находим три кикера
                kickers = sorted([r for r in rank_count.keys() if r != rank], reverse=True)[:3]
                return [rank] + kickers
        return []

    @staticmethod
    def compare_hands(hand1: Tuple[HandRank, List[int]], hand2: Tuple[HandRank, List[int]]) -> int:
        """Сравнивает две руки, возвращает 1 если hand1 сильнее, -1 если hand2 сильнее, 0 если ничья"""
        if hand1[0].value > hand2[0].value:
            return 1
        elif hand1[0].value < hand2[0].value:
            return -1
        else:
            for i in range(len(hand1[1])):
                if hand1[1][i] > hand2[1][i]:
                    return 1
                elif hand1[1][i] < hand2[1][i]:
                    return -1
            return 0