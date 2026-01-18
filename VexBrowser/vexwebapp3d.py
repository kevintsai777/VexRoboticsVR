from flask import Flask, render_template_string, jsonify
import math
import os

app = Flask(__name__)

INSTRUCTIONS_FILE = r"vex_instructions.txt"
PIXELS_PER_INCH = 100  # Scale for canvas (1 inch = 10 pixels)
SPEED_INCH_PER_SEC = 0.1  # Default moving speed
TURNING_SPEED_DEG_PER_SEC = 10  # Turning speed in degrees per second

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>VEX Robot Simulator</title>
    <style>
        #instructionDisplay {
            font-size: 18px;  /* Fixed to 18px */
            margin: 10px 0;
            color: blue;
        }
    </style>
</head>
<body>
    <h1>VEX Robot 3D Simulator</h1>
    <button onclick="window.executeInstructions()">Execute Instructions</button>
    <div id="instructionDisplay" style="font-family: monospace; padding: 10px;">Ready</div>

<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@v0.149.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@v0.149.0/examples/jsm/"
  }
}
</script>

<script type="module">
    import * as THREE from 'three';

    // --- 1. Scene Setup ---
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xeeeeee);
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight * 0.8);
    document.body.appendChild(renderer.domElement);

    // --- 2. Lighting ---
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5, 10, 7.5);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040));

    // --- 3. Create Robot Group ---
    const robot = new THREE.Group();

    const body = new THREE.Mesh(
        new THREE.BoxGeometry(4, 1.2, 2.8),
        new THREE.MeshLambertMaterial({ color: 0x001596 })
    );
    robot.add(body);

    const wheelGeom = new THREE.CylinderGeometry(0.7, 0.7, 0.4, 38);
    const wheelMat = new THREE.MeshLambertMaterial({ color: 0x5E5E5E });
    [[1.5, -0.3, 1.6], [1.5, -0.3, -1.6], [-1.5, -0.3, 1.6], [-1.5, -0.3, -1.6]].forEach(pos => {
        const wheel = new THREE.Mesh(wheelGeom, wheelMat);
        wheel.position.set(...pos);
        wheel.rotation.x = Math.PI / 2;
        robot.add(wheel);
    });

    // --- Create Two Beige Driver Seats ---
    const createSeat = () => {
        const seatGroup = new THREE.Group();
        const seatMaterial = new THREE.MeshStandardMaterial({ color: 0xF5F5DC }); // Beige

        // 1. Seat Base
        const baseGeom = new THREE.BoxGeometry(1.2, 0.2, 1.2);
        const seatBase = new THREE.Mesh(baseGeom, seatMaterial);
        seatBase.position.y = 0.6; // Sit on top of body (body height is 1, so top is 0.5)
        seatGroup.add(seatBase);

        // 2. Seat Back
        const backGeom = new THREE.BoxGeometry(0.2, 1.4, 1.2);
        const seatBack = new THREE.Mesh(backGeom, seatMaterial);
        seatBack.position.set(-0.5, 1.3, 0); // Positioned at the rear of the base
        seatGroup.add(seatBack);

        return seatGroup;
    };

    // Left Seat
    const leftSeat = createSeat();
    leftSeat.position.set(-0.5, 0, 0.7); // Shifted to the left side
    robot.add(leftSeat);

    // Right Seat
    const rightSeat = createSeat();
    rightSeat.position.set(-0.5, 0, -0.7); // Shifted to the right side
    robot.add(rightSeat);

    const headlightGeometry = new THREE.CylinderGeometry(0.2, 0.2, 0.5, 16);
    const headlightMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFF200,
        emissive: 0xFFF200,
        emissiveIntensity: 0.8
    });
    const headlight1 = new THREE.Mesh(headlightGeometry, headlightMaterial);
    headlight1.position.set(2.2, 0.3, 0.8); // Position: Forward, Up slightly, Right
    headlight1.rotation.x = Math.PI / 2; // Point forward

    const headlight2 = new THREE.Mesh(headlightGeometry, headlightMaterial);
    headlight2.position.set(2.2, 0.3, -0.8); // Position: Forward, Up slightly, Left
    headlight2.rotation.x = Math.PI / 2; // Point forward

    robot.add(headlight1);
    robot.add(headlight2);

    scene.add(robot);
    camera.position.set(0, 30, 16);
    camera.lookAt(0, 0, 0);

    // --- 4. Movement Logic ---
    window.executeInstructions = async function() {
        try {
            const response = await fetch('/get_movements');
            const data = await response.json();
            if (data.movements) await animateMovements(data.movements);
        } catch (err) {
            console.error("Fetch error:", err);
        }
    };

    async function animateMovements(movements) {
        const display = document.getElementById('instructionDisplay');
        const scale = 0.05; // Scale pixels/inches to 3D units

        for (const move of movements) {
            display.textContent = `Executing: ${move.instruction}`;

            const startPos = { x: robot.position.x, z: robot.position.z };
            const startRot = robot.rotation.y;

            // Map 2D (x, y) to 3D (x, z)
            const targetX = (move.x - 400) * scale;
            const targetZ = (move.y - 300) * scale;
            const targetRot = -move.angle * (Math.PI / 180);

            const duration = (move.delay || 0.1) * 1000;
            const startTime = performance.now();

            await new Promise(resolve => {
                function frame(now) {
                    const progress = Math.min((now - startTime) / duration, 1);

                    robot.position.x = startPos.x + (targetX - startPos.x) * progress;
                    robot.position.z = startPos.z + (targetZ - startPos.z) * progress;
                    robot.rotation.y = startRot + (targetRot - startRot) * progress;

                    if (progress < 1) requestAnimationFrame(frame);
                    else resolve();
                }
                requestAnimationFrame(frame);
            });
        }
        display.textContent = "Finished.";
    }

    // Standard 2026 Render Loop
    renderer.setAnimationLoop(() => {
        renderer.render(scene, camera);
    });
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_movements')
def get_movements():
    movements = []
    # Starting State
    x, y, angle = 400.0, 300.0, 0.0
    velocity = 0.0
    direction_multiplier = 1  # 1 for forward (0), -1 for backward (1)

    # Constants
    PIXELS_PER_INCH = 10
    TURNING_SPEED = 90 # degrees per second

    try:
        with open(INSTRUCTIONS_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2: continue

                command = parts[0].lower()
                value = float(parts[1])
                delay = 0.0

                if command == 'stop':
                    if value == 1: velocity = 0

                elif command == 'velocity':
                    velocity = value/10  # Convert to inches/sec

                elif command == 'direction':
                    # 0 = Forward, 1 = Backward
                    direction_multiplier = 1 if value == 1 else -1

                elif command == 'degree':
                    target_angle = value % 360
                    # Calculate shortest turn
                    diff = (target_angle - angle + 180) % 360 - 180
                    delay = abs(diff) / TURNING_SPEED
                    angle = target_angle

                elif command == 'wait':
                    # 'wait' triggers the actual movement calculation
                    duration = value
                    distance = velocity * duration * PIXELS_PER_INCH

                    rad = math.radians(angle)
                    x += direction_multiplier * distance * math.cos(rad)
                    y -= direction_multiplier * distance * math.sin(rad) # Inverted Y
                    delay = duration/10

                # Append state after every instruction to track progress
                movements.append({
                    'x': round(x, 2),
                    'y': round(y, 2),
                    'angle': round(angle, 2),
                    'velocity': velocity,
                    'delay': round(delay, 2),
                    'instruction': f"{command} {value}"
                })

    except FileNotFoundError:
        pass

    return jsonify({'movements': movements})

if __name__ == '__main__':
    app.run(debug=True)