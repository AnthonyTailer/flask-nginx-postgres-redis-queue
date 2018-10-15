from flask import request, jsonify, g

from app.api.auth import token_auth
from app.models import User, EnumType, RevokedToken, UserSchema
from app.api import bp
from flask import current_app
from app.api.errors import bad_request
from app import db


@bp.route('/registration', methods=['POST'])
def user_registration():
    data = request.get_json(silent=True) or {}

    if 'username' not in data or 'fullname' not in data or 'password' not in data or 'type' not in data:
        return bad_request('Os campos username, fullname, password e type são obrigatórios')

    if User.find_by_username(data['username']):
        return bad_request('Usuário {} já esta em uso'.format(data['username']))

    try:
        if data['type'] in EnumType.__members__:
            user_type = EnumType[data['type']].__str__()
        else:
            user_type = EnumType.anonymous.__str__()
    except (Exception, KeyError, LookupError) as e:
        return bad_request('Tipo de usuário inválido, {}'.format(e))

    new_user = User(
        username=data['username'],
        fullname=data['fullname'],
        password=User.generate_hash(data['password']),
        type=user_type
    )
    try:
        new_user.save_to_db()
        msg = 'Usuário {} criado com sucesso'.format(data['username'])
        current_app.logger.info(msg)
        db.session.commit()
        return jsonify({
            'message': msg,
            'login': 'api/login'
        }), 201
    except Exception as e:
        db.session.rollback()
        current_app.logger.error('Error {}'.format(e))
        return jsonify({'message': 'Algo de errado não está certo'}), 500


@bp.route('/login', methods=['POST'])
def user_login():
    data = request.get_json(silent=True) or {}

    if 'username' not in data or 'password' not in data:
        return bad_request('Os campos username e password são obrigatórios')

    current_user = User.find_by_username(data['username'])
    if not current_user:
        return bad_request('Usuário {} inexistente'.format(data['username']))

    if User.verify_hash(data['password'], current_user.password):
        access_token = current_user.get_token()
        db.session.commit()
        return jsonify({
            'message': 'Logado como {}'.format(current_user.username),
            'token': access_token,
            'info': 'api/user'
        }), 200
    else:
        return jsonify({'message': 'Senha ou usuário incorretos'}), 400


@bp.route('/logout', methods=['POST'])
@token_auth.login_required
def user_logout():
    token = g.current_user.token
    try:
        revoked_token = RevokedToken(token=token)
        revoked_token.add()
        db.session.commit()
        msg = 'O seu token de acesso foi revogado com sucesso'
        current_app.logger.info(msg)

        return jsonify({'message': msg}), 200
    except Exception as e:
        msg = 'Algo de errado não está certo, {}'.format(e)
        current_app.logger.error(msg)
        return jsonify({'message': msg}), 500


# @bp.route('/task', methods=['GET'])
# @jwt_required
# def test():
#     username = get_jwt_identity()
#     current_user = User.find_by_username(username)
#     task = current_user.launch_task('test_task', 'TEST Evaluation', current_user.id)
#     return jsonify({
#                'message': 'JOB criada com sucesso',
#                'data': {
#                    'task': task.id,
#                    'url': 'api/task/' + str(task.id),
#                }
#            }), 201


@bp.route('/password/change', methods=['POST'])
@token_auth.login_required
def user_change_pass():
    username = g.current_user.username
    data = request.get_json(silent=True) or {}
    current_user = g.current_user

    if 'current_password' not in data or 'new_password' not in data:
        return bad_request('Os campos current_password e new_password são obrigatórios')
    if not current_user:
        return bad_request('Usuário {} inexistente'.format(data['username']))

    if User.verify_hash(data['current_password'], current_user.password):
        try:
            User.change_password(username, data['new_password'])
            msg = 'Senha alterada com sucesso'
            current_app.logger.info(msg)
            try:
                g.current_user.revoke_token()
                db.session.commit()
                return jsonify({
                    'message': msg,
                }), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': 'Algo de errado não está certo, {}'.format(e)}), 500
        except Exception as e:
            db.session.rollback()
            current_app.logger.error('Error {}'.format(e))
            return jsonify({'message': 'Algo de errado não está certo'}), 500
    return jsonify({'message': 'A senha atual não está correta'}), 422


@bp.route('/user', methods=['PUT', 'GET'])
@token_auth.login_required
def user_info_change():

    if request.method == 'GET':
        user_schema = UserSchema()
        output = user_schema.dump(g.current_user).data
        return jsonify(output), 200

    elif request.method == 'PUT':
        data = request.get_json(silent=True) or {}
        if 'username' not in data or 'fullname' not in data or 'type' not in data:
            return bad_request('Os campos username, fullname e type são obrigatórios')

        current_user = g.current_user
        new_user = User.find_by_username(data['username'])

        if not current_user:
            return bad_request('Usuário {} inexistente'.format(data['username']))

        if new_user:
            if (new_user.username != current_user.username) and (new_user.id != current_user.id):
                return bad_request('Usuário {} já esta em uso'.format(data['username']))

        try:
            current_user.update_to_db(data['username'], data['fullname'], data['type'])
            current_app.logger.info('Usuário alterado com sucesso')
            try:
                if data['username'].strip() != current_user.username.strip():
                    g.current_user.revoke_token()
                db.session.commit()
                return jsonify({
                    'message': 'Usuário alterado com sucesso',
                }), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({'message': 'Algo de errado não está certo, {}'.format(e)}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': 'Algo de errado não está certo, {}'.format(e)}), 500
    else:
        return bad_request({'msg': 'Método não permitido'})