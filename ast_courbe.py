from flask import Flask, request, render_template
import math
import os

app = Flask(__name__)

def bezier(t, p0, p1, p2):
    return tuple(
        (1 - t)**2 * p0[i] + 2 * (1 - t) * t * p1[i] + t**2 * p2[i]
        for i in range(3)
    )

def calculate_yaw_pitch(p1, p2):
    dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    yaw = math.degrees(math.atan2(-dx, dz))
    dist_xz = math.sqrt(dx**2 + dz**2)
    pitch = math.degrees(math.atan2(-dy, dist_xz))
    return round(yaw, 2), round(pitch, 2)

def safe_float(value, default=0.0):
    try:
        return float(value)
    except:
        return default

def parse_points(raw):
    lines = raw.strip().split('\n')
    return [tuple(map(float, line.strip().split(','))) for line in lines if line.strip()]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            points_raw = request.form['points']
            offsets_raw = request.form.get('offsets', '')
            points = parse_points(points_raw)
            offsets = parse_points(offsets_raw)

            if len(points) < 2:
                raise ValueError("Il faut au moins deux points.")
            if len(offsets) != len(points) - 1:
                raise ValueError("Le nombre de décalages doit être égal au nombre de segments (points - 1).")

            tag = request.form['tag'].strip()
            speed = safe_float(request.form['speed'], 1.0)
            tick_interval = int(request.form['tick_interval'])
            tick_duration = tick_interval * 0.05
            delay_ticks = safe_float(request.form.get('delay_ticks', 2.8))

            commands = []

            for idx in range(len(points) - 1):
                start = points[idx]
                end = points[idx + 1]
                offset = offsets[idx]

                midpoint = tuple((start[i] + end[i]) / 2 for i in range(3))
                control = tuple(midpoint[i] + offset[i] for i in range(3))

                distance = math.sqrt(sum((end[i] - start[i])**2 for i in range(3)))
                duration = distance / speed
                steps = max(1, int(duration / tick_duration))

                previous_point = start
                for i in range(steps + 1):
                    t = i / steps
                    x, y, z = bezier(t, start, control, end)
                    current_point = (x, y, z)

                    yaw, pitch = calculate_yaw_pitch(previous_point, current_point)
                    selector = f"@e[type=armor_stand,tag={tag}]"
                    commands.append(f"minecraft:tp {selector} {x:.2f} {y:.2f} {z:.2f} {yaw:.2f} {pitch:.2f}")
                    commands.append(f"delay {delay_ticks}")
                    previous_point = current_point

            return render_template("ast_to_npc_result.html", commands=commands)

        except Exception as e:
            return f"Erreur : {e}"

    return render_template("ast_to_npc.html")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
