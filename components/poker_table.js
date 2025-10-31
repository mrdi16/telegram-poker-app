// Компонент покерного стола
class PokerTable {
    constructor(app) {
        this.app = app;
        this.container = document.getElementById('players-container');
    }

    renderPlayers(players) {
        this.container.innerHTML = '';
        
        // Создаем сетку игроков
        players.forEach((player, index) => {
            const playerElement = this.createPlayerElement(player, index);
            this.container.appendChild(playerElement);
        });
    }

    createPlayerElement(player, index) {
        const playerDiv = document.createElement('div');
        playerDiv.className = 'player-card';
        
        // Добавляем классы состояния
        if (player.folded) playerDiv.classList.add('folded');
        if (player.all_in) playerDiv.classList.add('all-in');
        if (player.is_current) playerDiv.classList.add('active');
        
        // Позиция за столом
        const positions = ['top-left', 'top-right', 'right-top', 'right-bottom', 'bottom-right', 'bottom-left'];
        playerDiv.classList.add(positions[index % positions.length]);
        
        playerDiv.innerHTML = this.getPlayerHTML(player);
        return playerDiv;
    }

    getPlayerHTML(player) {
        return `
            <div class="player-header">
                <span class="player-name">${player.username}</span>
                ${player.is_admin ? '<span class="admin-badge">👑</span>' : ''}
            </div>
            <div class="player-chips">$${player.chips.toFixed(1)}</div>
            <div class="player-bet">${player.current_bet > 0 ? `Ставка: $${player.current_bet}` : ''}</div>
            <div class="player-status">
                ${player.folded ? '📤 Фолд' : ''}
                ${player.all_in ? '🔥 All-in' : ''}
                ${!player.folded && !player.all_in && player.is_current ? '⭐ Ходит' : ''}
            </div>
            <div class="player-cards">
                ${this.renderPlayerCards(player)}
            </div>
        `;
    }

    renderPlayerCards(player) {
        if (player.folded || !player.hole_cards) {
            return '<div class="card-back">🂠</div><div class="card-back">🂠</div>';
        }
        
        // Если это текущий игрок, показываем карты
        if (player.user_id === this.app.user.id) {
            return player.hole_cards.map(card => 
                `<div class="mini-card ${this.getCardClass(card)}">${card}</div>`
            ).join('');
        }
        
        // Для других игроков показываем рубашку
        return '<div class="card-back">🂠</div><div class="card-back">🂠</div>';
    }

    getCardClass(cardStr) {
        const suit = cardStr.slice(-1);
        const suitMap = {
            '♥': 'hearts',
            '♦': 'diamonds',
            '♣': 'clubs', 
            '♠': 'spades'
        };
        return suitMap[suit] || '';
    }

    updateCommunityCards(cards) {
        const container = document.getElementById('community-cards');
        container.innerHTML = '';
        
        cards.forEach(cardStr => {
            const cardElement = document.createElement('div');
            cardElement.className = `card ${this.getCardClass(cardStr)}`;
            cardElement.textContent = cardStr;
            container.appendChild(cardElement);
        });
    }

    updatePot(amount) {
        document.getElementById('pot-amount').textContent = amount.toFixed(1);
    }

    updateCurrentBet(amount) {
        document.getElementById('current-bet').textContent = amount.toFixed(1);
    }
}