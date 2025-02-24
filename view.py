from flask import Flask, jsonify, request
from main import app, con
from flask_bcrypt import Bcrypt
import re

bcrypt = Bcrypt(app)  # Inicializa o bcrypt para criptografia segura

def validar_senha(senha):
    padrao = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
    return bool(re.fullmatch(padrao, senha))


@app.route('/usuario', methods=['GET'])
def usuario():
    cur = con.cursor()
    cur.execute('SELECT id_usuarios, nome, email, senha, telefone, data_nascimento FROM usuarios')
    usuarios = cur.fetchall()
    usuarios_dic = []
    for usuario in usuarios:
        usuarios_dic.append({
            'id_usuarios': usuario[0],
            'nome': usuario[1],
            'email': usuario[2],
            'senha': usuario[3],
            'telefone': usuario[4],
            'data_nascimento': usuario[5]
        })
    return jsonify(mensagem='Lista de Usuarios', usuarios=usuarios_dic)


@app.route('/usuarios', methods=['POST'])
def usuario_post():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    telefone = data.get('telefone')
    data_nascimento = data.get('data_nascimento')

    if not validar_senha(senha):
        return jsonify({"error": "A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais."}), 404

    cursor = con.cursor()

    cursor.execute('SELECT 1 FROM USUARIOS WHERE NOME = ?', (nome,))

    if cursor.fetchone():
        return jsonify('Usuario já cadastrado')

    senha = bcrypt.generate_password_hash(senha).decode('utf-8')

    cursor.execute('INSERT INTO USUARIOS(NOME, EMAIL, SENHA, TELEFONE, DATA_NASCIMENTO) VALUES (?,?,?,?,?)',
                   (nome, email, senha, telefone, data_nascimento))

    con.commit()
    cursor.close()

    return jsonify({
        'message': 'Usuario cadastrado com sucesso!',
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha,
            'telefone': telefone,
            'data_nascimento': data_nascimento
        }
    })


@app.route('/usuarios/<int:id>', methods=['PUT'])
def usuario_put(id):
    cursor = con.cursor()
    cursor.execute('SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS WHERE ID_USUARIO = ?', (id,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        cursor.close()
        return jsonify({'Usuario não foi encontrado'})

    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')
    telefone = data.get('telefone')
    data_nascimento = data.get('data_nascimento')

    # Validação da senha
    if not validar_senha(senha):
        return jsonify({"error": "A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais."}), 404

    cursor.execute('UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ?, TELEFONE = ?, DATA_NASCIMENTO = ? WHERE ID_USUARIO = ?',
                   (nome, email, senha, telefone, data_nascimento, id))

    con. commit()
    cursor.close()

    return jsonify({
        'message': 'Usuario editado com sucesso!',
        'usuario': {
            'id_usuarios': id,
            'nome': nome,
            'email': email,
            'senha': senha,
            'telefone': telefone,
            'data_nascimento': data_nascimento
        }
    })


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    cursor = con.cursor()

    cursor.execute('SELECT SENHA FROM usuarios WHERE EMAIL = ?', (email,))
    senha_crip = cursor.fetchone()
    cursor.close()

    if not senha_crip:
        return jsonify({"error": "Usuário não encontrado"}), 404

    senha_hash = senha_crip[0]

    if bcrypt.check_password_hash(senha_hash, senha):
        return jsonify({"message": "Login realizado com sucesso"}), 200
    return jsonify({"error": "email ou senha invalidos"}), 401

