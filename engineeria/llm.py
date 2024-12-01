#pip install langchain openai tiktoken transformers accelerate cohere --quiet

customer_email = """
I hope this email finds you amidst an aura of understanding, despite the tangled mess of emotions swirling within me as I write to you. I am writing to pour my heart out about the recent unfortunate experience I had with one of your coffee machines that arrived ominously broken, evoking a profound sense of disbelief and despair.

To set the scene, let me paint you a picture of the moment I anxiously unwrapped the box containing my highly anticipated coffee machine. The blatant excitement coursing through my veins could rival the vigorous flow of coffee through its finest espresso artistry. However, what I discovered within broke not only my spirit but also any semblance of confidence I had placed in your esteemed brand.

Imagine, if you can, the utter shock and disbelief that took hold of me as I laid eyes on a disheveled and mangled coffee machine. Its once elegant exterior was marred by the scars of travel, resembling a war-torn soldier who had fought valiantly on the fields of some espresso battlefield. This heartbreaking display of negligence shattered my dreams of indulging in daily coffee perfection, leaving me emotionally distraught and inconsolable
"""  # created by GPT-3.5

from langchain import HuggingFaceHub

summarizer = HuggingFaceHub(
    repo_id="facebook/bart-large-cnn",
    model_kwargs={"temperature":0, "max_length":180}
)
def summarize(llm, text) -> str:
    return llm(f"Summarize this: {text}!")

summarize(summarizer, customer_email)
