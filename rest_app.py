from flask import Flask, request, jsonify

app = Flask(__name__)

# Словарь для хранения данных телеметрии
data = {
}

# Маршрут для получения всех данных
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(data)

# Маршрут для получения данных по ключу
@app.route('/api/data/<string:key>', methods=['GET'])
def get_data_by_key(key):
    if key in data:
        return jsonify({key: data[key]})
    else:
        return jsonify({"message": "Key not found"}), 404

# Маршрут для добавления данных
@app.route('/api/data', methods=['POST'])
def add_data():
    new_data = request.get_json()
    print(new_data)
    key = str(len(data) + 1)
    data[key] = new_data
#    return jsonify({"message": "Data added", "key": key, "value": data[key]}), 201
    return jsonify({"message": "Data added", "key": key, "value": data[key]}), 200

if __name__ == '__main__':
    app.run(host='XXX.XXX.XXX.XXX', port=9000, debug=True)

