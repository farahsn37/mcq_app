# Quiz Application

A Python Flask-based multiple-choice quiz application integrated with the [Open Trivia Database API](https://opentdb.com/). Users can select quiz categories, answer questions, and view their results instantly.

## Features

- **Quiz Categories** – Choose from various categories, including General Knowledge, Technology, Science, History, Sports, and more.
- **Multiple-Choice Questions** – Each quiz consists of five questions with four answer options.
- **Randomized Answers** – Answer options are shuffled for each question.
- **Automated Scoring** – Automatically calculates scores based on selected answers.
- **Result Summary** – Displays the final score, percentage, and answer review.
- **API Integration** – Retrieves quiz questions dynamically from the Open Trivia Database API.

## Technologies Used

- Python
- Flask
- HTML5
- CSS3
- Bootstrap 4.5
- Requests Library
- Open Trivia Database API

## Project Structure

```text
quiz-application/
│
├── app.py
├── templates/
│   ├── index.html
│   ├── quiz.html
│   └── result.html
│
└── README.md
```

## Installation & Setup

**1. Clone the repository**

```bash
git clone <your-repository-url>
```

**2. Navigate to the project directory**

```bash
cd quiz-application
```

**3. Create a virtual environment (recommended)**

```bash
python -m venv venv
```

**4. Activate the virtual environment**

Windows:

```bash
venv\Scripts\activate
```

**5. Install dependencies**

```bash
pip install flask requests
```

**6. Run the Flask application**

```bash
python app.py
```

**7. Open the application**

Visit the following URL in your browser:

```text
http://127.0.0.1:5000
```

## API Reference

This project uses the [Open Trivia Database API](https://opentdb.com/api_config.php) to retrieve multiple-choice quiz questions.

## Future Improvements

- Add more quiz categories and difficulty levels.
- Allow users to select the number of questions.
- Store quiz history and scores.
- Implement a user login and registration system.
- Improve the user interface and responsiveness.

## Author

Developed as a personal Python Flask project to practise web application development, API integration, and backend programming.
