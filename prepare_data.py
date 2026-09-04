import pandas as pd
import json
import os
import numpy as np

def process_csv_to_jsonl(input_csv: str, output_jsonl: str):
    if not os.path.exists(input_csv):
        print(f"⚠️ Warning: Could not find {input_csv}. Skipping.")
        return

    print(f"📥 Processing {input_csv}...")
    df = pd.read_csv(input_csv)
    
    formatted_records = []
    dropped_count = 0

    for index, row in df.iterrows():
        # 1. Map fields for the new dataset format
        topic = str(row.get('topic', 'General Knowledge'))
        difficulty = str(row.get('difficulty', 'beginner')).lower()
        
        question = str(row.get('question', '')).strip()
        answer_key = str(row.get('answerKey', '')).strip()
        explanation = str(row.get('explanation', '')).strip()
        
        choices_str = str(row.get('choices', ''))
        
        try:
            # Parse the stringified dict containing numpy arrays
            choices = eval(choices_str, {"array": np.array, "object": object, "nan": np.nan})
            labels = list(choices.get('label', []))
            texts = list(choices.get('text', []))
            
            valid_options = [str(t).strip() for t in texts if str(t).strip() and str(t).strip().lower() != "nan"]
            
            if answer_key in labels:
                correct_idx = labels.index(answer_key)
                correct_answer = str(texts[correct_idx]).strip()
            else:
                correct_answer = ""
        except Exception:
            dropped_count += 1
            continue

        # 2. STRICT QUALITY CONTROL
        if not question or question.lower() == "nan":
            dropped_count += 1
            continue
            
        # For test datasets, answerKey might be missing. We allow missing correct_answer here.
        # But if it is provided, we validate it.
        if correct_answer and correct_answer.lower() != "nan":
            if correct_answer not in valid_options:
                dropped_count += 1
                continue
                
        if len(set(valid_options)) < 2:
            dropped_count += 1
            continue 
        # 3. Build the Target JSON Structure
        assistant_json = {
            "topic": topic,
            "difficulty": difficulty,
            "questions": [{
                "question": question,
                "options": valid_options,
                "correct_answer": correct_answer,
                "explanation": explanation
            }]
        }

        # 4. Wrap into the conversational format for the model to reference
        user_prompt = f"Generate a {difficulty} multiple-choice question on '{topic}'."
        record = {
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert cybersecurity examiner. Generate structured multiple-choice quizzes strictly adhering to the JSON schema."
                },
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": json.dumps(assistant_json, ensure_ascii=False)}
            ]
        }
        formatted_records.append(record)

    # 5. Export to JSONL
    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    with open(output_jsonl, "w", encoding="utf-8") as f:
        for item in formatted_records:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"✅ Converted {os.path.basename(input_csv)}: Kept {len(formatted_records)} | Dropped {dropped_count} broken rows.\n")

def convert_all_kaggle_csvs(input_dir: str, output_dir: str):
    """Maps your existing CSV splits to the target JSONL files."""
    file_mappings = {
        "train.csv": "train_topics.jsonl",
        "validation.csv": "val_dataset.jsonl",
        "test.csv": "test_dataset.jsonl"
    }
    
    for input_filename, output_filename in file_mappings.items():
        in_path = os.path.join(input_dir, input_filename)
        out_path = os.path.join(output_dir, output_filename)
        process_csv_to_jsonl(in_path, out_path)

if __name__ == "__main__":
    # Point this to wherever your raw Kaggle CSVs live
    convert_all_kaggle_csvs(input_dir="data/", output_dir="training/datasets/")