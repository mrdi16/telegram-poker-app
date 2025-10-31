// Компонент админской панели
class AdminPanel {
    constructor(app) {
        this.app = app;
        this.container = document.getElementById('admin-panel');
        this.infoContainer = document.getElementById('admin-info');
    }

    init() {
        if (this.app.isAdmin) {
            this.show();
        } else {
            this.hide();
        }
    }

    show() {
        this.container.classList.remove('hidden');
    }

    hide() {
        this.container.classList.add('hidden');
    }

    async showAllCards() {
        try {
            const response = await this.app.sendToBot('admin_show_cards');
            this.displayCardsInfo(response.cards);
        } catch (error) {
            this.showError('Ошибка получения карт');
        }
    }

    async showWinProbabilities() {
        try {
            const response = await this.app.sendToBot('admin_win_probabilities');
            this.displayProbabilitiesInfo(response.probabilities);
        } catch (error) {
            this.showError('Ошибка расчета вероятностей');
        }
    }

    displayCardsInfo(cards) {
        let html = '<h4>Карты всех игроков:</h4>';
        
        for (const [playerName, playerCards] of Object.entries(cards)) {
            html += `<div class="player-cards-info">
                <strong>${playerName}:</strong> ${playerCards.join(', ')}
            </div>`;
        }
        
        this.infoContainer.innerHTML = html;
    }

    displayProbabilitiesInfo(probabilities) {
        let html = '<h4>Вероятности победы:</h4>';
        
        for (const [playerName, probability] of Object.entries(probabilities)) {
            html += `<div class="probability-info">
                <strong>${playerName}:</strong> ${probability}%
            </div>`;
        }
        
        this.infoContainer.innerHTML = html;
    }

    showChipManagement() {
        this.infoContainer.innerHTML = `
            <h4>Управление фишками</h4>
            <div class="chip-management">
                <input type="text" id="chip-player" placeholder="Имя игрока">
                <input type="number" id="chip-amount" placeholder="Сумма">
                <select id="chip-action">
                    <option value="add">Добавить</option>
                    <option value="remove">Убрать</option>
                    <option value="set">Установить</option>
                </select>
                <button onclick="handleChipAction()">Применить</button>
            </div>
        `;
    }

    showError(message) {
        this.infoContainer.innerHTML = `<div class="error-message">${message}</div>`;
    }

    clearInfo() {
        this.infoContainer.innerHTML = '';
    }
}

// Глобальные функции для админской панели
function handleChipAction() {
    const playerName = document.getElementById('chip-player').value;
    const amount = parseFloat(document.getElementById('chip-amount').value);
    const action = document.getElementById('chip-action').value;
    
    if (!playerName || !amount) {
        alert('Заполните все поля');
        return;
    }
    
    window.pokerApp.performChipAction(playerName, amount, action);
}