## Baseline Evaluation (Base: qwen3:8b)

Part 1: System Instruction

Following text provides the system instructions as rules for the model:

Instruction: "You are a strict Data Compliance Agent. Rewrite the input text exactly word-for-word. You must replace all Personally Identifiable Information (PII)—including names, phone numbers, addresses, account numbers, and email addresses—with standardized tags like [NAME], [PHONE], [ADDRESS], and [ID]. Do not summarize. Do not explain your actions. If no PII is found, return the text exactly as is."

Test 1: Stochasticity Test

Goal: See if the model stays consistent when asked the same thing multiple times.
The Prompt (Run 3 times in fresh sessions):

Input: "Patient Michael Thompson (DOB: 05/12/1984) was seen at St. Jude Medical Center by Dr. Aris Thorne. Michael can be reached at m.thompson84@email.com or 555-928-1102. Please update his file."

Expected Output: "Patient [NAME] (DOB: [DATE]) was seen at [LOCATION] by Dr. [DOCTOR]. [NAME] can be reached at [EMAIL] or [PHONE]. Please update his file."

Results:

Run 1: "Patient [NAME] ([DOB]) was seen at St. Jude Medical Center by [NAME]. [NAME] can be reached at [EMAIL] or [PHONE]. Please update his file."

Primary Failure: Critical Entity Miss

Observations: Failed to redact "St. Jude Medical Center" (Location). Used [DOB] for date.

Run 2: "Patient [NAME] (DOB: [DOB]) was seen at St. Jude Medical Center by [NAME]. [NAME] can be reached at [EMAIL] or [PHONE]. Please update his file."

Primary Failure: Critical Entity Miss

Observations: Failed to redact "St. Jude Medical Center" (Location). Used [DOB] for date.

Run 3: "Patient [NAME] (DOB: [DOB]) was seen at St. Jude Medical Center by Dr. [NAME]. [NAME] can be reached at [EMAIL] or [PHONE]. Please update his file."

Primary Failure: Tag and Prose Drift

Observations: Missed "St. Jude." Included "Dr." prefix inside the redacted string, and changed tag format.


Test 2: Generalization Test

Goal: See if the model can handle different formats of PII and different writing styles

Input A: "Hey, this is Sarah Jennings. I'm calling about my account ending in 9928. I moved from 420 High St, Denver to 1102 Oak Ave, Austin, and my billing is still messed up. My cell is 512-555-0100."

Input B: "To: dev-team@startup.io | From: t.ross@gmail.com. Team, please send the API keys to Thomas Ross at his home office: 99 Broadway, NYC. If he’s not there, try his personal line: 917-555-3321. Thanks, Jessica."

Input C: "ERROR 404 - User(id=99281, name='Leonard McCoy', ip='192.168.1.1') failed login at 14:02 from Enterprise Way, San Francisco, CA. Contact admin at mccoy.l@starfleet.edu."

Output A: Hey, this is [NAME]. I'm calling about my account ending in [ID]. I moved from [ADDRESS] to [ADDRESS], and my billing is still messed up. My cell is [PHONE]."

Result: Pass

Observations: Successfully identified account numbers and addresses in a conversational tone.

Output B: "To: [EMAIL] | From: [EMAIL]. Team, please send the API keys to [NAME] at his home office: [ADDRESS]. If he’s not there, try his personal line: [PHONE]. Thanks, [NAME]."

Result: Partial Pass

Observations: Correctly redacted names/addresses, but struggled with "word-for-word" spacing/formatting.

Output C: "ERROR 404 - User(id=[ID], name=[NAME], ip=[IP]) failed login at 14:02 from [ADDRESS]. Contact admin at [EMAIL]."

Result: Pass

Observations: Caught the IP address and User ID within a technical log format.

