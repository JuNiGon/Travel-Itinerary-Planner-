from fastapi import FastAPI, HTTPException
import json
import uuid
import requests
from fastapi import Path
from fastapi import FastAPI, Path
from urllib.parse import urljoin

app = FastAPI()

class BaseManagement:
    def __init__(self, file_name):
        self.file_name = file_name

    def read_data(self):
        try:
            with open(self.file_name, "r", encoding="utf-8") as file:
                data = file.read()
                if not data:
                    return []
                return json.loads(data)
        except FileNotFoundError:
            return []

    def write_data(self, data):
        with open(self.file_name, "w") as file:
            json.dump(data, file)

class UserManagement(BaseManagement):
    def __init__(self, users_file="usuarios.json"):
        super().__init__(users_file)

    def generate_user_id(self):
        return str(uuid.uuid4())

    def read_users(self):
        return self.read_data()

    def write_users(self, users):
        self.write_data(users)

    def get_user_by_id(self, user_id):
        users = self.read_users()
        for user in users:
            if user["id_usuario"] == user_id:
                return user
        return None

    def update_user(self, user_id: str, updated_data: dict):
        users = self.read_users()
        user_index = None

        for i, user in enumerate(users):
            if user["id_usuario"] == user_id:
                user_index = i
                break

        if user_index is not None:
            users[user_index].update(updated_data)
            self.write_users(users)
            return {"message": f"Informações do usuário {user_id} atualizadas com sucesso!"}
        else:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

    def delete_user(self, user_id: str):
        users = self.read_users()
        user = self.get_user_by_id(user_id)

        if user:
            users.remove(user)
            self.write_users(users)
            return {"message": f"Usuário {user_id} deletado com sucesso!"}
        else:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")

    def copy_itinerary(self, id_usuario_1: str, id_usuario_2: str):
        users = self.read_users()

        usuario_1 = self.get_user_by_id(id_usuario_1)
        usuario_2 = self.get_user_by_id(id_usuario_2)

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
        self.write_users(users)

        return {"message": "Itinerário copiado com sucesso"}
    
class CityInformation(BaseManagement):
    def __init__(self, city_file="informacoes_destinos.json"):
        super().__init__(city_file)

    def obter_informacoes_cidade(self, nome_cidade):
        try:
            destinos = self.read_data()
            cidade_info = next((destino for destino in destinos["destinos"] if destino["cidade"] == nome_cidade), None)
            if cidade_info is None:
                raise ValueError(f"Informações não encontradas para a cidade '{nome_cidade}'")
            return {'informacoes_cidade': cidade_info}
        except FileNotFoundError:
            raise ValueError("Arquivo de dados não encontrado")

    def get_coordinates(self, cidade):
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
            raise ValueError(f"Coordenadas não encontradas para a cidade: {cidade}")
        
class ItineraryManagement(BaseManagement):
    def __init__(self, itinerary_file="roteiros.json"):
        super().__init__(itinerary_file)

    def carregar_roteiros(self):
        try:
            return self.read_data()
        except FileNotFoundError:
            return {"roteiros": []}

    def salvar_roteiros(self, roteiros):
        self.write_data(roteiros)

    def personalized_recommendations(self, user_id: str):
        users = UserManagement().read_data()
        user = UserManagement().get_user_by_id(user_id)
        
        if user is None:
            raise ValueError("Usuário não encontrado")
        
        cidade_origem_usuario = user["dados_voo"]["origem"]
        roteiros = self.carregar_roteiros()["roteiros"]
        
        roteiros_na_mesma_cidade = [r for r in roteiros if r["dados_roteiro"]["nome_da_cidade"] == cidade_origem_usuario]
        
        if roteiros_na_mesma_cidade:
            return {"recomendacoes": roteiros_na_mesma_cidade}
        else:
            roteiro_maior_nota = max(roteiros, key=lambda x: x["dados_roteiro"]["nota"])
            return {"recomendacoes": [roteiro_maior_nota]}
        
class FlightManagement(BaseManagement):
    def __init__(self, flights_file="dados_voo.json"):
        super().__init__(flights_file)

    def carregar_data(self):
        try:
            return self.read_data()
        except FileNotFoundError:
            return {"dados_voo": []}

    def salvar_data(self, dados_voo):
        self.write_data(dados_voo)



flight_manager = FlightManagement()
itinerary_manager = ItineraryManagement()
user_manager = UserManagement()
city_manager = CityInformation()

# Definição dos endpoints FastAPI
app = FastAPI()

@app.post("/itineraries/add")
def adicionar_roteiro(dados_roteiro: dict):
    roteiros = itinerary_manager.carregar_roteiros()
    roteiros["roteiros"].append(dados_roteiro)
    itinerary_manager.salvar_roteiros(roteiros)
    return {"message": "Roteiro adicionado com sucesso!"}

