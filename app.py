from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# Secret key for Flask session management
app.secret_key = "my_quiz_secret_key"

# Static hardcoded question
QUESTION = {
    "id": 1,
    "question": "Which programming language is primarily used with Flask?",
    "options": {
        "A": "Java",
        "B": "Python",
        "C": "PHP",
        "D": "C++"
    },
    "correct_answer": "B"
}


# Route 1: Home page
@app.route("/")
def index():
    return render_template("index.html")


# Route 2: Quiz page
@app.route("/quiz")
def quiz():
    return render_template("quiz.html", question=QUESTION)


# Route 3: Submit answer and evaluate result
@app.route("/submit", methods=["POST"])
def submit():
    # Get the answer submitted by the user
    selected_answer = request.form.get("answer")

    # Check whether the user selected an answer
    if selected_answer not in QUESTION["options"]:
        return render_template(
            "quiz.html",
            question=QUESTION,
            error="Please select an answer before submitting."
        ), 400

    # Evaluate the submitted answer on the backend
    correct_answer = QUESTION["correct_answer"]

    if selected_answer == correct_answer:
        score = 1
        feedback = "Correct! Well done."
    else:
        score = 0
        feedback = "Incorrect. Better luck next time!"

    # Store the result in the session for the result page
    session["score"] = score
    session["total_questions"] = 1
    session["selected_answer"] = selected_answer
    session["feedback"] = feedback

    # Redirect the user to the result page
    return redirect(url_for("result"))


# Route 4: Result page
@app.route("/result")
def result():
    # Prevent users from accessing the result before taking the quiz
    if "score" not in session:
        return redirect(url_for("index"))

    score = session["score"]
    total_questions = session["total_questions"]
    selected_answer = session["selected_answer"]
    feedback = session["feedback"]

    return render_template(
        "result.html",
        score=score,
        total_questions=total_questions,
        selected_answer=selected_answer,
        correct_answer=QUESTION["correct_answer"],
        correct_option=QUESTION["options"][QUESTION["correct_answer"]],
        feedback=feedback,
        percentage=int((score / total_questions) * 100)
    )


# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)