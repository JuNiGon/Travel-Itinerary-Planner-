##Travel Itinerary System
This travel itinerary system offers a variety of features to help users efficiently plan their trips. Below are the main functionalities of the system, along with the associated endpoints.

##installation
    1. postman
	2. vs code
	3. installation venv
	4. installation uvicorn (pip install uvicorn) (uvicorn app:app --reload)
	5. installation requesst (pip install requests)
	6. installation fastAPI (pip install fastapi uvicorn)


##Applied Requirements  

    1. Itinerary Creation and Customization
        Create User:  POST /user/add
            -Creates a new user with hotel, flight, and itinerary data.
        Update User: POST /user/update/{user_id}
            -Edits user, hotel, flight, and itinerary data based on the user ID.
        Delete User:  POST /user/delete/{user_id}
            -Deletes a user based on the ID.

    2. Destination Information and Recommendations
        Search Itineraries by City: GET /itineraries/search-itineraries/{city_name}
            -Searches itineraries by city name and returns the one with the highest rating.
            -If the city is not found, it returns the one with the highest rating among all.

    3. Booking Integration
        Add Itinerary:  POST /itineraries/add
            -Adds a new itinerary with hotel, flight, and activity data.

    4. Collaborative Planning Tools
        Copy Itinerary POST /user/copy-itinerary/{user_id_1}/{user_id_2}
            -Transfers the itinerary from one user to another.

    5. Travel Guides and Resources
        City Information: GET /cidade/{city_name}
            -Returns information about a specific city, including description, tips, tourist attractions, and country.

    6. Personalization Based on Preferences
        Personalized Recommendations: GET /user/personalized-recommendations/{user_id}
            -Obtains personalized recommendations based on user preferences.

    7. Map Integration and Route Planning
        Coordinates from a City: GET /maps/coordinates/{city}
            -Returns coordinates from an origin city to a destination city for route planning.

    8. Expense Tracking and Budget Management
        Add User and Calculate Expense:  POST /user/add
            -Adds travel information and calculates the sum of flight, hotel, and itinerary values.
            -Expenses are calculated and stored in the total_amount.

    9. Mobile Access and Offline Functionality
        Functionality not yet included.

    10. User Reviews and Community Input
        Add User Review: POST /user/add
        Update User:: POST /user/update/{user_id}
            -Allows users to leave reviews when creating or updating an itinerary.
        Add Itinerary Review:  POST /itineraries/add
            -Allows users to leave reviews when submitting a new itinerary.


