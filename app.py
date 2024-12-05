from flask import Flask, render_template, request, redirect, url_for, jsonify
import json

app = Flask(__name__)


# Load data from JSON file
def load_data():
    with open("data.json", "r") as file:
        return json.load(file)


# Save data back to JSON file
def save_data(data):
    with open("data.json", "w") as file:
        json.dump(data, file, indent=4)


@app.route("/")
def scoreboard():
    data = load_data()
    # Sort players by "Nombre de chall raté" in descending order
    sorted_data = sorted(data, key=lambda x: x["Nombre de chall raté"], reverse=True)
    return render_template("scoreboard.html", data=sorted_data)


@app.route("/update", methods=["POST"])
def update_score():
    pseudo = request.form.get("pseudo")
    action = request.form.get("action")

    data = load_data()
    for player in data:
        if player["Pseudo"] == pseudo:
            if action == "increment":
                player["Nombre de chall raté"] += 1
            elif action == "decrement" and player["Nombre de chall raté"] > 0:
                player["Nombre de chall raté"] -= 1
            break

    save_data(data)
    return redirect(url_for("scoreboard"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
