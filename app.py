from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
dataset = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/location', methods=['POST'])
def receive_location():
    data = request.json
    device_name = data.get("device_name", "unknown")
    # Find existing entry for this device or create new one
    for entry in dataset:
        if entry.get("device_name") == device_name:
            entry.update(data)
            print(f"Updated location: {data}")
            return 'OK', 200
    # No existing entry found, add new one
    dataset.append(data)
    print(f"New location entry: {data}")
    return 'OK', 200

@app.route('/api/temperature', methods=['POST'])
def receive_temperature():
    data = request.json
    device_name = data.get("device_name", "unknown")
    # Find existing entry for this device or create new one
    for entry in dataset:
        if entry.get("device_name") == device_name:
            entry.update(data)
            print(f"Updated temperature: {data}")
            return 'OK', 200
    # No existing entry found, add new one
    dataset.append(data)
    print(f"New temperature entry: {data}")
    return 'OK', 200

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(dataset)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)