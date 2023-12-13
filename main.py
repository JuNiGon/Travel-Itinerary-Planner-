from fastapi import FastAPI, HTTPException
import json
import uuid
import requests

app = FastAPI()

INFORMACOES_DESTINOS_FILE = "informacoes_destinos.json"
USERS_FILE = "usuarios.json"
ITINERARIES_FILE = "roteiros.json"

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

def obter_informacoes_cidade(nome_cidade):
    try:
        # Carregar dados do arquivo informacoes_destinos.json
        with open(INFORMACOES_DESTINOS_FILE, 'r', encoding='utf-8') as file:
            destinos = json.load(file)

        # Buscar informações da cidade no novo formato JSON
        cidade_info = next((destino for destino in destinos["destinos"] if destino["cidade"] == nome_cidade), None)

        if cidade_info is None:
            raise HTTPException(status_code=404, detail=f"Informações não encontradas para a cidade '{nome_cidade}'")

        # Retornar as informações
        return {'informacoes_cidade': cidade_info}

    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Arquivo de dados não encontrado")

def get_coordinates(cidade):
    endpoint = "https://nominatim.openstreetmap.org/search"
    params = {
        'format': 'json',
        'q': cidade,
    }

    response = requests.get(endpoint, params=params)
    data = response.json()

    if data:
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

@app.post("/itineraries/add")
def adicionar_roteiro(dados_roteiro: dict):
    roteiros = carregar_roteiros()
    roteiros["roteiros"].append(dados_roteiro)
    salvar_roteiros(roteiros)
    return {"message": "Roteiro adicionado com sucesso!"}

@app.get("/itineraries/search-itineraries/{nome_da_cidade}")
def buscar_roteiro(nome_da_cidade: str):
    roteiros = carregar_roteiros()
    roteiros_cidade = []
    for roteiro in roteiros["roteiros"]:
        if roteiro["dados_roteiro"]["nome_da_cidade"] == nome_da_cidade:
            nome_cidade = roteiro["dados_roteiro"]["nome_da_cidade"]
            roteiros_cidade = [r for r in roteiros["roteiros"] if r["dados_roteiro"]["nome_da_cidade"] == nome_cidade]
            if not roteiros_cidade:
                raise HTTPException(status_code=404, detail="Roteiro não encontrado")  
            # Encontrar o roteiro com a maior nota
            roteiro_maior_nota = max(roteiros_cidade, key=lambda x: x["dados_roteiro"]["nota"])
            return roteiro_maior_nota
    raise HTTPException(status_code=404, detail="Roteiro não encontrado")


@app.get("/maps/coordinates/")
def get_coordenadas(cidade_origem: str, cidade_destino: str):
    try:
        coordenadas_origem = get_coordinates(cidade_origem)
        coordenadas_destino = get_coordinates(cidade_destino)
        return {
            "cidades": [
                {"cidade_origem": cidade_origem, "coordenadas": {"latitude": coordenadas_origem[0], "longitude": coordenadas_origem[1]}},
                {"cidade_destino": cidade_destino, "coordenadas": {"latitude": coordenadas_destino[0], "longitude": coordenadas_destino[1]}}
            ]   
        }
    except HTTPException as e:
        raise e

@app.get("/user/personalized-recommendations/{user_id}")
async def personalized_recommendations(user_id: str):
    users = read_users()
    user = get_user_by_id(user_id, users)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    cidade_origem_usuario = user["dados_voo"]["origem"]
    # Verificar se existem roteiros na mesma cidade
    roteiros = carregar_roteiros()["roteiros"]
    roteiros_na_mesma_cidade = [r for r in roteiros if r["dados_roteiro"]["nome_da_cidade"] == cidade_origem_usuario]
    if roteiros_na_mesma_cidade:
        return {"recomendacoes": roteiros_na_mesma_cidade}
    else:
        # Se não houver roteiros na mesma cidade, retornar o roteiro com a maior nota
        roteiro_maior_nota = max(roteiros, key=lambda x: x["dados_roteiro"]["nota"])
        return {"recomendacoes": [roteiro_maior_nota]}

@app.get("/user/get_users")
async def get_users():
    return read_users()

@app.post("/user/add")
async def add_user(user_data: dict):
    user_id = generate_user_id()

    # Adicionando os novos campos e valores
    user_data["dados_voo"]["valor_voo"] = user_data["dados_voo"].get("valor_voo", 0)
    user_data["dados_hotel"]["valor_hotel"] = user_data["dados_hotel"].get("valor_hotel", 0)
    user_data["dados_roteiro"]["valor_roteiro"] = user_data["dados_roteiro"].get("valor_roteiro", 0)
    user_data["dados_do_usuario"]["valor_total"] = (
    user_data["dados_voo"]["valor_voo"]
    + user_data["dados_hotel"]["valor_hotel"]
    + user_data["dados_roteiro"]["valor_roteiro"]
)

    user_data["id_usuario"] = user_id

    users = read_users()
    users.append(user_data)
    write_users(users)

    return {"message": "Usuário adicionado com sucesso!", "id_usuario": user_id}

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

@app.post("/user/copy-itinerary/{id_usuario_1}/{id_usuario_2}")
async def copy_itinerary(id_usuario_1: str, id_usuario_2: str):
    users = read_users()

    usuario_1 = get_user_by_id(id_usuario_1, users)
    usuario_2 = get_user_by_id(id_usuario_2, users)

    if usuario_1 is None or usuario_2 is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Copiar itinerário do usuário 2 para o usuário 1
    usuario_1["dados_voo"] = usuario_2["dados_voo"]
    usuario_1["dados_hotel"] = usuario_2["dados_hotel"]
    usuario_1["dados_roteiro"] = usuario_2["dados_roteiro"]

    # Atualizar o valor total com base nos novos valores
    usuario_1["dados_do_usuario"]["valor_total"] = (
        usuario_1["dados_voo"]["valor_voo"]
        + usuario_1["dados_hotel"]["valor_hotel"]
        + usuario_1["dados_roteiro"]["valor_roteiro"]
    )

    # Salvar as alterações
    write_users(users)

    return {"message": "Itinerário copiado com sucesso"}

@app.get("/cidade/{nome_cidade}")
def get_informacoes_cidade(nome_cidade: str):
    try:
        informacoes_cidade = obter_informacoes_cidade(nome_cidade)
        return informacoes_cidade
    except HTTPException as e:
        return {"Informação não encontrada": str(e)}