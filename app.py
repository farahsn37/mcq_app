from flask import Flask, render_template, request, redirect, url_for
import requests
import html
import random
import json
from urllib.parse import unquote

app = Flask(__name__)

API_URL = "https://opentdb.com/api.php"

# Available quiz categories and their Open Trivia DB category IDs
QUIZ_CATEGORIES = {
    "": "All Categories",
    "9": "General Knowledge",
    "18": "Technology & Computers",
    "17": "Science & Nature",
    "19": "Mathematics",
    "23": "History",
    "22": "Geography",
    "21": "Sports",
    "15": "Video Games",
    "11": "Film",
    "12": "Music",
    "27": "Animals",
    "20": "Mythology"
}


# Route 1: Home page
@app.route("/")
def index():
    return render_template("index.html")

# Route 2: Fetch questions based on the selected category
@app.route("/quiz", methods=["GET"])
def quiz():
    try:
        # Retrieve the category ID submitted from index.html.
        # An empty value means the user selected All Categories.
        category_id = request.args.get("category", "").strip()

        # Validate the submitted category.
        if category_id not in QUIZ_CATEGORIES:
            return "Invalid quiz category.", 400

        category_name = QUIZ_CATEGORIES[category_id]

        # Set the default API parameters.
        params = {
            "amount": 5,
            "type": "multiple"
        }

        # Add the category parameter only if a specific category was selected.
        if category_id:
            params["category"] = category_id

        # Fetch questions from Open Trivia DB.
        response = requests.get(
            API_URL,
            params=params,
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        print("Selected category:", category_name)
        print("API response code:", data.get("response_code"))

        # Check whether the API successfully returned questions.
        if data.get("response_code") != 0:
            print("API error response:", data)

            raise ValueError(
                "The API could not return five questions for "
                f"the selected category: {category_name}."
            )

        api_questions = data.get("results", [])

        if len(api_questions) != 5:
            raise ValueError(
                f"Expected 5 questions, but received {len(api_questions)}."
            )

        question_mapping = {}
        checkbox_counter = 1

        # Process each question and its answer options.
        for question_number, api_question in enumerate(
            api_questions, start=1
        ):
            question_text = html.unescape(api_question["question"])
            correct_answer = html.unescape(
                api_question["correct_answer"]
            )

            incorrect_answers = [
                html.unescape(answer)
                for answer in api_question["incorrect_answers"]
            ]

            # Combine the correct and incorrect answers.
            all_options = incorrect_answers + [correct_answer]

            # Randomize the order of the options.
            random.shuffle(all_options)

            options_mapping = {}
            correct_checkbox_id = None

            # Assign a unique checkbox ID to each option.
            for option_text in all_options:
                current_checkbox_id = checkbox_counter

                options_mapping[str(current_checkbox_id)] = {
                    "text": option_text
                }

                if option_text == correct_answer:
                    correct_checkbox_id = current_checkbox_id

                checkbox_counter += 1

            # Store the question and its answer mapping.
            question_mapping[str(question_number)] = {
                "question": question_text,
                "options": options_mapping,
                "correct_checkbox_id": correct_checkbox_id
            }

        # Display the five questions using the existing quiz template.
        return render_template(
            "quiz.html",
            question_mapping=question_mapping,
            category_name=category_name
        )

    except Exception as error:
        app.logger.exception("Unable to load quiz questions")

        return render_template(
            "quiz.html",
            question_mapping={},
            error=(
                "Unable to load the quiz questions. "
                "Please return to the home page and try again later."
            )
        ), 503


# Route 3: Evaluate submitted answers
@app.route("/result", methods=["POST"])
def result():

    # Retrieve selected checkbox IDs.
    # getlist() handles multiple checkboxes with the same name.
    selected_ids = request.form.getlist("selected_ids")

    # Retrieve the original question mapping sent through form data.
    mapping_json = request.form.get("question_mapping", "")

    # Validate the submitted mapping
    try:
        question_mapping = json.loads(mapping_json)

        if not isinstance(question_mapping, dict):
            raise ValueError("Invalid question mapping.")

        if len(question_mapping) != 5:
            raise ValueError("The quiz must contain five questions.")

        # Validate the structure and answer IDs.
        for question_data in question_mapping.values():

            if not isinstance(question_data, dict):
                raise ValueError("Invalid question data.")

            options = question_data.get("options")

            if not isinstance(options, dict) or len(options) != 4:
                raise ValueError("Each question must contain four options.")

            correct_id = question_data.get("correct_checkbox_id")

            if str(correct_id) not in options:
                raise ValueError("Invalid correct answer mapping.")

    except (json.JSONDecodeError, ValueError, TypeError, AttributeError):
        return "Invalid quiz submission.", 400

    # Convert selected IDs to integers
    try:
        selected_ids = [int(value) for value in selected_ids]
    except (ValueError, TypeError):
        return "Invalid checkbox selection.", 400

    # Collect all valid checkbox IDs
    valid_ids = {
        int(option_id)
        for question_data in question_mapping.values()
        for option_id in question_data["options"]
    }

    # Reject checkbox IDs that do not belong to the quiz
    if any(option_id not in valid_ids for option_id in selected_ids):
        return "Invalid checkbox selection.", 400

    # Count selections for each question
    score = 0
    result_details = []

    for question_number, question_data in question_mapping.items():

        options = question_data["options"]

        correct_id = int(question_data["correct_checkbox_id"])

        # Find the four checkbox IDs belonging to this question
        question_option_ids = {
            int(option_id)
            for option_id in options
        }

        # Get the IDs selected for this question
        question_selections = [
            selected_id
            for selected_id in selected_ids
            if selected_id in question_option_ids
        ]

        # Determine whether the answer is correct
        if (
            len(question_selections) == 1
            and question_selections[0] == correct_id
        ):
            is_correct = True
            score += 1
        else:
            is_correct = False

        # Find the selected option text, if exactly one was selected
        if len(question_selections) == 1:
            selected_option_text = options[
                str(question_selections[0])
            ]["text"]
        elif len(question_selections) > 1:
            selected_option_text = "Multiple options selected"
        else:
            selected_option_text = "No answer selected"

        correct_option_text = options[str(correct_id)]["text"]

        result_details.append({
            "question_number": question_number,
            "question": question_data["question"],
            "selected_answer": selected_option_text,
            "correct_answer": correct_option_text,
            "is_correct": is_correct
        })

    total_questions = len(question_mapping)

    percentage = int((score / total_questions) * 100)

    if score == total_questions:
        feedback = "Excellent! All your answers are correct."
    elif score > 0:
        feedback = "Good effort! Keep practising."
    else:
        feedback = "Keep learning and try again!"

    # Render the result page directly.
    # No questions are fetched from the API on this route.
    return render_template(
        "result.html",
        score=score,
        total_questions=total_questions,
        percentage=percentage,
        feedback=feedback,
        result_details=result_details,

        # These variables preserve compatibility with the earlier
        # result.html template.
        selected_answer="See question details",
        correct_answer="",
        correct_option=""
    )


if __name__ == "__main__":
    app.run(debug=True)
