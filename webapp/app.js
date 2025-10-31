// Основной файл MiniApp
class PokerApp {
    constructor() {
        this.tg = null;
        this.user = null;
        this.currentTable = null;
        this.gameState = null;
        this.isAdmin = false;
        
        this.init();
    }

    async init() {
        try {
            // Инициализация Telegram Web App
            this.tg = window.Telegram.WebApp;
            this.tg.expand();
            
            // Получаем данные пользователя
            this.user = this.tg.initDataUnsafe.user;
            this.isAdmin = await this.checkAdminStatus();
            
            // Инициализация интерфейса
            this.initUI();
            
            // Показываем главное меню
            this.showScreen('main-menu');
            
        } catch (error) {
            console.error('Ошибка инициализации:', error);
            this.showScreen('main-menu');
        }
    }

    async checkAdminStatus() {
        // Проверяем является ли пользователь админом
        // В реальной реализации здесь будет запрос к бэкенду
        return this.user && this.user.id === 5917286646; // Твой ID
    }

    initUI() {
        // Инициализация компонентов
        this.initPokerTable();
        this.initAdminPanel();
        
        // Скрываем загрузку
        this.hideLoading();
    }

    hideLoading() {
        document.getElementById('loading').classList.remove('active');
    }

    showScreen(screenId) {
        // Скрываем все экраны
        document.querySelectorAll('.screen').forEach(screen => {
            screen.classList.remove('active');
        });
        
        // Показываем нужный экран
        const targetScreen = document.getElementById(screenId);
        if (targetScreen) {
            targetScreen.classList.add('active');
        }
    }

    // Навигация
    showMainMenu() {
        this.showScreen('main-menu');
    }

    showQuickGame() {
        this.showScreen('limit-select');
    }

    showPrivateTable() {
        alert('Приватные столы скоро будут доступны!');
    }

    async showStats() {
        this.showScreen('stats-screen');
        await this.loadStats();
    }

    showRules() {
        this.showScreen('rules-screen');
        this.loadRules();
    }

    // Игровые функции
    async joinTable(limit) {
        try {
            // Отправляем запрос на присоединение к столу
            const response = await this.sendToBot('join_table', { limit });
            
            if (response.success) {
                this.currentTable = { limit };
                await this.startGame();
            } else {
                alert('Ошибка: ' + response.message);
            }
        } catch (error) {
            console.error('Ошибка присоединения к столу:', error);
            alert('Ошибка подключения к игре');
        }
    }

    async startGame() {
        this.showScreen('poker-table');
        
        // Показываем админскую панель если пользователь админ
        if (this.isAdmin) {
            document.getElementById('admin-panel').classList.remove('hidden');
        }
        
        // Запускаем обновление состояния игры
        this.startGameLoop();
    }

    async startGameLoop() {
        // Цикл обновления состояния игры
        setInterval(async () => {
            await this.updateGameState();
        }, 2000); // Обновляем каждые 2 секунды
    }

    async updateGameState() {
        try {
            const gameState = await this.sendToBot('get_game_state');
            if (gameState) {
                this.gameState = gameState;
                this.renderGameState();
            }
        } catch (error) {
            console.error('Ошибка обновления состояния:', error);
        }
    }

    renderGameState() {
        if (!this.gameState) return;

        // Обновляем банк
        document.getElementById('pot-amount').textContent = this.gameState.pot;
        
        // Обновляем текущую ставку
        document.getElementById('current-bet').textContent = this.gameState.current_bet;
        
        // Обновляем общие карты
        this.renderCommunityCards();
        
        // Обновляем карты игроков
        this.renderPlayers();
        
        // Обновляем мои карты
        this.renderMyCards();
        
        // Обновляем доступные действия
        this.updateActions();
    }

    renderCommunityCards() {
        const container = document.getElementById('community-cards');
        container.innerHTML = '';
        
        this.gameState.community_cards.forEach(cardStr => {
            const card = this.createCardElement(cardStr);
            container.appendChild(card);
        });
    }

    renderPlayers() {
        const container = document.getElementById('players-container');
        container.innerHTML = '';
        
        this.gameState.players.forEach(player => {
            const playerElement = this.createPlayerElement(player);
            container.appendChild(playerElement);
        });
    }

    renderMyCards() {
        const container = document.getElementById('hole-cards');
        container.innerHTML = '';
        
        const myPlayer = this.gameState.players.find(p => p.user_id === this.user.id);
        if (myPlayer && myPlayer.hole_cards) {
            myPlayer.hole_cards.forEach(cardStr => {
                const card = this.createCardElement(cardStr);
                container.appendChild(card);
            });
        }
    }

