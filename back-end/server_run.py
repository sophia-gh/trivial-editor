import io
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from tokenizer import tokenize
from parser import parse
from evaluator import evaluate


app = Flask(__name__)
CORS(app)

@app.route('/run', methods=['POST'])
def run_code():
    try:
        code = request.json.get('code', '')
        environment = {}
        tokens = tokenize(code)
        ast = parse(tokens)

        captured_output = io.StringIO()
        sys.stdout = captured_output
        evaluate(ast, environment)

        output = captured_output.getvalue()
        sys.stdout = sys.__stdout__

        return jsonify({"result":output})
    except Exception as e:
        return jsonify({"error":str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
