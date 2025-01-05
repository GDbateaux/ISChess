import re

def analyze_depths(file_path):
    # Dictionnaire pour stocker les stats du bot
    stats = {
        'total_depth': 0,
        'move_count': 0,
        'max_depth': 0,
        'depths': []
    }
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                match = re.match(r"(w|b): Max depth reached: (\d+)", line.strip())
                if match:
                    depth = int(match.group(2))
                    
                    # Mise à jour des statistiques
                    stats['total_depth'] += depth
                    stats['move_count'] += 1
                    stats['max_depth'] = max(stats['max_depth'], depth)
                    stats['depths'].append(depth)
        
        # Calcul des moyennes
        stats['average_depth'] = stats['total_depth'] / stats['move_count'] if stats['move_count'] > 0 else 0
        
        # Calcul de l'écart type
        mean = stats['average_depth']

        # Suppression de la liste des profondeurs pour simplifier l'affichage
        del stats['depths']
    
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return
    
    # Affichage des résultats
    print("Statistiques des profondeurs du bot :")
    print("--------------------------------------")
    print(f"  - Nombre de coups analysés: {stats['move_count']}")
    print(f"  - Profondeur maximale atteinte: {stats['max_depth']}")
    print(f"  - Profondeur moyenne: {stats['average_depth']:.2f}")
    print()

# Exemple d'utilisation
file_path = "max_depths1.txt"
analyze_depths(file_path)
