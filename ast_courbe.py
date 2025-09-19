from flask import Flask, request, render_template
import math
import os

# Initialisation de l'application Flask
app = Flask(__name__)

# Fonction de courbe de Bézier quadratique
def bezier(t, p0, p1, p2):
    """Équation paramétrique de Bézier quadratique"""
    return tuple(
        (1 - t)**2 * p0[i] + 2 * (1 - t) * t * p1[i] + t**2 * p2[i]
        for i in range(3)
    )

# Route principale
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Récupération et conversion des données du formulaire
            start = tuple(map(float, request.form['start'].split(',')))
            end = tuple(map(float, request.form['end'].split(',')))
            uuid = request.form['uuid']
            speed = float(request.form['speed'])
            tick_interval = int(request.form['tick_interval'])
            tick_duration = tick_interval * 0.05

            # Récupération des offsets
            offset_x = float(request.form.get('offset_x', 0))
            offset_y = float(request.form.get('offset_y', 0))
            offset_z = float(request.form.get('offset_z', 0))

            # Récupération du delay personnalisé en ticks
            delay_ticks = float(request.form.get('delay_ticks', 2.8))

            # Vérification du champ 'control'
            control_raw = request.form.get('control', '').strip()
            if control_raw:
                # Si l'utilisateur a fourni un point de contrôle
                control = tuple(map(float, control_raw.split(',')))
            else:
                # Calcul automatique du point de contrôle avec décalage
                control = (
                    (start[0] + end[0]) / 2 + offset_x,
                    (start[1] + end[1]) / 2 + offset_y,
                    (start[2] + end[2]) / 2 + offset_z
                )

            # Calcul de la distance et du nombre d'étapes
            distance = math.sqrt(sum((end[i] - start[i])**2 for i in range(3)))
            duration = distance / speed
            steps = int(duration / tick_duration)

            # Génération des commandes Minecraft
            commands = []
            for i in range(steps + 1):
                t = i / steps
                x, y, z = bezier(t, start, control, end)
                commands.append(f"minecraft:tp {uuid} {x:.2f} {y:.2f} {z:.2f}")
                commands.append(f"delay {delay_ticks}")

            # Affichage du résultat
            return render_template("ast_to_npc_result.html", commands=commands)

        except Exception as e:
            return f"Erreur dans les données : {e}"

    # Affichage du formulaire
    return render_template("ast_to_npc.html")

# Nouvelle route pour la visualisation 3D
@app.route('/visualisation3D')
def visualisation3D():
    return render_template("visualisation3D.html")

# Lancement de l'application (important pour Render)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