@app.get("/itineraries/search-itineraries/{nome_da_cidade}")
def buscar_roteiro(nome_da_cidade: str):
    roteiros = itinerary_manager.carregar_roteiros()["roteiros"]
    roteiros_cidade = [r for r in roteiros if r["dados_roteiro"]["nome_da_cidade"] == nome_da_cidade]
    if not roteiros_cidade:
        raise HTTPException(status_code=404, detail="Roteiro não encontrado")
    roteiro_maior_nota = max(roteiros_cidade, key=lambda x: x["dados_roteiro"]["nota"])
    return roteiros_cidade

@app.get("/maps/coordinates/")
def get_coordenadas(cidade_origem: str, cidade_destino: str):
    # Obter coordenadas das cidades
    coordenadas_origem = city_manager.get_coordinates(cidade_origem)
    coordenadas_destino = city_manager.get_coordinates(cidade_destino)

    # Gere o link para o Google Maps com as coordenadas diretamente
    mapa_origem = f"https://www.google.com/maps/place/{coordenadas_origem[0]},{coordenadas_origem[1]}"
    mapa_destino = f"https://www.google.com/maps/place/{coordenadas_destino[0]},{coordenadas_destino[1]}"

    return {
        "cidades": [
            {"cidade_origem": cidade_origem, "coordenadas": {"latitude": coordenadas_origem[0], "longitude": coordenadas_origem[1], "mapa_link": mapa_origem}},
            {"cidade_destino": cidade_destino, "coordenadas": {"latitude": coordenadas_destino[0], "longitude": coordenadas_destino[1], "mapa_link": mapa_destino}}
        ]   
    }

@app.get("/cidade/{nome_cidade}")
def get_informacoes_cidade(nome_cidade: str):
    try:
        informacoes_cidade = city_manager.obter_informacoes_cidade(nome_cidade)
        return informacoes_cidade
    except HTTPException as e:
        return {"Informação não encontrada": str(e)}

@app.get("/user/get_users")
def get_users():
    users = user_manager.read_users()
    return {"users": users}

@app.get("/user/get_user/{user_id}")
async def get_user(user_id: str = Path(..., description="ID do usuário")):
    try:
        user_info = user_manager.get_user_by_id(user_id)
        if user_info is not None:
            return {"user_info": user_info}
        else:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
    except HTTPException as e:
        return {"error": str(e)}

@app.post("/user/add")
async def add_user(user_data: dict):
    user_id = user_manager.generate_user_id()

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

    # Lendo os usuários existentes
    users = user_manager.read_users()

    # Adicionando o novo usuário à lista de usuários
    users.append(user_data)

    # Escrevendo a lista atualizada de usuários de volta ao arquivo
    user_manager.write_users(users)

    return {"message": "Usuário adicionado com sucesso!", "id_usuario": user_id}

@app.post("/user/update/{user_id}")
async def update_user_endpoint(user_id: str, updated_data: dict):
    return user_manager.update_user(user_id, updated_data)

@app.get("/cidade/{nome_cidade}")
def get_informacoes_cidade(nome_cidade: str):
    try:
        informacoes_cidade = city_manager.obter_informacoes_cidade(nome_cidade)
        return informacoes_cidade
    except HTTPException as e:
        return {"Informação não encontrada": str(e)}
    
@app.post("/user/delete/{user_id}")
async def delete_user_endpoint(user_id: str):
    return user_manager.delete_user(user_id)

@app.get("/user/personalized-recommendations/{user_id}")
async def personalized_recommendations_endpoint(user_id: str):
    return itinerary_manager.personalized_recommendations(user_id)

@app.post("/user/copy-itinerary/{id_usuario_1}/{id_usuario_2}")
async def copy_itinerary_endpoint(id_usuario_1: str, id_usuario_2: str):
    return user_manager.copy_itinerary(id_usuario_1, id_usuario_2)

@app.post("/flights/add")
def adicionar_dados_voo(dados_voo: dict):
    voos_data = flight_manager.carregar_data()
    dados_voo_key = "dados_voo"
    if dados_voo_key not in voos_data:
        voos_data[dados_voo_key] = []

    voos_data[dados_voo_key].append(dados_voo)

    flight_manager.salvar_data(voos_data)
    
    return {"message": "Dados de voo adicionados com sucesso!"}


@app.get("/flights/search-flights/{nome_da_cidade}")
def buscar_roteiro(nome_da_cidade: str):
    voos_data = flight_manager.carregar_data()["dados_voo"]
    
    dados_voo_cidade = [r for r in voos_data if "origem" in r and r["origem"] == nome_da_cidade]
    
    if not dados_voo_cidade:
        raise HTTPException(status_code=404, detail="Dados voo não encontrado")
    
    return dados_voo_cidade


