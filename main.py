from flask import Flask, request, jsonify, send_file
import requests
import os
from dotenv import load_dotenv
from pytube import YouTube

# Charger les variables d'environnement
load_dotenv()

app = Flask(__name__)

# Récupérer la clé API depuis les variables d'environnement
API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'

# Liste temporaire pour stocker les résultats de recherche
search_results = []

@app.route('/recherche', methods=['GET'])
def youtube_search():
    global search_results

    # Récupérer la requête
    query = request.args.get('query')

    if not query:
        return jsonify({'error': 'Le paramètre "query" est requis.'}), 400

    # Paramètres de la requête YouTube
    params = {
        'part': 'snippet',
        'q': query,
        'key': API_KEY,
        'type': 'video',
        'maxResults': 5
    }

    # Requête API YouTube
    response = requests.get(YOUTUBE_SEARCH_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        search_results = []

        # Collecter les résultats
        for item in data.get('items', []):
            video_data = {
                'title': item['snippet']['title'],
                'videoId': item['id']['videoId']
            }
            search_results.append(video_data)

        # Construire le message de réponse formaté
        message = "Voici la liste disponible :\n"
        for i, result in enumerate(search_results, start=1):
            message += f"{i}- {result['title']}\n"  # Ajout d'une nouvelle ligne

        return jsonify({'message': message.strip()}), 200  # Utilisez .strip() pour enlever la dernière nouvelle ligne si nécessaire
    else:
        return jsonify({'error': 'Échec de la requête à l\'API YouTube.'}), response.status_code


@app.route('/regarde', methods=['POST'])
def regarde_video():
    """Télécharge et envoie la vidéo sélectionnée."""
    data = request.json
    choice = data.get('choice')
    
    if not search_results:
        return jsonify({'error': 'Aucune recherche préalable n\'a été effectuée.'}), 400
    
    if choice is None or choice < 1 or choice > len(search_results):
        return jsonify({"error": "Choix invalide"}), 400
    
    selected_video = search_results[choice - 1]
    video_url = f"https://www.youtube.com/watch?v={selected_video['videoId']}"

    try:
        # Télécharger la vidéo avec Pytube
        yt = YouTube(video_url)
        stream = yt.streams.get_highest_resolution()
        video_file = stream.download()

        # Envoyer la vidéo téléchargée
        return send_file(video_file, as_attachment=True, attachment_filename=f"{selected_video['title']}.mp4")

    except Exception as e:
        return jsonify({"error": f"Erreur lors du téléchargement de la vidéo: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
