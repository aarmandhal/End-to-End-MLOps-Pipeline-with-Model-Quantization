import os
import re
import json
from dotenv import load_dotenv
from huggingface_hub import login
from datasets import load_dataset

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
login(token=HF_TOKEN)

def replace_tag(match):
    label_map = {
        "FIRSTNAME": "[NAME]",
        "LASTNAME": "[NAME]",
        "MIDDLENAME": "[NAME]",
        "USERNAME": "[NAME]",
        "EMAIL": "[EMAIL]",
        "STREET": "[ADDRESS]",
        "BUILDINGNUMBER": "[ADDRESS]",
        "ZIPCODE": "[ADDRESS]",
        "CITY": "[ADDRESS]",
        "STATE": "[ADDRESS]",
        "COUNTRY": "[ADDRESS]",
        "CREDITCARDNUMBER": "[FINANCIAL]",
        "IBAN": "[FINANCIAL]",
        "CVV": "[FINANCIAL]",
        "DATEOFBIRTH": "[DATE]",
        "AGE": "[DATE]",
        "TELEPHONENUM": "[PHONE]",
        "PHONE": "[PHONE]",
        "IPADDRESS": "[IP_ADDRESS]",
        "SSN": "[ID]",
        "PASSPORT": "[ID]",
        "DRIVERSLICENSE": "[ID]"
    }
    base_label = match.group(1).upper()
    return label_map.get(base_label, match.group(0))

def format_to_chatml(raw_row, system_prompt):
    formatted_data = {"Instruction": system_prompt}
    formatted_data["Input"] = raw_row["source_text"]
    masked_text = raw_row["masked_text"]
    masked_text = re.sub(r'\[([A-Z]+)_[0-9]+\]', replace_tag, masked_text)
    formatted_data["Output"] = masked_text

    return formatted_data


def fetch_and_process_data(dataset_name, system_prompt, output_path):
    TARGET_RARE = 1000
    TARGET_DENSE = 2000
    TARGET_STANDARD = 1500 
    TARGET_NEGATIVE = 500
    rare_count = 0
    dense_count = 0
    standard_count = 0
    negative_count = 0
    f = open(output_path, "w")
    dataset = load_dataset(dataset_name, split="train", streaming=True)
    tags = r'\[[A-Z]+_[0-9]+\]'
    rare_tag = r'\[(CREDITCARDNUMBER|IPADDRESS|SSN|IBAN|PASSPORT|DRIVERSLICENSE)_[0-9]+\]'

    for row in dataset:
        text = row["masked_text"]
        tag_count = len(re.findall(tags, text))
        is_rare = re.search(rare_tag, text)
        
        if standard_count == TARGET_STANDARD and rare_count == TARGET_RARE and dense_count == TARGET_DENSE and negative_count == TARGET_NEGATIVE:
            break
        
        if tag_count == 0:
            if negative_count < TARGET_NEGATIVE:
                negative_count += 1
                f.write(json.dumps(format_to_chatml(row, system_prompt)) + "\n")
        
        elif is_rare:
            if rare_count < TARGET_RARE:
                rare_count += 1
                f.write(json.dumps(format_to_chatml(row, system_prompt)) + "\n")
        
        elif tag_count >= 3:
            if dense_count < TARGET_DENSE:
                dense_count += 1
                f.write(json.dumps(format_to_chatml(row, system_prompt)) + "\n")
        elif tag_count == 1 or tag_count == 2:
            if standard_count < TARGET_STANDARD:
                standard_count += 1
                f.write(json.dumps(format_to_chatml(row, system_prompt)) + "\n")
    
    f.close()

def main():
    system_prompt = (
        "You are an enterprise data sanitization AI. Your strict task is to redact Personally Identifiable Information (PII) from the user's input. "
        "You must replace all sensitive entities using ONLY the following standardized tags: "
        "[NAME], [EMAIL], [ADDRESS], [FINANCIAL], [DATE], [PHONE], [IP_ADDRESS], [ID]. "
        "Do not invent new tags, do not add conversational filler, and do not change the original sentence structure. Output only the fully redacted text."
    )
    
    fetch_and_process_data("ai4privacy/pii-masking-400k", system_prompt, "data/processed/train_dataset.jsonl")


if __name__ == "__main__":
    main()