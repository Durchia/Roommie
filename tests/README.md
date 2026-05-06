# Roomie - Roommate Matching Application

## Author
**Duru** *Vilnius Gediminas Technical University (Vilnius Tech)* *Artificial Intelligence Systems*

## Project Overview
Roomie is a Python-based application designed to match individuals with compatible roommates based on lifestyle habits and personal preferences. Unlike property listing apps, Roomie focuses strictly on the social and behavioral compatibility between potential roommates.

## Technical Architecture
The project follows a modular structure to ensure scalability and clean code:
- **models/**: Contains the core logic and data structures for `BaseUser`, `HouseOwner`, and `HouseSeeker`.
- **data/**: Manages data persistence using JSON files (`users.json`) and mock data for testing.
- **tests/**: Contains unit tests (`test_engine.py`) to ensure the matching engine functions correctly.
- **engine.py**: The core matching logic.
- **main.py**: The entry point for the console-based application.
- **user_factory.py**: Implements the Factory pattern for dynamic user creation.
- **scoring_strategy.py**: A customized algorithm to calculate compatibility scores.

## How to Run the Project
1. Ensure you have Python 3.x installed on your system.
2. Open your terminal or command prompt.
3. Navigate to the project root directory (`ROOMIE`).
4. Run the application using the following command:
   ```bash
   python main.py