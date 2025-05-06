function deleteList(listId) {
    if (confirm('Are you sure you want to delete this list and all its cards?')) {
        fetch(`/list/${listId}/delete`, { method: 'POST' })
            .then(() => window.location.reload());
    }
}

function toggleCard(cardId) {
    fetch(`/card/${cardId}/toggle`, { method: 'POST' })
        .then(() => window.location.reload());
}

function renameBoard(boardId, newName) {
    fetch(`/board/${boardId}/rename`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newName.trim() }),
    }).then(response => response.json())
      .then(data => {
          if (!data.success) {
              alert('Failed to rename board: ' + data.error);
          }
      });
}

function renameList(listId, newName) {
    fetch(`/list/${listId}/rename`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newName.trim() }),
    }).then(response => response.json())
      .then(data => {
          if (!data.success) {
              alert('Failed to rename list: ' + data.error);
          }
      });
}

function renameCard(cardId, newTitle) {
    fetch(`/card/${cardId}/rename`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: newTitle.trim() }),
    }).then(response => response.json())
      .then(data => {
          if (!data.success) {
              alert('Failed to rename card: ' + data.error);
          }
      });
}

function deleteBoard(boardId) {
    if (confirm('Are you sure you want to delete this board and all its lists?')) {
        fetch(`/board/${boardId}/delete`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else if (data.error) {
                    alert('Error: ' + data.error);
                }
            });
    }
}

function deleteCard(cardId) {
    if (confirm('Are you sure you want to delete this card?')) {
        fetch(`/card/${cardId}/delete`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.redirect) {
                window.location.href = data.redirect;
            } else if (data.error) {
                alert('Error: ' + data.error);
            }
        });
    }
}