##Execução Postman

    1. @app.get("/user/get_users")
        GET : http://127.0.0.1:8000/user/get_users

    2.@app.post("/user/add")
        POST : http://127.0.0.1:8000/user/add
        Body -> raw -> JSON
        Example Input:
            {
                "dados_do_usuario": {
                    "nome_completo": "Joazinho Costa",
                    "data_de_nascimento": "07/03/1945",
                    "email": "joao@gmail.com",
                    "valor_total": 0
                },
                "dados_voo": {
                    "valor_voo": 300,
                    "id_voo": "98756432",
                    "nome_do_voo": "TAM-456",
                    "assento": "C22",
                    "data_da_partida": "14/03/2024",
                    "origem": "Palmas",
                    "destino": "Salvador"
                },
                "dados_hotel": {
                    "valor_hotel": 200,
                    "id_hotel": "HOT-789",
                    "nome_da_cidade": "Salvador",
                    "hotel": "Ocean View",
                    "reviews": [
                        "Localizacao perfeita",
                        "Equipe atenciosa",
                        "otimo servico"
                    ],
                    "nota": 4
                },
                "dados_roteiro": {
                    "valor_roteiro": 600,
                    "id_roteiro": "XYZ-123",
                    "nome_da_cidade": "Salvador",
                    "nome_do_guia": "Jose Silva",
                    "lista_de_atividades": [
                        "Pelourinho historico",
                        "Praia do Farol",
                        "Mercado Modelo"
                    ],
                    "reviews": [
                        "Bonito",
                        "Muita comida",
                        "Legal"
                    ],
                    "nota": 3
                }
            }

    3.@app.post("/user/update/{user_id}")
        POST : http://127.0.0.1:8000/user/update/{user_id}
        Body -> raw -> JSON
        Example Input:
            POST : http://127.0.0.1:8000/user/update/e637e53c-d046-49be-9e25-c3125111cf82
            Body -> raw -> JSON
            {
                "dados_do_usuario": {
                    "nome_completo": "Maria FErnanda",
                    "data_de_nascimento": "07/03/1945",
                    "email": "maria@gmail.com",
                    "valor_total": 0
                },
                "dados_voo": {
                    "valor_voo": 100,
                    "id_voo": "98756432",
                    "nome_do_voo": "TAM-456",
                    "assento": "C12",
                    "data_da_partida": "14/03/2024",
                    "origem": "Palmas",
                    "destino": "Salvador"
                },
                "dados_hotel": {
                    "valor_hotel": 200,
                    "id_hotel": "HOT-789",
                    "nome_da_cidade": "Salvador",
                    "hotel": "Ocean View",
                    "reviews": [
                        "Localizacao perfeita",
                        "Equipe atenciosa",
                        "otimo servico"
                    ],
                    "nota": 4
                },
                "dados_roteiro": {
                    "valor_roteiro": 600,
                    "id_roteiro": "XYZ-123",
                    "nome_da_cidade": "Salvador",
                    "nome_do_guia": "Jose Silva",
                    "lista_de_atividades": [
                        "Pelourinho historico",
                        "Praia do Farol",
                        "Mercado Modelo"
                    ],
                    "reviews": [
                        "Bonito",
                        "Muita comida",
                        "Legal"
                    ],
                    "nota": 3
                }
            }

    4.@app.post("/user/delete/{user_id}")
        POST : http://127.0.0.1:8000/user/delete/{user_id}
        Example Input: 
                POST : http://127.0.0.1:8000/user/delete/e637e53c-d046-49be-9e25-c3125111cf82

    5.@app.get("/maps/coordinates/")
        GET : http://127.0.0.1:8000/maps/coordinates/?cidade_origem={nome_cidade}&cidade_destino={city_name}
        Example Input:
            GET : http://127.0.0.1:8000/maps/coordinates/?cidade_origem=Maceio&cidade_destino=Joao%20Pessoa

    6.@app.get("/itineraries/search-itineraries/{nome_da_cidade}")
        GET : http://127.0.0.1:8000/itineraries/search-itineraries/{city_name}
        Example Input:
            GET : http://127.0.0.1:8000/itineraries/search-itineraries/Palmas


    7.@app.post("/itineraries/add")
        POST : http://127.0.0.1:8000/itineraries/add
        Body -> raw -> JSON
        Example Input:
            Body -> raw -> JSON
            {
                "dados_roteiro": {
                    "id_roteiro": "BCD-1211",
                    "nome_da_cidade": "Rio Largo",
                    "nome_do_guia": "Andre Silva",
                    "lista_de_atividades": [
                    "Ir na feira",
                    "Ver o rio",
                    "subir ladeira"
                    ],
                    "reviews": [
                    "Cansativo",
                    "Bom",
                    "Muita ladeira"
                    ],
                    "nota": 2
                }
            }

    8.@app.get("/user/personalized-recommendations/{user_id}")
        GET : http://127.0.0.1:8000/user/personalized-recommendations/{id_usuario}
        Example Input:
            http://127.0.0.1:8000/user/personalized-recommendations/e637e53c-d046-49be-9e25-c3125111cf82

    9.@app.post("/user/copy-itinerary/{id_usuario_1}/{id_usuario_2}")
        POST : http://localhost:8000/user/copy-itinerary/{user_id_1}/{user_id_2}
        Example Input:
            http://localhost:8000/user/copy-itinerary/e0de0ea6-b75c-4ea2-b2f3-55e4c46d4978/9f3a3bc6-0833-4d5a-859b-d444187931a2

    10.@app.get("/cidade/{nome_cidade}")
        GET : http://127.0.0.1:8000/cidade/{city_name}
        Example Input:
            http://127.0.0.1:8000/cidade/Palmas