import pandas as pd

try:
    df = pd.read_csv('keep_notes.csv')
    # Filter for expense notes
    expense_notes = df[df['labels'].str.contains('expense', case=False, na=False)]
    
    if not expense_notes.empty:
        print(f"Found {len(expense_notes)} expense notes.")
        print("\n--- Sample Note 1 ---")
        row = expense_notes.iloc[0]
        print(f"Title: {row['title']}")
        print(f"Text:\n{row['text']}")
        print("-" * 20)
        
        if len(expense_notes) > 1:
            print("\n--- Sample Note 2 ---")
            row = expense_notes.iloc[1]
            print(f"Title: {row['title']}")
            print(f"Text:\n{row['text']}")
            print("-" * 20)
    else:
        print("No expense notes found.")

except Exception as e:
    print(f"Error: {e}")
