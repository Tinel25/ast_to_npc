from flask import Flask, request, render_template
import math
import os

app = Flask(__name__)

# Bézier quadratique
def bezier(t, p0, p1, p2):
    return tuple(
        (1 - t)**2 * p0[i] + 2 * (1 - t) * t * p1[i] + t**2 * p2[i]
        for i in range(3)
    )

# Calcul yaw/pitch pour tp avec orientation
def calculate_yaw_pitch(p1, p2):
    dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    yaw = math.degrees(math.atan2(-dx, dz))  # Z = nord
    dist_xz = math.sqrt(dx**2 + dz**2)
    pitch = math.degrees(math.atan2(-dy, dist_xz))
    return round(yaw, 2), round(pitch, 2)

def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Entrées utilisateur
            start = tuple(map(float, request.form['start'].split(',')))
            end = tuple(map(float, request.form['end'].split(',')))
            uuid = request.form['uuid']
            speed = safe_float(request.form['speed'], 1.0)
            tick_interval = int(request.form['tick_interval'])
            tick_duration = tick_interval * 0.05
            delay_ticks = safe_float(request.form.get('delay_ticks', 2.8))

            offset_x = safe_float(request.form.get('offset_x', 0))
            offset_y = safe_float(request.form.get('offset_y', 0))
            offset_z = safe_float(request.form.get('offset_z', 0))

            control_raw = request.form.get('control', '').strip()
            if control_raw:
                control = tuple(map(float, control_raw.split(',')))
            else:
                midpoint = tuple((start[i] + end[i]) / 2 for i in range(3))
                control = (
                    midpoint[0] + offset_x,
                    midpoint[1] + offset_y,
                    midpoint[2] + offset_z
                )
                if any(abs(control[i] - midpoint[i]) > 100 for i in range(3)):
                    raise ValueError("Décalage trop grand pour le point de contrôle.")

            # Calcul du nombre d'étapes
            distance = math.sqrt(sum((end[i] - start[i])**2 for i in range(3)))
            duration = distance / speed
            steps = max(1, int(duration / tick_duration))

            # Génération des commandes
            commands = []
            previous_point = start
            for i in range(steps + 1):
                t = i / steps
                x, y, z = bezier(t, start, control, end)
                current_point = (x, y, z)

                # Orientation
                yaw, pitch = calculate_yaw_pitch(previous_point, current_point)
                commands.append(f"tp {uuid} {x:.2f} {y:.2f} {z:.2f} {yaw:.2f} {pitch:.2f}")
                commands.append(f"delay {delay_ticks}")
                previous_point = current_point

            return render_template("ast_to_npc_result.html", commands=commands)

        except Exception as e:
            return f"Erreur : {e}"

    return render_template("ast_to_npc.html")

@app.route('/visualisation3D')
def visualisation3D():
    return render_template("visualisation3D.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
