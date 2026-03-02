from transformers import pipeline

print("Loading summarization model...")
summarizer_model = pipeline("summarization", model="t5-small")
print("Summarization model loaded ✅")


def summarize_text(text):
    try:
        if len(text.strip()) == 0:
            return "No content to summarize."

        summary = summarizer_model(
            text,
            max_length=120,
            min_length=30,
            do_sample=False
        )

        return summary[0]["summary_text"]

    except Exception as e:
        return f"Summarization failed: {str(e)}"