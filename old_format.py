import re
import pandas as pd
import emoji
from collections import Counter
import matplotlib.pyplot as plt

# Function to clean and extract messages from the chat
def extract_messages(chat):
    # Updated regex for format with parentheses and special characters
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[APap][Mm]) - (.*?): (.*)"
    messages = re.findall(pattern, chat)
    data = []
    
    for msg in messages:
        date, time, sender, message = msg
        data.append([date, time, sender.strip(), message.strip()])
    
    if not data:
        raise ValueError("No messages extracted. Check the file format or regex pattern.")
    
    return pd.DataFrame(data, columns=["Date", "Time", "Sender", "Message"])

# Process WhatsApp chat and analyze data
def process_whatsapp_chat(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            chat = file.read()
    except FileNotFoundError:
        raise FileNotFoundError("Chat file not found. Make sure the file path is correct.")
    
    # Extract messages into a DataFrame
    df = extract_messages(chat)
    
    # Basic statistics
    total_messages = len(df)
    message_counts = df['Sender'].value_counts()
    
    # Top emojis used
    all_emojis = [c for msg in df['Message'] for c in msg if c in emoji.EMOJI_DATA]
    top_emojis = Counter(all_emojis).most_common(10)
    
    # Top words used
    words = re.findall(r'\b\w+\b', ' '.join(df['Message']).lower())
    top_words = Counter(words).most_common(10)
    
    # Messages by sender
    messages_by_sender = df['Sender'].value_counts()
    
    # Messages by time of day
    df['Hour'] = pd.to_datetime(df['Time'], format='%I:%M %p').dt.hour
    messages_by_hour = df.groupby('Hour').size()
    
    # Plot messages by time of day
    plt.figure(figsize=(10, 6))
    messages_by_hour.plot(kind='bar', color='skyblue')
    plt.title('Messages by Time of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Messages')
    plt.show()

    return {
        "total_messages": total_messages,
        "message_counts": message_counts,
        "top_emojis": top_emojis,
        "top_words": top_words,
    }

# File path for the exported WhatsApp chat
file_path = '_chat.txt'

# Process the chat
details = process_whatsapp_chat(file_path)

# Display results
print("Total Messages:", details["total_messages"])
print("\nMessage Counts by Sender:\n", details["message_counts"])
print("\nTop Emojis:\n", details["top_emojis"])
print("\nTop Words:\n", details["top_words"])
