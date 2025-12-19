#!/usr/bin/env python
# Test parse_question_and_answers function

from apps.klasifikasi.file_extractor import QuestionExtractor

extractor = QuestionExtractor()

# Test Q2 (should have clear answers)
test_q2 = """What does fiduciary responbility mean? a. To use information gained for personal interests without breaching confidentiality of the client. b. To act for the benefit of another person and place the responbilities to be fair and honest ahead of your own interest. c. To follow the desires of the client and maintain total confidentiality even if illegal acts are discovered. The auditor shall never disclose information from an audit in order to protect the client. d. None of the above."""

result = extractor.parse_question_and_answers(test_q2)

print("=== TEST Q2 PARSING ===")
print(f"Question: {result['question'][:100]}...")
print(f"\nAnswers ({len(result['answers'])} found):")
for ans in result['answers']:
    print(f"  {ans['choice'].upper()}. {ans['text'][:80]}...")
print(f"\nIs Multiple Choice: {result['is_multiple_choice']}")

# Test Q3 (another example)
test_q3 = """What are common types of audits? a. forensic, accounting, verification, regulatory b. integrated, operational, compliance, administrative c. financial, SAS-74, compliance, administrative d. information system, SAS-70, regulatory , procedural"""

result3 = extractor.parse_question_and_answers(test_q3)

print("\n=== TEST Q3 PARSING ===")
print(f"Question: {result3['question']}")
print(f"\nAnswers ({len(result3['answers'])} found):")
for ans in result3['answers']:
    print(f"  {ans['choice'].upper()}. {ans['text']}")
print(f"\nIs Multiple Choice: {result3['is_multiple_choice']}")
