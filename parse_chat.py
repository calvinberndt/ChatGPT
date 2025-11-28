import json
import os

def parse_chatgpt_conversation(json_data):
    """
    Parses a ChatGPT conversation JSON object (DAG structure) 
    into a linear list of messages.
    """
    # 1. Access the mapping and the leaf node
    mapping = json_data.get('mapping', {})
    current_node_id = json_data.get('current_node')
    
    if not mapping or not current_node_id:
        return "Error: Invalid JSON structure (missing mapping or current_node)"

    conversation = []

    # 2. Traverse backwards from Leaf -> Root
    while current_node_id:
        node = mapping.get(current_node_id)
        if not node:
            break
            
        message = node.get('message')
        
        # 3. Filter valid messages (Skip system updates or empty nodes)
        if message and message.get('content') and message.get('author'):
            author_role = message['author']['role']
            content_type = message['content']['content_type']
            parts = message['content'].get('parts', [])
            
            # Text formatting
            text_content = ""
            if parts:
                # Handle standard text and tool outputs
                text_content = "".join([str(p) for p in parts if p is not None])
            
            # Exclude empty system messages or hidden context updates
            if text_content and author_role != 'system':
                timestamp = message.get('create_time')
                conversation.append({
                    'role': author_role,
                    'text': text_content,
                    'timestamp': timestamp,
                    'model': message.get('metadata', {}).get('model_slug')
                })

        # Move to parent
        current_node_id = node.get('parent')

    # 4. Reverse to get chronological order (Root -> Leaf)
    return conversation[::-1]

# --- Usage Example ---

# Assuming you saved your text block to 'ray_chat.json'
input_filename = 'ray_chat.json'
with open(input_filename, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

chats = parse_chatgpt_conversation(raw_data)

# Export formatted output to .txt file with same base name as input
base_name = os.path.splitext(input_filename)[0]
output_filename = f'{base_name}.txt'
with open(output_filename, 'w', encoding='utf-8') as f:
    f.write(f"Title: {raw_data.get('title')}\n" + "="*30 + "\n")
    for msg in chats:
        role = msg['role'].upper()
        f.write(f"\n[{role}]:\n")
        f.write(f"{msg['text']}\n")
        f.write("-" * 20 + "\n")

print(f"Output exported to {output_filename}")