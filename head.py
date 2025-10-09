from ingest import parse_all_data_folder

def print_first_three_chunks():
    excel_chunks, other_chunks = parse_all_data_folder()
    print("First 3 Excel chunks:")
    for chunk in excel_chunks[:3]:
        print(chunk)
    print("\nFirst 3 Other (PDF/DOCX) chunks:")
    for chunk in other_chunks[:3]:
        print(chunk)

if __name__ == "__main__":
    print_first_three_chunks()