from flask import Flask, request, render_template
import math

app = Flask(__name__)

def bezier(t, p0, p1, p2):
    """Équation paramétrique de Bézier quadratique"""
    return tuple(
        (1 - t)**2 * p0[i] + 2 * (1 - t) * t * p1[i] + t**2 * p2[i]
        for i in range(3)
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            start = tuple(map(float, request.form['start'].split(',')))
            end = tuple(map(float, request.form['end'].split(',')))
            control = tuple(map(float, request.form['control'].split(',')))
            uuid = request.form['uuid']
            speed = float(request.form['speed'])
            tick_interval = int(request.form['tick_interval'])
            tick_duration = tick_interval * 0.05

            distance = math.sqrt(sum((end[i] - start[i])**2 for i in range(3)))
            duration = distance / speed
            steps = int(duration / tick_duration)

            commands = []
            for i in range(steps + 1):
                t = i / steps
                x, y, z = bezier(t, start, control, end)
                commands.append(f"minecraft:tp {uuid} {x:.2f} {y:.2f} {z:.2f}")
                commands.append("delay 2.8")

            return render_template("ast_to_npc_result.html", commands=commands)

        except Exception as e:
            return f"Erreur dans les données : {e}"

    return render_template("ast_to_npc.html")

