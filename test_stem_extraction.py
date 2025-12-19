#!/usr/bin/env python
# Test the extract_question_stem_only function

from apps.klasifikasi.file_extractor import QuestionExtractor

extractor = QuestionExtractor()

# Test cases
test_questions = [
    "What is the difference between a policy and a procedure? a. Compliance to a policy is discretionary , and compliance to a procedure is mandatory . b. A procedure provides discetionary advice to aid in decision making. The policy defines specific requirements to ensure compliance. c. A policy is a high – level document signed by a person of authority , and compliance is mandatory . A procedure defines the mandatory steps to attain compliance. d. A policy is a mid – level document issued to advise the reader of desired actions in the absence of a standard .",
    "What does fiduciary responbility mean? a. To use information gained for personal interests without breaching confidentiality of the client. b. To act for the benefit of another person and place the responbilities to be fair and honest ahead of your own interest. c. To follow the desires of the client and maintain total confidentiality even if illegal acts are discovered. The auditor shall never disclose information from an audit in order to protect the client. d. None of the above.",
    "What are common types of audits? a. forensic, accounting, verification, regulatory b. integrated, operational, compliance, administrative c. financial, SAS-74, compliance, administrative d. information system, SAS-70, regulatory , procedural"
]

print("=== TESTING extract_question_stem_only ===\n")

for i, q in enumerate(test_questions, 1):
    stem = extractor.extract_question_stem_only(q)
    print(f"Q{i}:")
    print(f"  Original length: {len(q)} chars")
    print(f"  Stem length: {len(stem)} chars")
    print(f"  Stem: {stem[:100]}...")
    print()
