


# Options avancées classées par difficulté croissante

| Option / Filtre                         | Difficulté (1 = très facile, 10 = très difficile) | Commentaire rapide                                                                                 |
|------------------------------------------|:-------------------------------------------------:|----------------------------------------------------------------------------------------------------|
| **exclude**                             | 2                                                 | Simple à ajouter dans la boucle de tri (filtrage par extension ou pattern).                        |
| **log_action**                          | 2                                                 | Il suffit d’ajouter un if pour logger ou non selon la règle.                                       |
| **recursive**                           | 3                                                 | Nécessite d’utiliser os.walk ou équivalent, mais reste basique.                                    |
| **destination** (relatif/absolu)        | 3                                                 | Il faut juste détecter si le chemin est absolu ou relatif et adapter le chemin cible.              |
| **action** (move, copy, delete, etc.)   | 4                                                 | Il faut gérer plusieurs actions, mais c’est surtout des appels à shutil/os.                        |
| **Filtres avancés** (taille, date, regex, etc.) | 5-7                                         | Taille et date : facile (os.stat). Regex : facile (re). Combiner plusieurs filtres : plus complexe.|
| **priority**                            | 5                                                 | Il faut trier les règles avant de les appliquer, mais c’est surtout de la logique de tri.          |
| **notify**                              | 5                                                 | Il faut utiliser une lib externe (ex: plyer, win10toast), mais c’est bien documenté.               |
| **created_between**                     | 5                                                 | Il faut parser les dates et comparer avec os.stat.                                                 |
| **older_than_days / younger_than_days** | 5                                                 | Calcul de la date courante - date du fichier, assez direct.                                        |
| **rename_pattern**                      | 6                                                 | Il faut parser le pattern, gérer les variables, et renommer proprement sans collision.              |
| **created_on_weekdays**                 | 6                                                 | Il faut convertir la date de création en jour de la semaine et filtrer.                            |
| **created_between_hours**               | 6                                                 | Il faut extraire l’heure de création et comparer.                                                  |
| **apply_once**                          | 7                                                 | Facile en mémoire, mais difficile si tu veux la persistance (cache sur disque, gestion des doublons).|
| **Filtrage dynamique (combinaison)**    | 7                                                 | Il faut combiner plusieurs filtres, gérer les priorités et les conflits.                           |
| **Filtrage par date relative**          | 7                                                 | Il faut parser des expressions comme `now-7d`, gérer les cas limites, etc.                         |

---

## Légende

- **1-3** : Très facile, quelques lignes à ajouter.
- **4-6** : Moyen, nécessite de modifier la logique ou d’ajouter des fonctions utilitaires.
- **7-8** : Difficile, gestion de cas complexes, persistance, ou combinaisons avancées.
- **9-10** : Très difficile, architecture à revoir ou dépendances lourdes (aucune ici n’atteint ce niveau).


# Liste complète des idées/options de configuration avancées

1. **exclude**
2. **recursive**
3. **action** (move, copy, delete, rename, link, compress, etc.)
4. **Filtres avancés**  
   - min_size_kb / max_size_kb  
   - created_before / created_after  
   - modified_before / modified_after  
   - accessed_before / accessed_after  
   - regex (filtrage par expression régulière sur le nom)
5. **destination** (relative ou absolue)
6. **rename_pattern**
7. **priority**
8. **log_action**
9. **notify**
10. **apply_once**
11. **created_between**
12. **older_than_days / younger_than_days**
13. **created_on_weekdays**
14. **created_between_hours**
15. **Filtrage dynamique** (combinaison de plusieurs filtres)
16. **Filtrage par date relative** (ex: now-7d)


## Détail et exemples pour chaque option

### 1. **exclude**
- **Résumé** : Ignore certains fichiers ou extensions (ex : fichiers temporaires, téléchargements incomplets).
- **Exemple** :
  ```json
  "exclude": [".tmp", ".crdownload", ".part"]
  ```
- **Utilité** : Évite de traiter des fichiers inutiles ou en cours de téléchargement.

---

### 2. **recursive**
- **Résumé** : Surveille aussi les sous-dossiers du dossier principal.
- **Exemple** :
  ```json
  "recursive": true
  ```
- **Utilité** : Trie tous les fichiers, même dans les sous-dossiers (ex : Photos/2024/06).

---

### 3. **action**
- **Résumé** : Définit ce que fait la règle : déplacer, copier, supprimer, renommer, lier, compresser, etc.
- **Exemple** :
  ```json
  "action": "copy"
  ```
- **Utilité** : Copier les images dans un dossier de sauvegarde, supprimer automatiquement les fichiers temporaires, créer des liens symboliques, compresser des fichiers, etc.

