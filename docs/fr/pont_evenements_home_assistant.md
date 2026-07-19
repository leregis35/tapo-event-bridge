# Pont d’événements Home Assistant

La version 0.8.0 écoute uniquement les entités Home Assistant déjà existantes et rattachées aux caméras Tapo découvertes. Les changements d’état significatifs sont normalisés par Tapo Event Bridge.

L’écoute est limitée aux identifiants connus, sans polling, sans écriture directe en base et sans contact ni réveil direct des caméras. Le capteur Activité des événements expose des compteurs en mémoire, les détections actives et les 20 derniers événements.
