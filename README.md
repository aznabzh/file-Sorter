# File Sorter

*Projet étudiant - BTS SIO SLAM*

File Sorter est une application Python qui range automatiquement les fichiers dans vos dossiers. Elle surveille un dossier (comme le dossier Téléchargements) et déplace les fichiers vers les bons endroits selon des règles que vous définissez.

## Principe de fonctionnement

L'application regarde les nouveaux fichiers qui arrivent dans un dossier et les classe automatiquement :
- Les vidéos (.mp4, .avi) vont dans un dossier "Videos"
- Les images (.jpg, .png) vont dans un dossier "Photos"  
- Les documents (.pdf, .docx) vont dans un dossier "Documents"
- Et ainsi de suite...

## Fonctionnalités

**Tri automatique**
- Range les fichiers par type (extension)
- Peut aussi ranger selon le nom du fichier
- Fonctionne en temps réel quand de nouveaux fichiers arrivent

**Configuration simple**
- Les règles de tri sont dans un fichier JSON
- On peut facilement ajouter de nouvelles règles
- Possibilité de tester sans vraiment déplacer les fichiers

**Interface en ligne de commande**
- Commandes simples pour lancer le tri
- Affichage de ce qui se passe (logs)
- Mode test pour vérifier avant de vraiment trier

## Technologies utilisées

- **Python** : Langage principal
- **JSON** : Pour la configuration
- **Threading** : Pour surveiller les dossiers en continu
- **Regex** : Pour analyser les noms de fichiers

## Structure du projet

```
File-Sorter/
├── file_sorter/
│   ├── cli.py              # Interface en ligne de commande
│   ├── sorter.py           # Moteur de tri des fichiers
│   ├── watcher.py          # Surveillance des dossiers
│   ├── config_handler.py   # Gestion de la configuration
│   └── file_utils.py       # Fonctions utilitaires
├── config/
│   └── config.json         # Règles de tri
└── docs/
    └── requirements.txt    # Dépendances Python
```

## Exemple d'utilisation

```bash
# Tester le tri sans rien déplacer
python -m file_sorter.cli --directory "C:/Users/nom/Downloads" --dry-run

# Faire le tri pour de vrai
python -m file_sorter.cli --directory "C:/Users/nom/Downloads"

# Surveiller le dossier en continu
python -m file_sorter.cli --watch --directory "C:/Users/nom/Downloads"
```

## Configuration

Les règles de tri sont dans le fichier `config/config.json`. Exemple :

```json
{
  "folders": [
    {
      "directory": "C:/Users/nom/Downloads",
      "rules": [
        {
          "extensions": [".mp4", ".avi"],
          "destination": "Videos"
        },
        {
          "extensions": [".jpg", ".png"],
          "destination": "Photos"
        },
        {
          "extensions": [".pdf"],
          "destination": "Documents"
        }
      ]
    }
  ]
}
```

## Objectifs pédagogiques

Ce projet m'a permis de travailler sur :
- La programmation orientée objet en Python
- La gestion des fichiers et des dossiers
- Les expressions régulières
- La programmation multithreadée
- La gestion d'erreurs
- La création d'interfaces en ligne de commande
- La lecture/écriture de fichiers JSON