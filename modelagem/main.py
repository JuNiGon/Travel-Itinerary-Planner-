from fastapi import FastAPI, HTTPException
import uuid

app = FastAPI()

# Caminho para o arquivo JSON que armazenará os usuários
USERS_FILE = "usuarios.json"


def read_users():
    try:
        with open(USERS_FILE, "r") as file:
            users_data = file.read()
            if not users_data:
                return []
            return eval(users_data)
    except FileNotFoundError:
        return []


def write_users(users):
    with open(USERS_FILE, "w") as file:
        file.write(str(users))


def generate_user_id():
    return str(uuid.uuid4())


def get_user_by_id(user_id: str, users=None):
    if users is None:
        users = read_users()
    for user in users:
        if user["id_usuario"] == user_id:
            return user
    return None


# Ver usuários
@app.get("/user/get_users")
async def get_users():
    return read_users()


# Adicionar usuário
@app.post("/user/add")
async def add_user(user_data: dict):
    user_id = generate_user_id()
    user_data["id_usuario"] = user_id

    users = read_users()
    users.append(user_data)
    write_users(users)
    
    return {"message": "Usuário adicionado com sucesso!", "id_usuario": user_id}


# Editar informações do usuário
@app.post("/user/update/{user_id}")
async def update_user(user_id: str, updated_data: dict):
    users = read_users()
    user_index = None

    for i, user in enumerate(users):
        if user["id_usuario"] == user_id:
            user_index = i
            break

    if user_index is not None:
        users[user_index].update(updated_data)
        write_users(users)
        return {"message": f"Informações do usuário {user_id} atualizadas com sucesso!"}
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")


# Deletar usuário
@app.post("/user/delete/{user_id}")
async def delete_user(user_id: str):
    users = read_users()
    user = get_user_by_id(user_id, users)

    if user:
        users.remove(user)
        write_users(users)
        return {"message": f"Usuário {user_id} deletado com sucesso!"}
    else:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
