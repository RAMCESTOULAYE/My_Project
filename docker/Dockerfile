# Image Python légère
FROM python:3.11-slim

# Répertoire de travail
WORKDIR /app

# Copier uniquement le fichier requirements.txt d'abord pour utiliser le cache Docker
COPY requirements.txt .

# Installation des dépendances
RUN pip3 install --no-cache-dir -r requirements.txt

# Copier le reste du projet dans le conteneur
COPY . .


# Copier le script d'entrée depuis le dossier `docker` vers le répertoire racine du conteneur
COPY docker/entrypoint.sh /entrypoint.sh

# Donner les droits d'exécution à l'entrée du conteneur
RUN chmod +x /entrypoint.sh

# Exposer les ports utilisés par Gunicorn et Daphne
EXPOSE 8000 

# Lancer le script d’entrée
ENTRYPOINT ["/entrypoint.sh"]
