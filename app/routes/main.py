from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify 
from flask_login import login_required, current_user
from app.models import Board, List, Comment, board_members, Card, db, User, BoardPermission
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
@login_required
def index():
    boards = current_user.boards.all()
    return render_template('index.html', boards=boards)

@main.route('/board/new', methods=['POST'])
@login_required
def new_board():
    name = request.form.get('name')
    if name:
        board = Board(name=name, owner=current_user)
        db.session.add(board)
        db.session.commit()
        flash('Board created successfully!', 'success')
    return redirect(url_for('main.index'))

@main.route('/board/<int:id>')
@login_required
def view_board(id):
    board = Board.query.get_or_404(id)
    if board.owner != current_user and current_user not in board.members:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('board.html', board=board, active_board=board)

@main.route('/board/<int:board_id>/list/new', methods=['POST'])
@login_required
def new_list(board_id):
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    name = request.form.get('name')
    if name:
        position = len(board.lists.all())
        list = List(name=name, board=board, position=position)
        db.session.add(list)
        db.session.commit()
        flash('List created successfully!', 'success')
    return redirect(url_for('main.view_board', id=board_id))

# Helper function to check permissions
def check_board_permission(board, user, required_permission):
    if user == board.owner:
        return True
        
    member_permission = db.session.query(board_members.c.permission).\
        filter(board_members.c.board_id == board.id).\
        filter(board_members.c.user_id == user.id).\
        scalar()
        
    if not member_permission:
        return False
        
    permission_levels = {
        BoardPermission.VIEW: 1,
        BoardPermission.EDIT: 2,
        BoardPermission.MANAGE: 3
    }
    
    return permission_levels[member_permission] >= permission_levels[required_permission]

@main.route('/list/<int:list_id>/card/new', methods=['POST'])
@login_required
def new_card(list_id):
    list = List.query.get_or_404(list_id)
    if not check_board_permission(list.board, current_user, BoardPermission.EDIT):
        flash('Permission denied.', 'danger')
        return redirect(url_for('main.view_board', id=list.board.id))
    
    title = request.form.get('title')
    description = request.form.get('description')
    due_date_str = request.form.get('due_date')
    
    if title:
        # Get max position
        max_position = db.session.query(db.func.max(Card.position)).filter_by(list_id=list_id).scalar() or 0
        
        card = Card(
            title=title,
            description=description,
            list_id=list_id,
            position=max_position + 1
        )
        
        if due_date_str:
            try:
                card.due_date = datetime.strptime(due_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                pass
                
        db.session.add(card)
        db.session.commit()
        flash('Card created successfully!', 'success')
        
    return redirect(url_for('main.view_board', id=list.board.id))

@main.route('/list/<int:id>/delete', methods=['POST'])
@login_required
def delete_list(id):
    list = List.query.get_or_404(id)
    if list.board.owner != current_user:
        return 'Access denied', 403
    
    db.session.delete(list)
    db.session.commit()
    return '', 204

@main.route('/card/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_card(id):
    card = Card.query.get_or_404(id)
    if card.list.board.owner != current_user:
        return 'Access denied', 403
    
    card.completed = not card.completed
    db.session.commit()
    return '', 204

@main.route('/board/position', methods=['POST'])
@login_required
def update_board_position():
    data = request.get_json()
    board_id = data.get('board_id')
    new_position = data.get('position')
    
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403
    
    # Update positions for all affected boards
    boards = current_user.boards.order_by(Board.position).all()
    for i, b in enumerate(boards):
        if i == new_position:
            board.position = i
        elif b.id != board_id:
            b.position = i
    
    db.session.commit()
    return jsonify({'success': True})

@main.route('/list/position', methods=['POST'])
@login_required
def update_list_position():
    data = request.get_json()
    list_id = data.get('list_id')
    new_position = data.get('position')
    
    list = List.query.get_or_404(list_id)
    if list.board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403
    
    # Update positions for all affected lists
    lists = list.board.lists.order_by(List.position).all()
    for i, l in enumerate(lists):
        if i == new_position:
            list.position = i
        elif l.id != list_id:
            l.position = i
    
    db.session.commit()
    return jsonify({'success': True})

@main.route('/card/position', methods=['POST'])
@login_required
def update_card_position():
    data = request.get_json()
    card_id = data.get('card_id')
    new_list_id = data.get('list_id')
    new_position = data.get('position')
    
    card = Card.query.get_or_404(card_id)
    new_list = List.query.get_or_404(new_list_id)
    
    if new_list.board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403
    
    # Update card's list and position
    card.list_id = new_list_id
    
    # Update positions for all affected cards
    cards = new_list.cards.order_by(Card.position).all()
    for i, c in enumerate(cards):
        if i == new_position:
            card.position = i
        elif c.id != card_id:
            c.position = i
    
    db.session.commit()
    return jsonify({'success': True})

@main.route('/board/<int:board_id>/rename', methods=['POST'])
@login_required
def rename_board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403

    new_name = request.json.get('name')
    if new_name:
        board.name = new_name
        db.session.commit()
        return jsonify({'success': True, 'name': board.name})
    return jsonify({'error': 'Invalid name'}), 400


@main.route('/list/<int:list_id>/rename', methods=['POST'])
@login_required
def rename_list(list_id):
    list = List.query.get_or_404(list_id)
    if list.board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403

    new_name = request.json.get('name')
    if new_name:
        list.name = new_name
        db.session.commit()
        return jsonify({'success': True, 'name': list.name})
    return jsonify({'error': 'Invalid name'}), 400


@main.route('/card/<int:card_id>/rename', methods=['POST'])
@login_required
def rename_card(card_id):
    card = Card.query.get_or_404(card_id)
    if card.list.board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403

    new_title = request.json.get('title')
    if new_title:
        card.title = new_title
        db.session.commit()
        return jsonify({'success': True, 'title': card.title})
    return jsonify({'error': 'Invalid title'}), 400


@main.route('/board/<int:board_id>/delete', methods=['POST'])
@login_required
def delete_board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403

    db.session.delete(board)
    db.session.commit()
    flash('Board deleted successfully!', 'success')
    return jsonify({'redirect': url_for('main.index')})


@main.route('/card/<int:card_id>/delete', methods=['POST'])
@login_required
def delete_card(card_id):
    card = Card.query.get_or_404(card_id)
    
    # Check permissions
    if not check_board_permission(card.list.board, current_user, BoardPermission.EDIT):
        return jsonify({'error': 'Permission denied'}), 403
    
    board_id = card.list.board_id
    db.session.delete(card)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'redirect': url_for('main.view_board', id=board_id)
    })

