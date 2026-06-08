from app.file_processor import extract_text_from_file

file_path = "sample.txt"
filename = "sample.txt"

text = extract_text_from_file(file_path, filename)

print(text[:1000])