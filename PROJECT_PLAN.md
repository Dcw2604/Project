An interactive exam chatbot system for students, where the teacher defines the exam and the bot delivers the questions, collects the student's answers, and analyzes their understanding by topic.

✅ Phase 1: File Ingestion and Question Generation
🔹 Task 1.1: Upload and Process the Input File
Allow the teacher to upload a file (PDF, DOCX, etc.) that contains the study material.

Use an OCR engine (like Tesseract or Mathpix for math content) to extract readable text from the file if needed.

Preprocess the text: clean formatting, remove irrelevant content, segment by topic or section.

🔹 Task 1.2: Automatically Generate High-Quality Questions
Use a local or external LLM (e.g., LLaMA3 via Ollama or OpenAI GPT) to generate diverse question types based on the document.

Ensure each question is tagged with a specific topic, e.g., "fractions", "derivatives", "sorting algorithms", etc.

Store the generated questions in a database or JSON file, including:

Question text

Topic

Difficulty level (if applicable)

Correct answer (optional, for evaluation later)

✅ Phase 2: Exam Creation by the Teacher
🔹 Task 2.1: Define the Exam
Provide a simple UI or form for the teacher to:

Select number of questions

Select topics or allow random topic distribution

Optionally set a time limit per question (optional)

The system will generate an “exam session” based on the teacher's settings.

🔹 Task 2.2: Store Exam Configuration
Save the exam structure with metadata:

Teacher ID

List of selected questions

Start time, end time (optional)

Student assigned (optional for personalized exams)

✅ Phase 3: Student-Chat Interaction (Exam Mode)
🔹 Task 3.1: Start an Exam Session
When the student starts the exam:

The chatbot greets the student.

Sends only the first question to the student (no answer or hints).

Waits for a student response.

🔹 Task 3.2: Collect and Store Answers
For each student reply:

Save the response (question ID + student answer) in a database.

Store timestamp and interaction log.

Proceed to the next question until the exam ends.

🔹 Task 3.3: End Exam Session
When all questions have been answered:

Thank the student.

End the session and mark it as completed in the database.

✅ Phase 4: Analysis and Teacher Dashboard
🔹 Task 4.1: Analyze Student Performance
For each answer:

Optionally compare to the correct answer (if available).

Use NLP or logic to determine correctness (exact match or similarity).

Assign a score or qualitative grade (correct / partially correct / wrong).

🔹 Task 4.2: Evaluate Topic-Level Knowledge
Group performance by topic:

E.g., 2/3 correct answers in "fractions" → 66% mastery

Generate a visual report for the teacher:

Table or chart showing topic-level understanding.

🔹 Task 4.3: Display Results to the Teacher
Build a dashboard where the teacher can:

View individual student performance.

View per-topic analysis.

Export results (CSV, PDF, etc.)

✅ Phase 5: Optional Enhancements
🔹 Task 5.1: Feedback for Student
After the exam is graded, optionally send the student a summary of:

Topics they did well in

Topics they should review

Sample correct answers or explanations (optional)

🔹 Task 5.2: Continuous Learning Mode (not just exams)
Allow students to practice in a "learning mode" where the chatbot teaches instead of testing.

Give hints and explanations after each answer.