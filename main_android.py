import re
import pandas as pd
from collections import Counter
import emoji
import matplotlib.pyplot as plt

# Function to clean and extract messages from the chat
def extract_messages(chat):
    # Updated regex for format with parentheses and special characters
    pattern = r"(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}\s?[APap][Mm]) - (.*?): (.*)"
    messages = re.findall(pattern, chat)
    data = []
    
    for msg in messages:
        date, time, sender, message = msg
        data.append([date.strip(), time.strip(), sender.strip(), message.strip()])
    
    if not data:
        raise ValueError("No messages extracted. Check the file format or regex pattern.")
    
    return pd.DataFrame(data, columns=["Date", "Time", "Sender", "Message"])

# Load and process the WhatsApp chat
def process_whatsapp_chat(file_path, selected_sender=None):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            chat = file.read()
    except FileNotFoundError:
        raise FileNotFoundError("Chat file not found. Make sure the file path is correct.")
    
    # Extract messages into a DataFrame
    df = extract_messages(chat)
    
    # Total messages and message counts per sender
    total_messages = len(df)
    message_counts = df['Sender'].value_counts()
    
    # Top emojis used
    all_emojis = [c for msg in df['Message'] for c in msg if c in emoji.EMOJI_DATA]
    top_emojis = Counter(all_emojis).most_common(10)
    
    # Normalize messages to lowercase for consistent analysis
    df['Message_normalized'] = df['Message'].str.lower()
    
    # Top 10 most common messages (case-insensitive)
    top_10_messages = df['Message_normalized'].value_counts().head(10)
    
    # Top 10 words used (case-insensitive, excluding excluded words)
    excluded_words = ['image', 'video', 'sticker', 'omitted']
    words = re.findall(r'\b\w+\b', ' '.join(df['Message']).lower())
    filtered_words = [word for word in words if word not in excluded_words]
    top_words = Counter(filtered_words).most_common(10)
    
    # First encounter
    first_encounter = df.iloc[0] if not df.empty else None
    
    # Messages arranged according to time of day
    df['Hour'] = pd.to_datetime(df['Time'], format='%I:%M %p').dt.hour
    messages_by_hour = df.groupby('Hour').size()
    
    # Plot messages arranged by time of day
    plt.figure(figsize=(10, 6))
    messages_by_hour.plot(kind='bar', color='skyblue')
    plt.title('Messages by Time of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Number of Messages')
    plt.show()

    # Count occurrences of specific negative responses (case-insensitive)
    negative_responses = ['no', 'nope', 'nahi']
    
    if selected_sender:
        user_responses = df[(df['Sender'] == selected_sender) & (df['Message_normalized'].isin(negative_responses))]
        user_no_count = len(user_responses)
        return {
            'message_counts': message_counts,
            'total_messages': total_messages,
            'top_emojis': top_emojis,
            'top_10_messages': top_10_messages,
            'top_words': top_words,
            'first_encounter': first_encounter,
            'user_no_count': user_no_count,
            'selected_sender': selected_sender
        }
    else:
        user_no_counts = df[df['Message_normalized'].isin(negative_responses)].groupby('Sender').size()
        return {
            'message_counts': message_counts,
            'total_messages': total_messages,
            'top_emojis': top_emojis,
            'top_10_messages': top_10_messages,
            'top_words': top_words,
            'first_encounter': first_encounter,
            'user_no_counts': user_no_counts
        }

# File path of the exported WhatsApp chat
file_path = '_chat.txt'

# Select a sender or leave it as None for general user analysis
selected_sender = None  # Replace with 'Name' to analyze a specific user

# Process the chat data
details = process_whatsapp_chat(file_path, selected_sender)

# Print the details
print("Message counts:\n", details['message_counts'])
print("\nTotal messages:", details['total_messages'])
print("\nTop 10 emojis:", details['top_emojis'])
print("\nTop 10 most common messages and their counts (case-insensitive):\n", details['top_10_messages'])
print("\nTop 10 words:", details['top_words'])
print("\nFirst encounter:\n", details['first_encounter'])

if selected_sender:
    print(f"\nNumber of times {details['selected_sender']} sent 'No', 'Nope', or 'Nahi':", details['user_no_count'])
else:
    print("\nNegative response counts for all users:\n", details['user_no_counts'])