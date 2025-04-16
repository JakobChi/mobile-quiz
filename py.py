#!/usr/bin/env python3
import csv
import random
import tkinter as tk
from tkinter import messagebox
import tkinter.font as tkfont

ANSWER_MAX_WIDTH = 500  # maximal erlaubte Breite der Antwort-Buttons in Pixeln

def load_questions(filename):
    questions = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Erwartet: [Frage, Option A, Option B, Option C, Option D, korrekte Antwort]
                if len(row) == 6:
                    question = {
                        'frage': row[0],
                        'optionen': {
                            'A': row[1],
                            'B': row[2],
                            'C': row[3],
                            'D': row[4]
                        },
                        'korrekt': row[5].strip().upper()
                    }
                    questions.append(question)
    except Exception as e:
        print("Fehler beim Laden der Fragen:", e)
    return questions

def measure_wrapped_text(font, text, max_width):
    """
    Teilt den Text in Worte und simuliert ein Zeilenumbruch, 
    sodass die tatsächliche Breite der breitesten Zeile ermittelt wird.
    """
    words = text.split()
    if not words:
        return 0
    lines = []
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + " " + word
        if font.measure(test_line) <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return max(font.measure(line) for line in lines)

def adjust_button_font(btn, text, base_family="Arial", base_size=16, max_width=ANSWER_MAX_WIDTH, min_size=10):
    # Erstelle ein Font-Objekt mit der Ausgangsgröße
    font = tkfont.Font(family=base_family, size=base_size)
    current_size = base_size
    # Nutze measure_wrapped_text statt font.measure(text)
    while measure_wrapped_text(font, text, max_width) > max_width and current_size > min_size:
        current_size -= 1
        font.config(size=current_size)
    btn.config(font=font)

class QuizApp(tk.Tk):
    def __init__(self, questions):
        super().__init__()
        self.title("Quiz App")
        self.geometry("800x500")
        self.configure(bg="#f0f0f0")
        self.questions = questions
        random.shuffle(self.questions)
        self.current_index = 0
        self.score = 0

        self.create_widgets()
        self.display_question()

    def create_widgets(self):
        self.question_label = tk.Label(
            self, text="", wraplength=700, justify="center",
            font=("Arial", 20, "bold"), bg="#f0f0f0"
        )
        self.question_label.pack(pady=30)

        # Erstellen eines Frames für die Antwort-Buttons
        self.options_frame = tk.Frame(self, bg="#f0f0f0")
        self.options_frame.pack(pady=20)

        self.option_buttons = {}
        for option in ['A', 'B', 'C', 'D']:
            # Die feste width/height werden entfernt, damit die Größe nicht durch Zeichenanzahl erzwungen wird.
            btn = tk.Button(
                self.options_frame,
                text="",
                font=("Arial", 16),
                bg="#ffffff",
                fg="#333333",
                relief="raised",
                bd=2,
                wraplength=ANSWER_MAX_WIDTH,
                command=lambda opt=option: self.check_answer(opt)
            )
            btn.pack(pady=8, fill="x", padx=20)
            self.option_buttons[option] = btn

        self.feedback_label = tk.Label(
            self, text="", font=("Arial", 18), bg="#f0f0f0"
        )
        self.feedback_label.pack(pady=20)

    def display_question(self):
        if self.current_index < len(self.questions):
            q = self.questions[self.current_index]
            self.question_label.config(text=q['frage'])
            # Setze die Buttons zurück und passe den Text an
            for option in ['A', 'B', 'C', 'D']:
                btn_text = f"{option}: {q['optionen'][option]}"
                self.option_buttons[option].config(
                    text=btn_text,
                    state="normal",
                    bg="#ffffff"
                )
                # Passe die Schriftgröße an, damit der Text in den Button passt.
                adjust_button_font(self.option_buttons[option], btn_text)
            self.feedback_label.config(text="")
        else:
            self.finish_quiz()

    def check_answer(self, answer):
        q = self.questions[self.current_index]
        # Deaktivieren der Buttons, damit keine weiteren Eingaben möglich sind
        for btn in self.option_buttons.values():
            btn.config(state="disabled")
            
        if answer == q['korrekt']:
            self.feedback_label.config(text="Richtig!", fg="green")
            self.option_buttons[answer].config(bg="#90ee90")  # leicht grün
            self.score += 1
        else:
            self.feedback_label.config(text=f"Falsch! Korrekte Antwort: {q['korrekt']}", fg="red")
            self.option_buttons[answer].config(bg="#ffcccb")  # leicht rot
            self.option_buttons[q['korrekt']].config(bg="#90ee90")
        
        self.current_index += 1
        # Nach kurzer Verzögerung wird die nächste Frage angezeigt:
        self.after(1500, self.display_question)

    def finish_quiz(self):
        messagebox.showinfo(
            "Quiz beendet",
            f"Du hast {self.score} von {len(self.questions)} Fragen richtig beantwortet."
        )
        self.destroy()

def main():
    filename = "csv.csv"  # Passe hier ggf. den Dateinamen an
    questions = load_questions(filename)
    if not questions:
        print("Keine Fragen gefunden. Bitte überprüfe die CSV-Datei.")
        return
    app = QuizApp(questions)
    app.mainloop()

if __name__ == "__main__":
    main()