---

### 4. **Filtres avancés**
- **Résumé** : Permet de filtrer selon la taille, la date, le nom, etc.
- **Exemples** :
  ```json
  "min_size_kb": 100,
  "max_size_kb": 5000,
  "created_before": "2025-01-01",
  "created_after": "2024-01-01",
  "modified_before": "2024-06-01",
  "accessed_after": "2024-05-01",
  "regex": ".*facture.*"
  ```
- **Utilité** : Déplacer seulement les gros fichiers, archiver les fichiers anciens, trier les fichiers dont le nom contient un mot-clé, ne traiter que les fichiers modifiés récemment, etc.

---

### 5. **destination**
- **Résumé** : Chemin où envoyer les fichiers, relatif au dossier surveillé ou absolu.
- **Exemples** :
  ```json
  "destination": "Docs"
  "destination": "C:/Users/coren/Documents/Factures"
  ```
- **Utilité** : Organiser les fichiers dans des sous-dossiers, centraliser certains fichiers dans un dossier précis.

---

### 6. **rename_pattern**
- **Résumé** : Renomme automatiquement les fichiers selon un modèle.
- **Exemple** :
  ```json
  "rename_pattern": "facture_{date}_{original_name}"
  ```
- **Utilité** : Ajouter la date au nom du fichier, standardiser les noms pour éviter les doublons.

---

### 7. **priority**
- **Résumé** : Définit l’ordre d’application des règles si plusieurs matchent.
- **Exemple** :
  ```json
  "priority": 1
  ```
- **Utilité** : Appliquer d’abord la règle la plus importante (ex : factures avant PDF génériques).

---

### 8. **log_action**
- **Résumé** : Active ou désactive le log pour cette règle.
- **Exemple** :
  ```json
  "log_action": true
  ```
- **Utilité** : Garder une trace des fichiers supprimés ou déplacés, réduire la taille des logs pour les actions fréquentes.

---

### 9. **notify**
- **Résumé** : Envoie une notification système quand la règle s’applique.
- **Exemple** :
  ```json
  "notify": true
  ```
- **Utilité** : Être averti quand un fichier important est traité, recevoir une alerte en cas de suppression automatique.

---

### 10. **apply_once**
- **Résumé** : N’applique la règle qu’une seule fois par fichier, même après redémarrage (si cache persistant).
- **Exemple** :
  ```json
  "apply_once": true
  ```
- **Utilité** : Éviter de traiter en boucle un fichier qui revient dans le dossier, archiver un fichier une seule fois, même s’il est restauré.

---

### 11. **created_between**
- **Résumé** : Ne traite que les fichiers créés entre deux dates précises.
- **Exemple** :
  ```json
  "created_between": ["2024-01-01", "2024-12-31"]
  ```
- **Utilité** : Archiver ou déplacer uniquement les fichiers d’une certaine période.

---

### 12. **older_than_days / younger_than_days**
- **Résumé** : Filtrer selon l’âge du fichier (en jours).
- **Exemple** :
  ```json
  "older_than_days": 30,
  "younger_than_days": 7
  ```
- **Utilité** : Nettoyer les fichiers vieux de plus d’un mois, traiter seulement les fichiers récents.

---

### 13. **created_on_weekdays**
- **Résumé** : Ne traite que les fichiers créés certains jours de la semaine.
- **Exemple** :
  ```json
  "created_on_weekdays": [1, 2, 3, 4, 5]  // 1=lundi, 7=dimanche
  ```
- **Utilité** : Traiter différemment les fichiers créés en semaine ou le week-end.

---

### 14. **created_between_hours**
- **Résumé** : Ne traite que les fichiers créés entre certaines heures.
- **Exemple** :
  ```json
  "created_between_hours": [8, 18]
  ```
- **Utilité** : Appliquer une règle seulement aux fichiers créés pendant la journée de travail.

---

### 15. **Filtrage dynamique**
- **Résumé** : Combiner plusieurs filtres pour des règles très précises.
- **Exemple** :
  ```json
  "older_than_days": 90,
  "created_on_weekdays": [6, 7]
  ```
- **Utilité** : Traiter uniquement les fichiers vieux de 3 mois ET créés le week-end.

---

### 16. **Filtrage par date relative**
- **Résumé** : Utiliser des expressions dynamiques pour la date (ex : “il y a 7 jours”).
- **Exemple** :
  ```json
  "created_after": "now-7d"
  ```
- **Utilité** : Traiter les fichiers créés il y a moins d’une semaine, ou depuis le début du mois, etc.

---
```