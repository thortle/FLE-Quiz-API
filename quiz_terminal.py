#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Terminal Quiz for French Grammar
Connects to the API to fetch questions and verify answers
"""

import requests
import sys

API_URL = "http://127.0.0.1:8000"


def clear_screen():
    print("\n" * 2)


def check_api():
    """Check if API is running"""
    try:
        resp = requests.get(f"{API_URL}/verify", timeout=2)
        return resp.status_code == 200
    except:
        return False


def get_quiz(niveau):
    """Fetch quiz from API"""
    try:
        resp = requests.post(
            f"{API_URL}/generate_quiz",
            json={"niveau": niveau},
            timeout=5
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except:
        return None


def display_question(num, total, question_data):
    """Display a single question with options"""
    print("\n" + "=" * 60)
    print(f"Question {num}/{total} | Niveau: {question_data['niveau']} | {question_data['categorie']}")
    print("=" * 60)
    print(f"\n{question_data['question']}\n")
    
    options = [
        ("A", question_data['reponseA']),
        ("B", question_data['reponseB']),
        ("C", question_data.get('reponseC', '')),
        ("D", question_data.get('reponseD', ''))
    ]
    
    valid_options = []
    for letter, text in options:
        if text and str(text).strip():
            print(f"  {letter}) {text}")
            valid_options.append(letter)
    
    return valid_options, question_data['reponse']


def verify_answer(user_choice, valid_options, correct_answer, question_data):
    """Verify user's answer and display result"""
    # Map letter to actual answer text
    option_map = {
        'A': question_data['reponseA'],
        'B': question_data['reponseB'],
        'C': question_data.get('reponseC', ''),
        'D': question_data.get('reponseD', '')
    }
    
    user_answer = option_map.get(user_choice.upper(), '')
    
    # Compare with correct answer (strip whitespace for comparison)
    is_correct = user_answer.strip() == correct_answer.strip()
    
    print()
    if is_correct:
        print(">>> CORRECT! <<<")
        return True
    else:
        print(">>> WRONG <<<")
        # Find which letter has the correct answer
        correct_letter = None
        for letter, text in option_map.items():
            if text and text.strip() == correct_answer.strip():
                correct_letter = letter
                break
        if correct_letter:
            print(f"    Correct answer: {correct_letter}) {correct_answer}")
        else:
            print(f"    Correct answer: {correct_answer}")
        return False


def run_quiz(niveau):
    """Run a complete quiz session"""
    print(f"\nFetching {niveau}-level questions...")
    
    quiz_data = get_quiz(niveau)
    if not quiz_data or not quiz_data.get('quiz'):
        print("Error: Could not fetch questions from API")
        return
    
    questions = quiz_data['quiz']
    total = len(questions)
    score = 0
    
    print(f"Loaded {total} questions. Let's begin!\n")
    input("Press Enter to start...")
    
    for i, question in enumerate(questions, 1):
        valid_options, correct_answer = display_question(i, total, question)
        
        # Get user input
        while True:
            user_input = input(f"\nYour answer ({'/'.join(valid_options)}): ").strip().upper()
            if user_input in valid_options:
                break
            elif user_input == 'Q':
                print("\nQuiz aborted.")
                return
            else:
                print(f"Invalid choice. Please enter {', '.join(valid_options)} (or Q to quit)")
        
        # Verify answer
        if verify_answer(user_input, valid_options, correct_answer, question):
            score += 1
        
        # Pause before next question (except for last one)
        if i < total:
            input("\nPress Enter for next question...")
    
    # Final score
    print("\n" + "=" * 60)
    print("QUIZ COMPLETE!")
    print("=" * 60)
    percentage = (score / total) * 100
    print(f"\nYour score: {score}/{total} ({percentage:.0f}%)")
    
    if percentage >= 80:
        print("Excellent!")
    elif percentage >= 60:
        print("Good job!")
    elif percentage >= 40:
        print("Keep practicing!")
    else:
        print("You need more practice.")
    print()


def main_menu():
    """Display main menu and handle user choice"""
    while True:
        print("\n" + "=" * 60)
        print("      QUIZ FLE - GRAMMAIRE FRANCAISE")
        print("=" * 60)
        print("\nChoose an option:\n")
        print("  1) Generate Quiz - Level A (A1, A2)")
        print("  2) Generate Quiz - Level B (B1, B2)")
        print("  3) Generate Quiz - Level C (C1, C2)")
        print("  4) View Statistics")
        print("  5) Quit")
        print()
        
        choice = input("Your choice (1-5): ").strip()
        
        if choice == '1':
            run_quiz('A')
        elif choice == '2':
            run_quiz('B')
        elif choice == '3':
            run_quiz('C')
        elif choice == '4':
            show_stats()
        elif choice == '5':
            print("\nAu revoir!\n")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter 1-5.")


def show_stats():
    """Display database statistics"""
    try:
        resp = requests.get(f"{API_URL}/stats", timeout=5)
        if resp.status_code == 200:
            stats = resp.json()
            print("\n" + "-" * 40)
            print("DATABASE STATISTICS")
            print("-" * 40)
            print(f"Total questions: {stats['total_questions']}")
            print("\nBy level:")
            for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
                count = stats['par_niveau'].get(level, 0)
                print(f"  {level}: {count}")
            print("\nBy category:")
            for cat, count in stats['par_categorie'].items():
                print(f"  {cat}: {count}")
            print("-" * 40)
            input("\nPress Enter to continue...")
        else:
            print("Error fetching statistics")
    except:
        print("Error: Could not connect to API")


if __name__ == "__main__":
    print("\nChecking API connection...")
    
    if not check_api():
        print("\nERROR: API is not running!")
        print("Please start the server first:")
        print("  python3 -m uvicorn main:api --host 127.0.0.1 --port 8000")
        print()
        sys.exit(1)
    
    print("API connected!\n")
    main_menu()
