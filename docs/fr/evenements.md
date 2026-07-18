# Moteur d’événements

Tapo Event Bridge utilise un modèle `CameraEvent` indépendant du transport.
Les futures sources publieront dans un moteur léger unique au lieu d’exposer
les charges utiles propres à chaque protocole aux plateformes Home Assistant.

L’enregistreur est borné et uniquement en mémoire. Le rejeu crée des copies
anonymisées et ne republie jamais les données brutes de la caméra. Aucun
polling ni tâche d’arrière-plan n’est démarré.
