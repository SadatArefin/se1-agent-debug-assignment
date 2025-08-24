"""
Example: Adding a new tool with the @tool decorator

This example shows how easy it is to add new tools to the system.
Simply create a function, add the @tool decorator, and it's automatically
registered and available for use.
"""

from src.agent.core.decorators import tool


@tool(name="joke_generator", description="Generate jokes on various topics")
def joke_generator(topic: str = "general") -> str:
    """
    Generate a joke on the specified topic.
    
    Args:
        topic: The topic for the joke (general, programming, science)
    
    Returns:
        str: A joke about the topic
    """
    jokes = {
        "programming": [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem.",
            "Why did the programmer quit his job? He didn't get arrays!",
        ],
        "science": [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call a fake noodle? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
        ],
        "general": [
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a sleeping bull? A bulldozer!",
            "Why don't scientists trust atoms? Because they make up everything!",
        ]
    }
    
    import random
    topic_jokes = jokes.get(topic.lower(), jokes["general"])
    return random.choice(topic_jokes)


@tool(name="password_generator", description="Generate secure passwords")
def password_generator(length: int = 12, include_symbols: bool = True) -> str:
    """
    Generate a secure password.
    
    Args:
        length: Length of the password (default: 12)
        include_symbols: Whether to include symbols (default: True)
    
    Returns:
        str: A randomly generated password
    """
    import random
    import string
    
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*"
    
    if length < 4:
        length = 4  # Minimum security
    
    return ''.join(random.choice(characters) for _ in range(length))


@tool(name="color_palette", description="Generate color palettes for design")
def color_palette(theme: str = "modern", count: int = 5) -> str:
    """
    Generate a color palette for design projects.
    
    Args:
        theme: Theme of the palette (modern, vintage, nature, ocean)
        count: Number of colors in the palette (default: 5)
    
    Returns:
        str: A formatted color palette
    """
    palettes = {
        "modern": ["#2C3E50", "#E74C3C", "#ECF0F1", "#3498DB", "#F39C12"],
        "vintage": ["#8B4513", "#CD853F", "#F5DEB3", "#A0522D", "#DEB887"],
        "nature": ["#228B22", "#8FBC8F", "#006400", "#9ACD32", "#32CD32"],
        "ocean": ["#008B8B", "#20B2AA", "#48D1CC", "#00CED1", "#40E0D0"],
    }
    
    theme_colors = palettes.get(theme.lower(), palettes["modern"])
    selected_colors = theme_colors[:min(count, len(theme_colors))]
    
    result = f"{theme.title()} Color Palette:\n"
    for i, color in enumerate(selected_colors, 1):
        result += f"{i}. {color}\n"
    
    return result.strip()


# Example of a tool that uses external data
@tool(name="text_stats", description="Analyze text and provide statistics")
def text_stats(text: str) -> str:
    """
    Analyze text and provide basic statistics.
    
    Args:
        text: The text to analyze
    
    Returns:
        str: Text statistics
    """
    import re
    
    # Basic stats
    char_count = len(text)
    word_count = len(text.split())
    sentence_count = len(re.split(r'[.!?]+', text.strip())) - 1
    paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
    
    # Character frequency (top 5)
    char_freq = {}
    for char in text.lower():
        if char.isalpha():
            char_freq[char] = char_freq.get(char, 0) + 1
    
    top_chars = sorted(char_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    
    stats = f"""Text Statistics:
    
Characters: {char_count}
Words: {word_count}
Sentences: {sentence_count}
Paragraphs: {paragraph_count}

Most frequent letters:"""
    
    for char, count in top_chars:
        stats += f"\n  {char}: {count}"
    
    return stats


if __name__ == "__main__":
    # These tools are now automatically registered and available!
    # Test the tools manually
    print("🎭 Joke:", joke_generator("programming"))
    print("🔐 Password:", password_generator(16))
    print("🎨 Palette:", color_palette("ocean", 3))
    print("📊 Stats:", text_stats("Hello world! This is a test."))