    createCardElement(cardStr) {
        const card = document.createElement('div');
        card.className = 'card';
        
        const suit = cardStr.slice(-1);
        const rank = cardStr.slice(0, -1);
        
        card.textContent = cardStr;
        card.classList.add(this.getSuitClass(suit));
        
        return card;
    }

    createPlayerElement(player) {
        const playerDiv = document.createElement('div');
        playerDiv.className = 'player-card';
        
        if (player.folded) playerDiv.classList.add('folded');
        if (player.is_current) playerDiv.classList.add('active');
        
        playerDiv.innerHTML = `
            <div class="player-name">${player.username}</div>
            <div class="player-chips">$${player.chips}</div>
            <div class="player-bet">Ставка: $${player.current_bet}</div>
            ${player.all_in ? '<div class="player-allin">ALL-IN!</div>' : ''}
        `;
        
        return playerDiv;
    }

    getSuitClass(suit) {
        const suitMap = {
            '♥': 'hearts',
            '♦': 'diamonds', 
            '♣': 'clubs',
            '♠': 'spades'
        };
        return suitMap[suit] || '';
    }

    updateActions() {
        const myPlayer = this.gameState.players.find(p => p.user_id === this.user.id);
        if (!myPlayer) return;

        const actionsPanel = document.getElementById('actions');
        const canAct = !myPlayer.folded && !myPlayer.all_in && myPlayer.is_current;
        
        if (canAct) {
            actionsPanel.style.display = 'block';
        } else {
            actionsPanel.style.display = 'none';
        }
    }

    // Действия игрока
    async makeAction(action, amount = null) {
        try {
            const response = await this.sendToBot('player_action', {
                action: action,
                amount: amount
            });
            
            if (response.success) {
                console.log('Действие выполнено:', response.message);
            } else {
                alert('Ошибка: ' + response.message);
            }
        } catch (error) {
            console.error('Ошибка выполнения действия:', error);
            alert('Ошибка выполнения действия');
        }
    }

    showRaisePanel() {
        document.getElementById('raise-panel').classList.remove('hidden');
    }

    hideRaisePanel() {
        document.getElementById('raise-panel').classList.add('hidden');
    }

    async confirmRaise() {
        const amount = parseFloat(document.getElementById('raise-amount').value);
        if (amount && amount > 0) {
            await this.makeAction('raise', amount);
            this.hideRaisePanel();
        } else {
            alert('Введите корректную сумму');
        }
    }

    // Админские функции
    async adminShowCards() {
        try {
            const response = await this.sendToBot('admin_show_cards');
            this.showAdminInfo(response.cards);
        } catch (error) {
            console.error('Ошибка админской функции:', error);
        }
    }

    async adminWinProbabilities() {
        try {
            const response = await this.sendToBot('admin_win_probabilities');
            this.showAdminInfo(response.probabilities);
        } catch (error) {
            console.error('Ошибка админской функции:', error);
        }
    }

    adminChipManagement() {
        alert('Управление фишками скоро будет доступно в админской панели');
    }

    async adminResetGame() {
        if (confirm('Вы уверены что хотите сбросить текущую игру?')) {
            try {
                const response = await this.sendToBot('admin_reset_game');
                alert(response.message);
            } catch (error) {
                console.error('Ошибка сброса игры:', error);
            }
        }
    }

    showAdminInfo(info) {
        const infoDiv = document.getElementById('admin-info');
        infoDiv.innerHTML = '';
        
        if (typeof info === 'object') {
            for (const [key, value] of Object.entries(info)) {
                const line = document.createElement('div');
                line.textContent = `${key}: ${value}`;
                infoDiv.appendChild(line);
            }
        } else {
            infoDiv.textContent = info;
        }
    }

    // Вспомогательные методы
    async sendToBot(method, data = {}) {
        // В реальной реализации здесь будет запрос к бэкенду
        // Пока используем заглушку
        return await this.mockBotResponse(method, data);
    }

