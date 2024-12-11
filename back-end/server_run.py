from flask import Flask, request, jsonify
from tokenizer import tokenize
from parser import parse
from evaluator import evaluate


app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    try:
        code = request.json.get('code', '')
        environment = {}

        tokens = tokenize(code)
        ast = parse(tokens)
        result, _ = evaluate(ast,environment)

        return jsonify({"result":result})
    except Exception as e:
        return jsonify({"error":str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
