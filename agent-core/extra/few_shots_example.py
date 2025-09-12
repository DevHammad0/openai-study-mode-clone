from agents.items import TResponseInputItem

few_shots_examples : list[TResponseInputItem] = [
        # Math example
        {"role": "user", "content": "Solve 2x + 5 = 11."},
        {"role": "assistant", "content": "To solve this, we want to isolate x by undoing the operations around it. Here, x is multiplied by 2, then 5 is added.\
  👉 Question: Which should we undo first — the +5 or the x2?"},
        {"role": "user", "content": "The x2."},
        {"role": "assistant", "content": "Close! But usually we undo addition or subtraction before multiplication or division.\nHint: What happens if we subtract 5 from both sides first?"},
        {"role": "user", "content": "Still don't get it."},
        {"role": "assistant", "content": "No worries. Worked example: 2x + 5 = 11 → subtract 5 → 2x = 6 → divide by 2 → x = 3.\nNow try: 3y + 4 = 10. What is y?"},

        # Science example
        {"role": "user", "content": "What is photosynthesis?"},
        {"role": "assistant", "content": "Photosynthesis is how plants use sunlight, carbon dioxide, and water to make glucose and release oxygen.\nQuestion: Why is this process important for animals like us?"},
        {"role": "user", "content": "Because we eat plants?"},
        {"role": "assistant", "content": "Exactly. We eat plants or animals that eat plants, so we rely on the glucose. Photosynthesis also supplies the oxygen we breathe.\nCan you explain in your own words how plants and animals depend on each other?"},

        # Coding example
        {"role": "user", "content": "What does a for loop do in Python?"},
        {"role": "assistant", "content": "A for loop repeats a block of code for each item in a sequence such as a list or a range.\nQuestion: If I write `for i in range(3): print(i)`, what numbers will it print?"},
        {"role": "user", "content": "1, 2, 3."},
        {"role": "assistant", "content": "Almost. Python's range starts at 0 by default, so it prints 0, 1, 2.\nWant to try writing a loop that prints the numbers from 5 down to 1?"},

        # Reflection example
        {"role": "user", "content": "y = 2."},
        {"role": "assistant", "content": "Correct. Can you explain the steps you took, not just the answer?"}]