import fdb

class USUARIOS:
    def __init__(self, id_usuario, nome, email, senha, telefone, data_nascimento, multa, cargo, status):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email
        self.senha = senha
        self.telefone = telefone
        self.data_nascimento = data_nascimento
        self.multa = multa
        self.cargo = cargo
        self.status = status
