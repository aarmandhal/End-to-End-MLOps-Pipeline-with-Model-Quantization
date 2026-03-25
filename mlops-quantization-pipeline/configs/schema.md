# PII Redaction Standardization Schema

This document defines the strict, standardized tags the fine-tuned model must use when redacting Personally Identifiable Information (PII). The model must not invent new tags, guess formatting, or leave sensitive data exposed. 

## 1. Personal Identity
* **Target:** First names, last names, middle initials, user handles.
* **Tag to Use:** `[NAME]`
* **Example:** "Please contact `[NAME]` regarding the issue."

## 2. Contact Information
* **Target:** Phone numbers (all formats/country codes), fax numbers.
* **Tag to Use:** `[PHONE]`
* **Example:** "Reach me at `[PHONE]`."
* **Target:** Email addresses.
* **Tag to Use:** `[EMAIL]`
* **Example:** "Sent from `[EMAIL]`."

## 3. Locations and Facilities
* **Target:** Street addresses, cities, states, zip codes.
* **Tag to Use:** `[ADDRESS]`
* **Example:** "Package delivered to `[ADDRESS]`."
* **Target:** Names of hospitals, clinics, specific office branches, or company HQ names.
* **Tag to Use:** `[FACILITY]`
* **Example:** "Patient was transferred to `[FACILITY]`." *(Note: This was a primary failure point in the baseline model).*

## 4. Dates & Times
* **Target:** Birthdays, appointment dates, specific historical dates linked to a user.
* **Tag to Use:** `[DATE]`
* **Example:** "Patient DOB is `[DATE]`." *(Note: Do not use [DOB] or [TIME]; standardize all to [DATE]).*

## 5. Financial & Identifiers
* **Target:** Credit card numbers, bank routing numbers, dollar amounts tied to specific personal accounts.
* **Tag to Use:** `[FINANCIAL]`
* **Example:** "The account ending in `[FINANCIAL]` was charged."
* **Target:** SSNs, Patient IDs, Employee IDs, Driver's Licenses, UserIDs.
* **Tag to Use:** `[ID]`
* **Example:** "User `[ID]` logged into the portal."

## 6. Digital & Network
* **Target:** IP addresses, MAC addresses.
* **Tag to Use:** `[IP_ADDRESS]`
* **Example:** "Login attempt from `[IP_ADDRESS]`."