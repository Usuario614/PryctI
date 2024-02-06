
from fastapi import FastAPI
from typing import List
import pandas as pd
import os



# Obtener la ruta al directorio del script principal
directorio_actual = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta al archivo CSV utilizando una ruta relativa
ruta_csv_rel = os.path.join(directorio_actual, 'df_para_consultas.csv')

# Leer el archivo CSV utilizando pandas
try:
    df_para_consultas = pd.read_csv(ruta_csv_rel)
    print(df_para_consultas.head())
except FileNotFoundError:
    print(f"Error: No se encontró el archivo en la ruta relativa: {ruta_csv_rel}")





app = FastAPI()

# Función para obtener la cantidad de items y porcentaje de contenido Free por año según la empresa desarrolladora
@app.get('/developer')
def developer(desarrollador: str):
    # Filtrar el DataFrame por desarrollador
    df_filtered = df_para_consultas[df_para_consultas['developer'] == desarrollador]
    
    # Agrupar por año y calcular la cantidad de items y el porcentaje de contenido Free
    result = df_filtered.groupby('year').agg({'id': 'count', 'price': lambda x: (x == 0).mean() * 100}).reset_index()
    result.columns = ['Año', 'Cantidad de Items', 'Contenido Free']
    
    return result.to_dict(orient='records')

# Función para obtener información del usuario, incluyendo dinero gastado, porcentaje de recomendación y cantidad de items
@app.get('/userdata')
def userdata(user_id: str):
    # Filtrar el DataFrame por user_id
    df_user = df_para_consultas[df_para_consultas['user_id'] == user_id]
    
    # Calcular el dinero gastado, el porcentaje de recomendación y la cantidad de items
    dinero_gastado = df_user['price'].sum()
    porcentaje_recomendacion = df_user['recommend'].mean() * 100
    cantidad_items = len(df_user)
    
    # Crear el diccionario de retorno
    result = {
        "Usuario": user_id,
        "Dinero gastado": f"{dinero_gastado} USD",
        "% de recomendación": f"{porcentaje_recomendacion:.2f}%",
        "Cantidad de items": cantidad_items
    }
    
    return result

# Función para obtener el usuario con más horas jugadas para un género dado y la acumulación de horas jugadas por año
@app.get('/UserForGenre')
def UserForGenre(genero: str):
    # Filtrar el DataFrame por género
    df_genre = df_para_consultas[df_para_consultas['genres'].str.contains(genero, case=False)]
    
    # Encontrar el usuario con más horas jugadas
    max_user = df_genre.loc[df_genre['playtime_forever'].idxmax(), 'user_id']
    
    # Calcular la acumulación de horas jugadas por año
    hours_by_year = df_genre.groupby('year')['playtime_forever'].sum().reset_index()
    hours_by_year.columns = ['Año', 'Horas']
    
    # Crear el diccionario de retorno
    result = {
        "Usuario con más horas jugadas para Género": max_user,
        "Horas jugadas": hours_by_year.to_dict(orient='records')
    }
    
    return result

# Función para obtener el top 3 de desarrolladores con juegos MÁS recomendados por usuarios para el año dado
@app.get('/best_developer_year')
def best_developer_year(year: int):
    # Filtrar el DataFrame por año y reviews positivos
    df_year_positive_reviews = df_para_consultas[(df_para_consultas['year'] == year) & (df_para_consultas['recommend'] == 1.0)]
    
    # Obtener el top 3 de desarrolladores
    top_developers = df_year_positive_reviews.groupby('developer').size().nlargest(3).reset_index()
    top_developers.columns = ['Desarrollador', 'Cantidad de juegos recomendados']
    
    # Crear el diccionario de retorno
    result = top_developers.to_dict(orient='records')
    
    return result

# Función para obtener el análisis de reseñas de usuarios por desarrollador
@app.get('/developer_reviews_analysis')
def developer_reviews_analysis(desarrolladora: str):
    # Filtrar el DataFrame por desarrollador y reseñas con análisis de sentimiento positivo o negativo
    df_reviews_analysis = df_para_consultas[df_para_consultas['developer'] == desarrolladora]
    
    # Contar la cantidad de registros con análisis de sentimiento positivo o negativo
    reviews_count = df_reviews_analysis['sentiment_analysis'].value_counts().to_dict()
    
    # Crear el diccionario de retorno
    result = {desarrolladora: reviews_count}
    
    return result