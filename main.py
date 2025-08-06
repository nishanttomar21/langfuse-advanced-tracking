import os
from dotenv import load_dotenv
from openai import OpenAI
from langfuse import get_client
from datetime import datetime
import importlib.metadata

# Load environment variables
load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
langfuse = get_client()


def make_metadata(user_id, model, temperature, max_tokens):
    return {
        "user_id": user_id,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "timestamp": datetime.now().isoformat(),
    }

def chat_with_tracking(prompt, user_id="nishant_tomar", model="gpt-3.5-turbo", temperature=0.7, max_tokens=150):
    metadata = make_metadata(user_id, model, temperature, max_tokens)

    # The context manager tracks everything with your metadata dynamically (@observe is for static information as it's assigned values at the tke of import)
    with langfuse.start_as_current_generation(name="metadata_tracking", model=model, input=prompt, metadata=metadata) as generation:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[  # type: ignore
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        response_text = response.choices[0].message.content

        if generation is not None:
            generation.update(output=response_text)

        return response_text

def main():
    print()
    print("-" * 40)
    print("Simple Chatbot with Langfuse Tracking (with custom metadata)")
    print("-" * 40)
    print()
    sample_prompts = [
        "Describe the concept of photosynthesis in simple terms.",
        "How does blockchain technology work?",
        "If you could travel to any city in the world, where would you go and why?",
        "What's an interesting historical event from the 20th century?"
    ]

    for i, prompt in enumerate(sample_prompts, 1):
        user_id = f"nishant_tomar_{i}"         # Unique user/session ID for each request
        model = "gpt-3.5-turbo"                # Or any other version you use
        temperature = 0.7 + i * 0.1            # Just to demonstrate parameter tracking
        max_tokens = 150
        print(f"\nQuery {i}: {prompt}")
        try:
            response = chat_with_tracking(
                prompt,
                user_id=user_id,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

    langfuse.flush()
    print("\nAll queries completed! Check your Langfuse dashboard.")

if __name__ == "__main__":
    main()
