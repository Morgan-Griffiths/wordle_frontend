import numpy as np
from flask import Flask, render_template, request, url_for, redirect
import requests
import json
import logging
import pathlib

logging.basicConfig(
    filename=pathlib.Path(__file__).resolve().parents[0] / "logs.txt",
    level=logging.INFO,
)
app = Flask(__name__)
APIServer = "http://localhost:4000/api"
EMPTY_WORD = " " * 5
LETTER_DIM = 0
RESULT_DIM = 1
alphabet = "".join([" "] + "abcdefghijklmnopqrstuvwxzy".lower().split())
alphabet_dict = {letter: i for i, letter in enumerate(alphabet)}
index_to_letter_dict = {i: letter for i, letter in enumerate(alphabet)}
color_dict = {0: None, 1: "#3a3a3c", 2: "#b59f3b", 3: "#538d4e"}


@app.route("/")
def index():
    res = requests.get(f"{APIServer}/target")
    secret = res.json()
    row1 = request.args.get("row1")
    row2 = request.args.get("row2")
    row3 = request.args.get("row3")
    row4 = request.args.get("row4")
    row5 = request.args.get("row5")
    row6 = request.args.get("row6")
    row1colors = request.args.get("row1colors")
    row2colors = request.args.get("row2colors")
    row3colors = request.args.get("row3colors")
    row4colors = request.args.get("row4colors")
    row5colors = request.args.get("row5colors")
    row6colors = request.args.get("row6colors")
    row1colors = json.loads(row1colors) if row1colors is not None else row1colors
    row2colors = json.loads(row2colors) if row2colors is not None else row2colors
    row3colors = json.loads(row3colors) if row3colors is not None else row3colors
    row4colors = json.loads(row4colors) if row4colors is not None else row4colors
    row5colors = json.loads(row5colors) if row5colors is not None else row5colors
    row6colors = json.loads(row6colors) if row6colors is not None else row6colors
    value = request.args.get("value")
    valueColor = (
        "rgba(255, 99, 132, 0.2)" if value and float(value) > 0 else "rgba(54, 162, 235, 0.2)"
    )
    valueBorder = (
        "rgba(255, 99, 132, 1)" if value and float(value) > 0 else "rgba(54, 162, 235, 1)"
    )
    policy = request.args.get("policy")
    temp = request.args.get("temp")
    temp = 1 if temp is None else temp
    if policy is None:
        freqs = [0] * 5
        words = [" " * 5] * 5
    else:
        policy = json.loads(policy)
        words = list(policy.keys())
        freqs = list(policy.values())
        res = sorted(zip(freqs, words), key=lambda x: x[0])
        freqs = [x[0] for x in res]
        words = [x[1] for x in res]
    return render_template(
        "wordle.html",
        row1=row1,
        row2=row2,
        row3=row3,
        row4=row4,
        row5=row5,
        row6=row6,
        secret=secret,
        value=value,
        policy=words,
        freqs=freqs,
        temp=temp,
        row1colors=row1colors,
        row2colors=row2colors,
        row3colors=row3colors,
        row4colors=row4colors,
        row5colors=row5colors,
        row6colors=row6colors,
        valueColor=valueColor,
        valueBorder=valueBorder,
    )


@app.route("/step", methods=["POST"])
def step():
    res = requests.get(f"{APIServer}/step")
    data = res.json()
    words, results = decode_state(data["state"])
    return redirect(
        url_for(
            "index",
            row1=words[0],
            row2=words[1],
            row3=words[2],
            row4=words[3],
            row5=words[4],
            row6=words[5],
            value=data["value"],
            policy=data["policy"],
            row1colors=json.dumps(results[0]),
            row2colors=json.dumps(results[1]),
            row3colors=json.dumps(results[2]),
            row4colors=json.dumps(results[3]),
            row5colors=json.dumps(results[4]),
            row6colors=json.dumps(results[5]),
        )
    )


@app.route("/reset", methods=["POST"])
def reset():
    data = requests.get(f"{APIServer}/reset").json()
    words, results = decode_state(data["state"])
    return redirect(
        url_for(
            "index",
            row1=words[0],
            row2=words[1],
            row3=words[2],
            row4=words[3],
            row5=words[4],
            row6=words[5],
            value=data["value"],
            policy=data["policy"],
            row1colors=json.dumps(results[0]),
            row2colors=json.dumps(results[1]),
            row3colors=json.dumps(results[2]),
            row4colors=json.dumps(results[3]),
            row5colors=json.dumps(results[4]),
            row6colors=json.dumps(results[5]),
        )
    )


def decode_state(state):
    state = np.array(state)
    row_words = []
    row_results = []
    for row in range(6):
        letter_nums = state[row, :, LETTER_DIM]
        result_nums = state[row, :, RESULT_DIM]
        letters = "".join([index_to_letter_dict[int(l)] for l in letter_nums])
        result_colors = [color_dict[num] for num in result_nums]
        row_words.append(letters)
        row_results.append(result_colors)
    return row_words, row_results


if __name__ == "__main__":
    app.run(debug=True)
