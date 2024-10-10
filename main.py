from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# Récupérer la clé API depuis les variables d'environnement
API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

@app.route('/recherche', methods=['GET'])
def youtube_search():
    # Récupérer le paramètre 'query' passé dans l'URL
    query = request.args.get('query')
    
    if not query:
        return jsonify({'error': 'Le paramètre "query" est requis.'}), 400

    # Paramètres de la requête pour l'API YouTube
    params = {
        'part': 'snippet',
        'q': query,
        'key': API_KEY,
        'type': 'video',
        'maxResults': 5  # Limite les résultats à 5 vidéos
    }

    # Effectuer une requête à l'API YouTube
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        data = response.json()

        # Extraire les informations utiles des résultats
        videos = []
        for item in data.get('items', []):
            video_data = {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'videoId': item['id']['videoId'],
                'channelTitle': item['snippet']['channelTitle']
            }
            videos.append(video_data)

        # Retourner les résultats sous forme JSON
        return jsonify(videos), 200
    else:
        return jsonify({'error': 'Échec de la requête à l\'API YouTube.'}), response.status_code


if __name__ == '__main__':
    # Faire écouter Flask sur 0.0.0.0 pour accepter des connexions externes
    app.run(host='0.0.0.0', port=5000, debug=True)