@main.route('/card/<int:card_id>/details')
@login_required
def get_card_details(card_id):
    card = Card.query.get_or_404(card_id)
    if not check_board_permission(card.list.board, current_user, BoardPermission.VIEW):
        return jsonify({'error': 'Access denied'}), 403
    
    comments = [
        {
            'id': comment.id,
            'text': comment.text,
            'created_at': comment.formatted_date(),
            'user': comment.user.username
        } for comment in card.comments.order_by(Comment.created_at.desc()).all()
    ]
    
    return jsonify({
        'id': card.id,
        'title': card.title,
        'description': card.description,
        'due_date': card.due_date.isoformat() if card.due_date else None,
        'comments': comments,
        'can_edit': check_board_permission(card.list.board, current_user, BoardPermission.EDIT)
    })

@main.route('/card/<int:card_id>/update', methods=['POST'])
@login_required
def update_card(card_id):
    card = Card.query.get_or_404(card_id)
    if not check_board_permission(card.list.board, current_user, BoardPermission.EDIT):
        return jsonify({'error': 'Access denied'}), 403

    data = request.json
    if 'title' in data:
        card.title = data['title']
    if 'description' in data:
        card.description = data['description']
    if 'due_date' in data:
        card.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
    
    db.session.commit()
    return jsonify({'success': True})

@main.route('/card/<int:card_id>/comment', methods=['POST'])
@login_required
def add_comment(card_id):
    card = Card.query.get_or_404(card_id)
    if not check_board_permission(card.list.board, current_user, BoardPermission.EDIT):
        return jsonify({'error': 'Access denied'}), 403

    text = request.json.get('text')
    if text:
        comment = Comment(text=text, user=current_user, card=card)
        db.session.add(comment)
        db.session.commit()
        return jsonify({
            'id': comment.id,
            'text': comment.text,
            'created_at': comment.formatted_date(),
            'user': comment.user.username
        })
    return jsonify({'error': 'Comment text required'}), 400

@main.route('/board/<int:board_id>/share', methods=['POST'])
@login_required
def share_board(board_id):
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403

    email = request.json.get('email')
    permission = request.json.get('permission', 'view')
    
    if not email:
        return jsonify({'error': 'Email required'}), 400

    try:
        permission = BoardPermission(permission)
    except ValueError:
        return jsonify({'error': 'Invalid permission level'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user == current_user:
        return jsonify({'error': 'Cannot share with yourself'}), 400

    if user in board.members:
        stmt = board_members.update().\
               where(board_members.c.user_id == user.id).\
               where(board_members.c.board_id == board.id).\
               values(permission=permission)
        db.session.execute(stmt)
    else:
        stmt = board_members.insert().values(
            user_id=user.id,
            board_id=board.id,
            permission=permission
        )
        db.session.execute(stmt)
    
    db.session.commit()
    return jsonify({
        'success': True,
        'member': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'permission': permission.value
        }
    })

@main.route('/board/<int:board_id>/members/<int:user_id>/permission', methods=['POST'])
@login_required
def update_member_permission(board_id, user_id):
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403

    permission = request.json.get('permission')
    try:
        permission = BoardPermission(permission)
    except ValueError:
        return jsonify({'error': 'Invalid permission level'}), 400

    stmt = board_members.update().\
           where(board_members.c.user_id == user_id).\
           where(board_members.c.board_id == board_id).\
           values(permission=permission)
    db.session.execute(stmt)
    db.session.commit()

    return jsonify({'success': True})

@main.route('/board/<int:board_id>/members')
@login_required
def get_board_members(board_id):
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user and current_user not in board.members:
        return jsonify({'error': 'Access denied'}), 403

    # Get members with their permissions
    members_query = db.session.query(
        User, board_members.c.permission
    ).join(
        board_members, 
        User.id == board_members.c.user_id
    ).filter(
        board_members.c.board_id == board.id
    ).all()

    members = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_owner': user == board.owner,
        'permission': permission.value if permission else None
    } for user, permission in members_query]

    # Add owner at the start
    if board.owner not in [m['id'] for m in members]:
        members.insert(0, {
            'id': board.owner.id,
            'username': board.owner.username,
            'email': board.owner.email,
            'is_owner': True,
            'permission': 'owner'
        })

    return jsonify({'members': members})

@main.route('/board/<int:board_id>/remove-member/<int:user_id>', methods=['POST'])
@login_required
def remove_board_member(board_id, user_id):
    board = Board.query.get_or_404(board_id)
    if board.owner != current_user:
        return jsonify({'error': 'Access denied'}), 403

    user = User.query.get_or_404(user_id)
    if user in board.members:
        board.members.remove(user)
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'error': 'User is not a member'}), 400