import pandas as pd
import os

# === CONFIGURATION ===
key_file = os.path.join("sample_data", "answer_keys", "Key(Set A and B).xlsx")
responses_file = "student_responses.xlsx"
output_file = "scores.xlsx"

# === LOAD ANSWER KEYS ===
answer_key_A = pd.read_excel(key_file, sheet_name="Set - A").iloc[0].to_dict()
answer_key_B = pd.read_excel(key_file, sheet_name="Set - B").iloc[0].to_dict()

# Map set to answer key and relevant columns
# ...existing code...
set_to_key = {
    "A": (answer_key_A, ["Python", "EDA", "SQL", "POWER BI", "Statistics"]),
    "B": (answer_key_B, ["Python", "EDA", "SQL", "POWER BI", "Statistics"])
}
# ...existing code...

# === LOAD STUDENT RESPONSES ===
if os.path.exists(responses_file):
    student_responses = pd.read_excel(responses_file)
else:
    print(f"'{responses_file}' not found. Skipping scoring.")
    student_responses = None

if student_responses is not None:
    # === SCORING FUNCTION ===
    def score_student(row):
        student_set = str(row["Set"]).strip().upper()
        if student_set not in set_to_key:
            return 0  # or handle as needed
        key_dict, columns = set_to_key[student_set]
        score = 0
        for col in columns:
            student_ans = str(row.get(col, "")).strip().lower()
            correct_ans = str(key_dict.get(col, "")).strip().lower()
            if student_ans and student_ans == correct_ans:
                score += 1
        return score

    # === COMPUTE SCORES ===
    student_responses["Score"] = student_responses.apply(score_student, axis=1)

    # === SAVE RESULTS ===
    student_responses.to_excel(output_file, index=False)
    print(f"Scores saved to {output_file}")