    async mockBotResponse(method, data) {
        // Заглушка для тестирования интерфейса
        await new Promise(resolve => setTimeout(resolve, 500));
        
        const mockResponses = {
            'join_table': { success: true, message: 'Вы присоединились к столу' },
            'get_game_state': this.getMockGameState(),
            'player_action': { success: true, message: 'Действие выполнено' },
            'admin_show_cards': { 
                cards: {
                    'Игрок1': ['A♥', 'K♠'],
                    'Игрок2': ['Q♦', 'J♣'],
                    'Админ': ['10♥', '9♦']
                }
            },
            'admin_win_probabilities': {
                probabilities: {
                    'Игрок1': '45.2%',
                    'Игрок2': '32.1%', 
                    'Админ': '22.7%'
                }
            },
            'admin_reset_game': { success: true, message: 'Игра сброшена' }
        };
        
        return mockResponses[method] || { success: false, message: 'Метод не найден' };
    }

    getMockGameState() {
        return {
            stage: 'preflop',
            pot: 150,
            current_bet: 20,
            community_cards: ['A♥', 'K♠', 'Q♦'],
            players: [
                {
                    username: 'Игрок1',
                    user_id: 123,
                    chips: 980,
                    current_bet: 20,
                    folded: false,
                    all_in: false,
                    is_current: false,
                    hole_cards: ['A♥', 'K♠']
                },
                {
                    username: this.user.first_name,
                    user_id: this.user.id,
                    chips: 1000,
                    current_bet: 0,
                    folded: false,
                    all_in: false,
                    is_current: true,
                    hole_cards: ['10♣', '9♣']
                },
                {
                    username: 'Админ',
                    user_id: 5917286646,
                    chips: 1020,
                    current_bet: 20,
                    folded: false,
                    all_in: false,
                    is_current: false,
                    hole_cards: ['Q♥', 'J♦']
                }
            ]
        };
    }

    async loadStats() {
        const content = document.getElementById('stats-content');
        content.innerHTML = `
            <div class="stat-item">
                <div class="stat-label">Сыграно рук</div>
                <div class="stat-value">42</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Побед</div>
                <div class="stat-value">18</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Процент побед</div>
                <div class="stat-value">42.9%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Самый большой выигрыш</div>
                <div class="stat-value">$1,250</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Текущий баланс</div>
                <div class="stat-value">$2,340</div>
            </div>
        `;
    }

    loadRules() {
        const content = document.querySelector('.rules-content');
        content.innerHTML = `
            <h3>Правила Техасского Холдема</h3>
            <p>Цель игры: собрать лучшую покерную комбинацию из 5 карт.</p>
            
            <h4>Стадии игры:</h4>
            <ul>
                <li><strong>Префлоп:</strong> Раздача карт игрокам</li>
                <li><strong>Флоп:</strong> Выкладываются 3 общие карты</li>
                <li><strong>Тёрн:</strong> 4-я общая карта</li>
                <li><strong>Ривер:</strong> 5-я общая карта</li>
                <li><strong>Вскрытие:</strong> Игроки показывают карты</li>
            </ul>
            
            <h4>Действия:</h4>
            <ul>
                <li><strong>Fold:</strong> Сбросить карты</li>
                <li><strong>Check:</strong> Пропустить ход</li>
                <li><strong>Call:</strong> Уравнять ставку</li>
                <li><strong>Raise:</strong> Поднять ставку</li>
                <li><strong>All-in:</strong> Поставить все фишки</li>
            </ul>
        `;
    }

    initPokerTable() {
        // Инициализация покерного стола
        console.log('Poker table initialized');
    }

    initAdminPanel() {
        // Инициализация админской панели
        console.log('Admin panel initialized');
    }
}

// Глобальные функции для вызова из HTML
function showMainMenu() {
    window.pokerApp.showMainMenu();
}

function showQuickGame() {
    window.pokerApp.showQuickGame();
}

function showPrivateTable() {
    window.pokerApp.showPrivateTable();
}

function showStats() {
    window.pokerApp.showStats();
}

function showRules() {
    window.pokerApp.showRules();
}

function joinTable(limit) {
    window.pokerApp.joinTable(limit);
}

function makeAction(action) {
    window.pokerApp.makeAction(action);
}

function showRaisePanel() {
    window.pokerApp.showRaisePanel();
}

function hideRaisePanel() {
    window.pokerApp.hideRaisePanel();
}

function confirmRaise() {
    window.pokerApp.confirmRaise();
}

// Админские функции
function adminShowCards() {
    window.pokerApp.adminShowCards();
}

function adminWinProbabilities() {
    window.pokerApp.adminWinProbabilities();
}

function adminChipManagement() {
    window.pokerApp.adminChipManagement();
}

function adminResetGame() {
    window.pokerApp.adminResetGame();
}

// Запуск приложения
document.addEventListener('DOMContentLoaded', () => {
    window.pokerApp = new PokerApp();
});