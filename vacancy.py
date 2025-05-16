import argparse
import pymupdf
import re
import json

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

        if re.match(r"Vacancy VN-\d+", block_text):
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
                [_, detail] = block_text.split("\n", 1)
                [contact, number] = detail.split(",")

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


def main():
    parser = argparse.ArgumentParser(description="Extract vacancy information from a PDF file.")
    parser.add_argument("pdf_file", help="The path to the PDF file.")
    args = parser.parse_args()

    pdf_file_path = args.pdf_file
    blocks = extract_text_with_layout(pdf_file_path)

    if isinstance(blocks, str) and blocks.startswith("Error"):
        print(blocks)
    else:
        extracted_vacancies = parse_vacancies_with_layout(blocks)
        print(json.dumps(extracted_vacancies, indent=2))

if __name__ == "__main__":
    main()
