from fastapi import FastAPI, HTTPException
import json
import uuid
import requests

app = FastAPI()

# Caminho para os arquivos JSON que armazenam os dados

USERS_FILE = "usuarios.json"
ITINERARIES_FILE = "roteiros.json"


# User methods
def read_users():
    try:
        with open(USERS_FILE, "r") as file:
            users_data = file.read()
            if not users_data:
                return []
            return json.loads(users_data)
    except FileNotFoundError:
        return []
    
def write_users(users):
    with open(USERS_FILE, "w") as file:
        json.dump(users, file)

def generate_user_id():
    return str(uuid.uuid4())

def get_user_by_id(user_id: str, users=None):
    if users is None:
        users = read_users()
    for user in users:
        if user["id_usuario"] == user_id:
            return user
    return None


# Coordinates methods
def get_coordinates(cidade):
    endpoint = "https://nominatim.openstreetmap.org/search"
    params = {
        'format': 'json',
        'q': cidade,
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    if data:
        # A resposta pode conter várias correspondências, escolha a primeira
        latitude = float(data[0]['lat'])
        longitude = float(data[0]['lon'])
        return latitude, longitude
    else:
        raise HTTPException(status_code=404, detail=f"Coordenadas não encontradas para a cidade: {cidade}")

def carregar_roteiros():
    try:
        with open(ITINERARIES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"roteiros": []}

def salvar_roteiros(roteiros):
    with open(ITINERARIES_FILE, "w") as file:
        json.dump(roteiros, file, indent=2)


# ITINERARIES
# Rota para adicionar um novo roteiro
@app.post("/itineraries/add")
def adicionar_roteiro(dados_roteiro: dict):
    roteiros = carregar_roteiros()
    roteiros["roteiros"].append(dados_roteiro)
    salvar_roteiros(roteiros)
    return {"message": "Roteiro adicionado com sucesso!"}

# Rota para buscar roteiros pelo ID
@app.get("/itineraries/search-itineraries/{id_roteiro}")
def buscar_roteiro(id_roteiro: str):
    roteiros = carregar_roteiros()
    for roteiro in roteiros["roteiros"]:
        if roteiro["dados_roteiro"]["id_roteiro"] == id_roteiro:
            
            return roteiro
    raise HTTPException(status_code=404, detail="Roteiro não encontrado")


# MAPS
# Retorna coordenadas a partir de uma cidade
@app.get("/maps/coordinates/{cidade}")
def get_coordenadas(cidade: str):
    try:
        coordenadas = get_coordinates(cidade)
        return {"cidade": cidade, "coordenadas": {"latitude": coordenadas[0], "longitude": coordenadas[1]}}
    except HTTPException as e:
        raise e


# USERS
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



# RECOMENDATION
# Recomendation methods
# @app.get("/recomendation/destination/{cidade}")
# def get_coordenadas(cidade: str):