document.addEventListener('DOMContentLoaded', function () {

    let gameStatus = "waiting";

    document.body.addEventListener('htmx:wsOpen', function(event) {
        var username = localStorage.getItem("username");
        const ws = event.detail.socketWrapper;

        setTimeout(() => {
            ws.send(JSON.stringify({
                'type': 'game.join',
                'data': "join_game",
                'username': username
            }));
        }, 100);

        document.addEventListener('DOMContentLoaded', function () {
            history.pushState(null, null, `/`);
            
        });

        document.getElementById('fibonacci-cards').addEventListener('click', function(event) {
            if (event.target.tagName === 'BUTTON' && gameStatus === "started") {
                const cardValue = event.target.value;

                resetFibonacciCards();
                updateSelectedCardStyle(event.target);

                const wsData = {
                    type: 'select.card',
                    data: cardValue,
                    username: username
                };

                ws.send(JSON.stringify(wsData));
            }
        });

        document.getElementById('copy-room-link').addEventListener('click', function() {
            const roomLink = window.location.href;
            const tempInput = document.createElement('input');
            const gameId = document.getElementById('game-id-var').value;
            tempInput.value = roomLink + "invite/" + gameId;
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
        });

        document.getElementById('reveal-cards').addEventListener('click', function() {
            const wsData = {
                type: 'reveal.cards',
                data: "reveal",
                username: username
            };
            ws.send(JSON.stringify(wsData));
        });

        document.getElementById('start-game').addEventListener('click', function() {
            const wsData = {
                type: 'game.start',
                data: "start",
                username: username
            };
            ws.send(JSON.stringify(wsData));
        });

        document.getElementById('end-game').addEventListener('click', function() {
            const wsData = {
                type: 'game.end',
                data: "end",
                username: username
            };
            ws.send(JSON.stringify(wsData));
        });

    });

    document.body.addEventListener('htmx:wsBeforeMessage', handleWsBeforeMessage);

    function handleWsBeforeMessage(event) {
        const messageString = event.detail.message;
        try {
            const message = JSON.parse(messageString);
            if (message.type === "game.join" || message.type === "game.leave") {
                updatePlayersInfo(message.data.players);
            } else if (message.type === 'reveal.cards') {
                gameStatus = "revealed";
                updatePlayersInfo(message.data, true);
            } else if (message.type === 'select.card') {
                updatePlayersInfo(message.data, false);
            } else if (message.type === 'game.start') {
                gameStatus = "started";
            } else if (message.type === 'game.end') {
                gameStatus = "waiting";
                updatePlayersInfo(message.data, false);
                resetFibonacciCards();
            }
            handleInformationMessage();
        } catch (error) {
            console.error("Error parsing message:", error);
        }
    }

    function resetFibonacciCards() {
        document.querySelectorAll('#fibonacci-cards button').forEach(button => {
            button.classList.remove('bg-blue-500', 'text-white');
            button.classList.add('text-blue-500');
            button.style.transform = 'translateY(0)';
        });
    }

    function updateSelectedCardStyle(target) {
        target.classList.remove('text-blue-500');
        target.classList.toggle('bg-blue-500');
        target.classList.toggle('text-white', 'min-w-20');
        target.style.transform = 'translateY(-10px)';
        target.style.transition = 'transform 0.5s';
    }

    function updatePlayersInfo(players, show) {
        const playersInfoDiv = document.getElementById('players-info');
        playersInfoDiv.innerHTML = '';

        for (const [username, value] of Object.entries(players)) {
            const cardContainerDiv = document.createElement('div');
            cardContainerDiv.className = 'mx-4 flex flex-col items-center mt-2';

            const cardDiv = createCardDiv(username, value, show);
            const playerNameSpan = createPlayerNameSpan(username);

            cardContainerDiv.appendChild(cardDiv);
            cardContainerDiv.appendChild(playerNameSpan);
            playersInfoDiv.appendChild(cardContainerDiv);
        }
    }

    function createCardDiv(username, value, show) {
        const cardDiv = document.createElement('div');
        cardDiv.className = getCardDivClassName(value);

        if (show) {
            const cardNumberSpan = document.createElement('span');
            cardNumberSpan.textContent = value;
            cardNumberSpan.className = 'block text-center text-2xl font-bold';
            cardDiv.appendChild(cardNumberSpan);
        }

        return cardDiv;
    }

    function getCardDivClassName(value) {
        if (value === null) {
            return 'mx-2 text-blue-500 bg-blue-500 border-solid border-2 p-6 h-28 min-w-20 rounded-lg text-xl flex items-center justify-center';
        } else {
            return 'mx-2 text-blue-500 border-blue-500 border-solid border-2 p-6 h-28 min-w-20 rounded-lg text-xl flex items-center justify-center';
        }
    }

    function createPlayerNameSpan(username) {
        const playerNameSpan = document.createElement('span');
        playerNameSpan.textContent = username;
        playerNameSpan.className = 'block text-center text-xs text-gray-600';
        return playerNameSpan;
    }

    function handleInformationMessage() {
        if (gameStatus === "waiting") {
            document.getElementById('game-status-text').textContent = "Wait for the game start 🤖";
        } else if (gameStatus === "started") {
            document.getElementById('game-status-text').textContent = "Choose your card 👇";
        } else if (gameStatus === "revealed") {
            document.getElementById('game-status-text').textContent = "Cards revealed, wait for next turn 🃏";
        }
    }
});