from llama_cpp import Llama
import re
import os

class Redactor:
    def __init__(self, model_path: str):
        self.llm = Llama(model_path=model_path, n_gpu_layers=-1, n_ctx=2048)
        
        self.label_map = {
            "NAME": "[NAME]", "GIVENNAME": "[NAME]", "SURNAME": "[NAME]", 
            "FIRSTNAME": "[NAME]", "LASTNAME": "[NAME]", "MIDDLENAME": "[NAME]",
            "ACCOUNTNAME": "[NAME]", "USERNAME": "[NAME]", "USERNNAME": "[NAME]",
            "PERSONALTITLE": "[NAME]", "ORG": "[NAME]", "ORG_NAME": "[NAME]", "COMPANYNAME": "[NAME]",

            "ADDRESS": "[ADDRESS]", "STREET": "[ADDRESS]", "STREETNAME": "[ADDRESS]",
            "CITY": "[ADDRESS]", "STATE": "[ADDRESS]", "ZIPCODE": "[ADDRESS]",
            "COUNTRY": "[ADDRESS]", "BUILDINGNUM": "[ADDRESS]", "SUBSTATE": "[ADDRESS]",
            "ISO": "[ADDRESS]", "SCHOOL": "[ADDRESS]", "JOBAREA": "[ADDRESS]", "JOBTYPE": "[ADDRESS]",

            "FINANCIAL": "[FINANCIAL]", "ACCOUNTNUM": "[FINANCIAL]", "AMOUNT": "[FINANCIAL]",
            "CREDITCARDNUMBER": "[FINANCIAL]", "IBAN": "[FINANCIAL]", "CVV": "[FINANCIAL]",
            "CREDITCARDISSUER": "[FINANCIAL]", "OTP": "[FINANCIAL]", "CREDRATING": "[FINANCIAL]",

            "DATE": "[DATE]", "DATEOFBIRTH": "[DATE]", "AGE": "[DATE]", "TIME": "[DATE]",

            "PHONE": "[PHONE]", "TELEPHONENUM": "[PHONE]", "PHONE_IMEI": "[PHONE]",

            "IPADDRESS": "[IP_ADDRESS]", "IP_ADDRESS": "[IP_ADDRESS]", "IPS": "[IP_ADDRESS]", 
            "MACADDRESS": "[IP_ADDRESS]", "URL": "[IP_ADDRESS]", "IPV4": "[IP_ADDRESS]", "IPV6": "[IP_ADDRESS]",

            "ID": "[ID]", "SSN": "[ID]", "PASSPORT": "[ID]", "PASSPORTNUM": "[ID]",
            "DRIVERSLICENSE": "[ID]", "DRIVERLICENSENUM": "[ID]", "SOCIALNUM": "[ID]",
            "TAXNUM": "[ID]", "IDCARDNUM": "[ID]", "DOCNUM": "[ID]", "VEHICLEVRM": "[ID]",
            "SOCIAL": "[ID]",

            "EMAIL": "[EMAIL]"
        }

    def replace_tag(self, match):
        base_label = match.group(1).upper()
        return self.label_map.get(base_label, f"[{base_label}]")

    def create_prompt(self, text):
        prompt = f"""<|im_start|>system
You are an enterprise data sanitization AI. 
Your strict task is to redact Personally Identifiable Information (PII) from the user's input. 
You must replace all sensitive entities using ONLY the following standardized tags: 
[NAME], [EMAIL], [ADDRESS], [FINANCIAL], [DATE], [PHONE], [IP_ADDRESS], [ID]. 
Do not invent new tags, do not add conversational filler, and do not change the original sentence structure. 
Output only the fully redacted text.<|im_end|>
<|im_start|>user
{text}<|im_end|>
<|im_start|>assistant
"""
        return prompt

    def clean_output(self, text):
        text = re.sub(r'\[([A-Z0-9]+)_[0-9]+\]', self.replace_tag, text)
        text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '[EMAIL]', text)
        text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_ADDRESS]', text)
        text = re.sub(r'\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b', '[IP_ADDRESS]', text)
        text = re.sub(r'\b(?:\d{3}|\*{3})-(?:\d{2}|\*{2})-\d{4}\b', '[ID]', text)
        text = re.sub(r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[FINANCIAL]', text)
        text = re.sub(r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b', '[FINANCIAL]', text)

        return text

    def process_text(self, user_input: str) -> str:
        prompt = self.create_prompt(user_input)
        
        raw_output = self.llm(
            prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
            top_p=0.9,
            top_k=40,
            echo=False,
            stop=["<|im_end|>", "<|endoftext|>"], 
        )
        
        model_generated_text = raw_output['choices'][0]['text'].strip()
        final_text = self.clean_output(model_generated_text)
        
        return final_text

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_model_path = os.path.join(current_dir,"..", "models", "quantized_gguf", "pii-redactor-qwen-q4_k_m.gguf")
    
    redactor_app = Redactor(model_path=test_model_path)
    
    test_string = "Hello, my name is John Doe, I live at 123 Main St, and my IP is 192.168.1.1."
    print("\n--- STARTING TEST ---")
    print(f"Original: {test_string}")
    
    result = redactor_app.process_text(test_string)
    
    print(f"Redacted: {result}")
    print("--- TEST COMPLETE ---\n")