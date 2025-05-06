document.addEventListener('DOMContentLoaded', function() {
    // Initialize Sortable for boards sidebar
    new Sortable(document.getElementById('boardsList'), {
        animation: 150,
        onEnd: function(evt) {
            const boardId = evt.item.getAttribute('data-board-id');
            const newPosition = evt.newIndex;
            updateBoardPosition(boardId, newPosition);
        }
    });

    // Initialize Sortable for lists
    const listContainer = document.querySelector('.list-container');
    if (listContainer) {
        new Sortable(listContainer, {
            animation: 150,
            draggable: '.list',
            handle: '.list-header',
            onEnd: function(evt) {
                const listId = evt.item.getAttribute('data-list-id');
                const newPosition = evt.newIndex;
                updateListPosition(listId, newPosition);
            }
        });
    }

    // Initialize Sortable for cards in each list
    document.querySelectorAll('.cards-container').forEach(container => {
        new Sortable(container, {
            animation: 150,
            group: 'cards',
            onEnd: function(evt) {
                const cardId = evt.item.getAttribute('data-card-id');
                const newListId = evt.to.closest('.list').getAttribute('data-list-id');
                const newPosition = evt.newIndex;
                updateCardPosition(cardId, newListId, newPosition);
            }
        });
    });
});

// API functions for updating positions
function updateBoardPosition(boardId, newPosition) {
    fetch('/board/position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ board_id: boardId, position: newPosition })
    });
}

function updateListPosition(listId, newPosition) {
    fetch('/list/position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ list_id: listId, position: newPosition })
    });
}

function updateCardPosition(cardId, newListId, newPosition) {
    fetch('/card/position', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            card_id: cardId,
            list_id: newListId,
            position: newPosition
        })
    });
}