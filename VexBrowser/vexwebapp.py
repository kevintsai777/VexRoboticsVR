from flask import Flask, render_template_string, jsonify
import math
import os

app = Flask(__name__)

INSTRUCTIONS_FILE = 'vex_instructions.txt'
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
    <h1>VEX Robot Movement Simulator</h1>
    <button onclick="executeInstructions()">Execute Instructions</button>
    <div id="instructionDisplay"></div>  <!-- Added for displaying current instruction -->
    <canvas id="canvas" width="800" height="600" style="border:1px solid black;"></canvas>
<script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');

    // Robot State
    let robotX = 400;
    let robotY = 300;
    let robotAngle = 0;

    function drawRobot() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(robotX, robotY);
        ctx.rotate(robotAngle * Math.PI / 180);

        // 1. Draw 4 Wheels (Black Rectangles)
        ctx.fillStyle = 'blue';
        const wheelW = 10; // wheel width
        const wheelH = 6;  // wheel height

        // Front Left, Front Right, Back Left, Back Right
        ctx.fillRect(10, -21, wheelW, wheelH);  // Front Left
        ctx.fillRect(10, 15, wheelW, wheelH);   // Front Right
        ctx.fillRect(-20, -21, wheelW, wheelH); // Back Left
        ctx.fillRect(-20, 15, wheelW, wheelH);  // Back Right

        // 2. Draw the Rectangle (Robot Body)
        ctx.fillStyle = 'gray';
        ctx.fillRect(-20, -15, 40, 30);

        // 3. Small Connector Rectangle (Attached to Triangle)
        ctx.fillStyle = 'yellow';
        // Positioned from x=5 to x=15 to meet the triangle base
        ctx.fillRect(-12, -8, 29, 16);

        // 3. Draw Isosceles Triangle (Direction Indicator)
        ctx.beginPath();
        ctx.fillStyle = 'pink';

        ctx.lineWidth = 2;         // Thickness of the outline

        // The triangle points forward (right) along the x-axis
        ctx.moveTo(35, 0);    // The forward tip (Apex)
        ctx.lineTo(15, -10);  // Back-left corner
        ctx.lineTo(15, 10);   // Back-right corner
        ctx.closePath();
        ctx.fill();

        ctx.restore();
    }

    async function executeInstructions() {
        const btn = document.querySelector('button');
        if(btn) btn.disabled = true;

        try {
            const response = await fetch('/get_movements');
            const data = await response.json();
            if (data.movements) await animateMovements(data.movements);
        } catch (err) {
            console.error("Fetch error:", err);
        } finally {
            if(btn) btn.disabled = false;
        }
    }

    async function animateMovements(movements) {
        const display = document.getElementById('instructionDisplay');

        for (let i = 0; i < movements.length; i++) {
            const target = movements[i];
            const startX = robotX;
            const startY = robotY;
            const startAngle = robotAngle;

            display.textContent = `Executing: ${target.instruction}`;

            const duration = (target.delay || 0) * 1000; // convert to ms

            if (duration > 0) {
                const startTime = performance.now();

                // Smooth Animation Loop for the duration of the 'delay'
                await new Promise(resolve => {
                    function step(now) {
                        const elapsed = now - startTime;
                        const progress = Math.min(elapsed / duration, 1);

                        // Linear Interpolation (Lerp)
                        robotX = startX + (target.x - startX) * progress;
                        robotY = startY + (target.y - startY) * progress;

                        // Angle handling (simple lerp)
                        robotAngle = startAngle + (target.angle - startAngle) * progress;

                        drawRobot();

                        if (progress < 1) {
                            requestAnimationFrame(step);
                        } else {
                            resolve();
                        }
                    }
                    requestAnimationFrame(step);
                });
            } else {
                // If no delay (state change only), jump immediately
                robotX = target.x;
                robotY = target.y;
                robotAngle = target.angle;
                drawRobot();
            }
        }
        display.textContent = 'Sequence Finished';
    }

    // Initial Render
    drawRobot();
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