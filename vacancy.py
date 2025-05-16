import csv
import os
import pymupdf
import re
import sys

def get_current_exe_dir():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.abspath(__file__))

def extract_text_with_layout(pdf_path):
    blocks = []
    try:
        doc = pymupdf.open(pdf_path)
        for page in doc:
            blocks.extend(page.get_text("blocks"))
        doc.close()
    except FileNotFoundError:
        return f"Error: File not found at {pdf_path}"
    except Exception as e:
        return f"An error occurred: {e}"
    return blocks

def parse_vacancies_with_layout(blocks):
    vacancies = []
    job = {}

    for index, block in enumerate(blocks):
        block_text = block[4].strip()

        if "Vacancy VN-" in block_text:
            parts = block_text.split("\n", 1)

            if len(parts) == 2:
                detail = parts[1]
                [_, vacancy] = parts[1].split(" ")
            else:
                [_, vacancy] = block_text.split(" ")

            job["vacancy"] = vacancy
            client = blocks[index + 1][4].strip()
            job["client"] = " ".join(client.split("\n"))
        elif job:
            if "Job Title" in block_text:
                if block_text == "Job Title":
                    detail = blocks[index + 1][4].strip()
                    job["job_title"] = " ".join(detail.split("\n"))
                else:
                    job["job_title"] = parse_detail_in_block(block_text)
            elif "Job Type" in block_text:
                job["job_type"] = parse_detail_in_block(block_text)
            elif re.match(r"^Location", block_text):
                job["location"] = parse_detail_in_block(block_text)
            elif "Salary" in block_text:
                job["salary"] = parse_detail_in_block(block_text)
            elif "Future Merit" in block_text:
                parts = block_text.split("\n", 2)

                if len(parts) == 2:
                    detail = blocks[index + 1][4].strip()
                    job["future_merit_locations"] = " ".join(detail.split("\n"))
                else:
                    job["future_merit_locations"] = " ".join(parts[2].split("\n"))
            elif "Office Arrangement" in block_text:
                parts = block_text.split("\n", 2)

                if len(parts) == 2:
                    if parts[1] == "Details":
                        detail = blocks[index + 1][4].strip()
                        job["office_arrangement_details"] = " ".join(detail.split("\n"))
                    else:
                        job["office_arrangement"] = " ".join(parts[1].split("\n"))
                else:
                    job["office_arrangement_details"] = " ".join(parts[2].split("\n"))
            elif "Classification" in block_text:
                job["classification"] = parse_detail_in_block(block_text)
            elif "Position Number" in block_text:
                job["position_number"] = parse_detail_in_block(block_text)
            elif "Agency Website" in block_text:
                job["agency_website"] = parse_detail_in_block(block_text)
            elif "Position Contact" in block_text:
                parts = block_text.split("\n", 2)
                parts_length = len(parts)

                if parts_length == 3:
                    job["position_contact"] = parts[0] + ", " + parts[1]
                elif parts_length == 2:
                    [contact, number] = parts

                    job["position_contact"] = contact.strip()
                    job["contact_number"] = number.strip()
            elif "Agency Recruitment Site" in block_text:
                job["agency_recruitment_site"] = parse_detail_in_block(block_text)
                vacancies.append(job)
                job = {}

    return vacancies

def parse_detail_in_block(text):
    parts = text.split("\n", 1)
    detail = text if len(parts) == 1 else parts[1]

    return " ".join(detail.split("\n"))

def write_to_csv(vacancies):
    file_path = get_current_exe_dir() + "/vacancies.csv"

    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = vacancies[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(vacancies)

def main():
    pdf_file_path = get_current_exe_dir() + "/gazette.pdf"
    blocks = extract_text_with_layout(pdf_file_path)

    vacancies = parse_vacancies_with_layout(blocks)
    write_to_csv(vacancies)

if __name__ == "__main__":
    main()
