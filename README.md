
# WriteShelf

WriteShelf is a digital library and interactive platform designed for both readers and writers. It enables users to browse books, search by genre, theme, and author, and provides writers a space to publish, manage, and receive feedback on their written works. WriteShelf also includes social features like following authors, creating personalized feeds, and viewing activity history.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Project Overview
WriteShelf is a standalone system that combines a digital library with social and interactive features for writers and readers. The system is built using a client-server architecture with a Flask backend, MongoDB database, and HTML/CSS/JavaScript frontend.

## Features
- **Digital Library**: Browse and search books by genre, theme, or author, view detailed book information, and rate books.
- **Authoring Tools**: Writers can create, publish, and manage their stories and other written works.
- **Social Interaction**: Follow authors, view personalized feeds, comment on books, and receive notifications.
- **Activity Tracking**: History of user interactions, including ratings, comments, and follower activity.

## Technology Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Hosting**: Local computer (or VPS if affordable)

---

## Installation
### Prerequisites
- **Python** (version 3.7 or higher)
- **MongoDB** (version 4.0 or higher)

### Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/WriteShelf.git
   cd WriteShelf
   ```

2. **Set Up a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up MongoDB**
   - Ensure MongoDB is installed and running on your local machine or on a server.
   - Configure the MongoDB connection URI in `config.py`.

5. **Run the Application**
   ```bash
   flask run
   ```
   Access the app at `http://localhost:5000`.

---

## Usage
Once the application is running:
1. **Create an Account**: Sign up as a new user.
2. **Browse Books**: Search, filter by genre, and view book details.
3. **Authoring**: If you’re a writer, create new stories, publish, and manage them.
4. **Social Features**: Follow authors, leave comments, and interact with the community.

---

## Testing
WriteShelf includes a series of tests to ensure system stability:
- **Unit Testing**: Tests individual modules and components.
- **Integration Testing**: Verifies interactions between components like frontend-backend and backend-database.
- **User Acceptance Testing (UAT)**: Ensures that end-user requirements are met.
- **Performance Testing**: Evaluates system responsiveness under load.

To run the tests:
```bash
pytest
```

---

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add feature"`).
4. Push to your branch (`git push origin feature-branch`).
5. Open a pull request.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

---

## Contact
Created by:
- **Seif Eldin** - seifeldin@example.com
- **Ahmed Mostafa** - ahmedmostafa@example.com

For any questions, feel free to contact us.
