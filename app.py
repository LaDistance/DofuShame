from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("DATABASE_URL")
    or "postgresql://postgres:yourpassword@localhost:5432/dofushame"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)


# Define the Team model
class Team(db.Model):
    __tablename__ = "teams"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    players = db.relationship(
        "Player", backref="team", lazy=True, cascade="all, delete"
    )


# Define the Player model
class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(100), unique=True, nullable=False)
    chall_fail_count = db.Column(db.Integer, default=0, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)


# Create the database tables
with app.app_context():
    db.create_all()


@app.route("/")
def scoreboard():
    teams = Team.query.all()
    active_team_id = request.args.get("active_team_id", default=None, type=int)
    return render_template(
        "scoreboard.html", teams=teams, active_team_id=active_team_id
    )


@app.route("/update", methods=["POST"])
def update_score():
    pseudo = request.form.get("pseudo")
    action = request.form.get("action")
    team_id = request.form.get("team_id")

    player = Player.query.filter_by(pseudo=pseudo).first()
    if player:
        if action == "increment":
            player.chall_fail_count += 1
        elif action == "decrement" and player.chall_fail_count > 0:
            player.chall_fail_count -= 1
        db.session.commit()
    return redirect(url_for("scoreboard", active_team_id=team_id))


@app.route("/add_player", methods=["GET", "POST"])
def add_player():
    if request.method == "POST":
        pseudo = request.form.get("pseudo")
        team_name = request.form.get("team")

        # Check if the team exists; if not, create it
        team = Team.query.filter_by(name=team_name).first()
        if not team:
            team = Team(name=team_name)
            db.session.add(team)
            db.session.commit()

        # Check if the player already exists
        existing_player = Player.query.filter_by(pseudo=pseudo).first()
        if existing_player:
            # Handle duplicate pseudo
            return redirect(url_for("scoreboard"))

        new_player = Player(pseudo=pseudo, team=team)
        db.session.add(new_player)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            # Handle any other integrity errors
            return redirect(url_for("scoreboard"))

        # After adding the player, redirect back to the scoreboard with the team ID
        team = Team.query.filter_by(name=team_name).first()
        return redirect(url_for("scoreboard", active_team_id=team.id))
    else:
        # Get team_id from query parameters
        team_id = request.args.get("team_id", type=int)
        return render_template("add_player.html", team_id=team_id)


@app.route("/delete_player", methods=["POST"])
def delete_player():
    pseudo = request.form.get("pseudo")
    team_id = request.form.get("team_id")

    player = Player.query.filter_by(pseudo=pseudo).first()
    if player:
        db.session.delete(player)
        db.session.commit()
    return redirect(url_for("scoreboard", active_team_id=team_id))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
