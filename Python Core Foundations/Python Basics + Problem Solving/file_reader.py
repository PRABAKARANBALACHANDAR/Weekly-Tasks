filename = 'business_51.txt'

with open(filename, 'r') as file:
    content = file.read()
line_count = content.count('\n') + 1 if content else 0
word_count = len(content.split())  
print(f"Number of lines: {line_count}")
print(f"Number of words: {word_count}")