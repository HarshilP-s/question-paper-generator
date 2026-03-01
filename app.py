
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import mysql.connector
from flask import flash
from templates_config import TEMPLATES



# ------------------- Configuration -------------------
app = Flask(__name__)
app.secret_key = "dev-secret-key-123"
app.config['UPLOAD_FOLDER'] = "uploads"

# Make sure upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# ------------------- Database Connection -------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MySQL@Root2025!",
    database="question_paper_db"
)
cursor = db.cursor(dictionary=True)  # dictionary=True allows using column names

# ------------------- Routes -------------------

# Home route - redirect to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# ------------------- Register -------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # plain text password
        university = request.form['university']

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("Email already registered. Please login instead.", "danger")
            return redirect(url_for('register'))

        # Insert user into database
        cursor.execute(
            "INSERT INTO users (name, email, password, university) VALUES (%s, %s, %s, %s)",
            (name, email, password,university)  # store plain password directly
        )
        db.commit()
        flash("Registration successful! Please login.", "success")

        return redirect('/login')

    return render_template('register.html')


# ------------------- Login -------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']  # plain text password

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE name=%s", (name,))
        user = cursor.fetchone()

        # Check password directly
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['name'] = user['name']
            return redirect(url_for('welcome')) 
        else:
            return "Invalid username or password!"

    return render_template('login.html')

# ------------------- Logout -------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
#---------welcome page-------------------------
@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect('/login')

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT name, university FROM users WHERE id=%s",
        (session['user_id'],)
    )
    user = cursor.fetchone()

    return render_template('welcome.html', user=user)
#---------------paper setup`````````````````````````````
@app.route('/paper_setup', methods=['GET', 'POST'])
def paper_setup():

    if request.method == 'POST':

        # -------- FILE UPLOAD --------
        file = request.files['syllabus']
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # -------- FORM DATA --------
        university = request.form['university']
        exam_date = request.form['exam_date']
        subject = request.form['subject']
        difficulty = request.form['difficulty']
        exam_time = request.form['exam_time']

        total_marks = int(request.form['total_marks'])
        marks_mode = request.form['marks_mode']
        if marks_mode not in ["fixed", "alternate"]:
            return "Selected marking mode is not implemented yet."

        # -------- Marks Mode Handling --------
        marks_per_question = None
        alternate_pattern = None

        if marks_mode == "fixed":
            marks_per_question = int(request.form.get('marks_per_question', 0))

        elif marks_mode == "alternate":
            alternate_pattern = request.form.get('alternate_pattern')
            if not alternate_pattern:
                return "Please select an alternate marking pattern."

        # -------- Instructions (Customizable) --------
        instructions = request.form.get('instructions', '').strip()
        # If teacher types NA, treat as None (hide instructions)
        if instructions.lower() == "na":
            instructions = None

        # -------- SAVE IN SESSION --------
        session['paper_setup'] = {
            'filepath': filepath,
            'university': university,
            'exam_date': exam_date,
            'subject': subject,
            'difficulty': difficulty,
            'exam_time': exam_time,
            'total_marks': total_marks,
            'marks_mode': marks_mode,
            'marks_per_question': marks_per_question,
            'alternate_pattern': alternate_pattern,
            'total_sets': 6,
            'instructions': instructions  # ✅ new field
        }

        return redirect(url_for('select_template'))

    return render_template('paper_setup.html')



#----------------tamplets selections-----------------------
import random
import copy

# ---------------- Dummy Question Bank ----------------
# Expand this list to ensure enough unique dummy questions for preview
QUESTION_BANK = [
    # Programming & Data Structures
    "Explain the concept of recursion",
    "Describe the OSI model layers",
    "What is normalization in databases?",
    "Explain polymorphism in OOP",
    "Discuss the differences between TCP and UDP",
    "What is a binary search algorithm?",
    "Explain deadlock in operating systems",
    "Describe the lifecycle of a thread",
    "What is a hash function?",
    "Explain the difference between stack and queue",
    "What is a linked list?",
    "Explain inheritance in Java",
    "Explain exception handling in Python",
    "Describe graph traversal algorithms",
    "What is a binary tree?",
    "Explain dynamic programming with example",
    "What is memoization?",
    "Explain sorting algorithms with complexity",
    "Describe heap data structure",
    "What is a trie?",
    
    # Databases
    "Discuss primary vs foreign keys",
    "Explain SQL joins",
    "What is a transaction in DBMS?",
    "Explain ACID properties",
    "Describe indexing in databases",
    "What is a stored procedure?",
    "Explain triggers in SQL",
    "Discuss NoSQL databases",
    "What is MongoDB?",
    "Explain CAP theorem",
    
    # Operating Systems
    "What is cloud computing?",
    "Explain REST API architecture",
    "Describe the concept of virtual memory",
    "Explain paging in OS",
    "What is a semaphore?",
    "Explain scheduling algorithms",
    "Describe file system hierarchy",
    "What is a process vs thread?",
    "Explain interprocess communication",
    "What is a kernel?",
    
    # Networking
    "Describe caching mechanisms",
    "What is DNS?",
    "Explain load balancing",
    "What is IPv6?",
    "Explain difference between HTTP and HTTPS",
    "Describe TCP handshake",
    "What is a firewall?",
    "Explain VPN",
    "What is a proxy server?",
    "Describe QoS in networking",
    
    # Software Engineering
    "Explain MVC architecture",
    "Discuss Agile methodology",
    "What is continuous integration?",
    "Explain DevOps pipeline",
    "What is version control?",
    "Describe Git branching strategies",
    "Explain software testing types",
    "What is unit testing?",
    "Explain regression testing",
    "Describe SDLC phases",
    
    # Web & Cloud
    "Discuss responsive web design",
    "What is JSON?",
    "Explain API rate limiting",
    "What is Docker used for?",
    "What is Kubernetes?",
    "Explain microservices architecture",
    "What is a CDN?",
    "Describe caching in web apps",
    "Explain serverless computing",
    "What is cloud deployment model?",
    
    # Security
    "Describe encryption vs hashing",
    "Explain symmetric vs asymmetric encryption",
    "What is SSL/TLS?",
    "Explain authentication vs authorization",
    "What is OAuth?",
    "Describe common cyber attacks",
    "Explain SQL injection",
    "What is XSS?",
    "Explain CSRF",
    "Describe role of IDS/IPS",
    
    # AI & Emerging Tech
    "Explain machine learning basics",
    "What is a neural network?",
    "Describe supervised vs unsupervised learning",
    "Explain reinforcement learning",
    "What is deep learning?",
    "Explain natural language processing",
    "What is computer vision?",
    "Describe clustering algorithms",
    "Explain decision trees",
    "What is blockchain?",
    
    # Miscellaneous
    "What is a compiler?",
    "Explain garbage collection in Java",
    "Describe RAID levels",
    "What is a virtual machine?",
    "Explain session vs cookie",
    "What is caching in OS?",
    "Explain CAPEX vs OPEX in IT",
    "What is data warehousing?",
    "Describe clustering in big data",
    "Explain IoT basics",
]
# ---------------- MCQ Generator ----------------
def generate_mcq_from_topic(topic):
    """
    Generate a simple MCQ style question from a topic.
    """
    q_text = f"Which of the following best describes {topic}?"
    options = [
        f"A) Basic definition of {topic}",
        f"B) Example related to {topic}",
        f"C) Advantage of {topic}",
        f"D) Limitation of {topic}"
    ]
    return q_text, options


# ---------------- Template Generator ----------------
def generate_template(template, marks_list, topics, used_flags,
                      dummy_mode=False, dummy_flags=None):
    template = copy.deepcopy(template)
    sections_out = []
    mark_index = 0

    while mark_index < len(marks_list):
        marks = marks_list[mark_index]

        # Pick topic
        if dummy_mode:
            available_dummy = [q for q in QUESTION_BANK if not dummy_flags.get(q, False)]
            if not available_dummy:
                raise ValueError("Not enough dummy questions in QUESTION_BANK.")
            topic = random.choice(available_dummy)
            dummy_flags[topic] = True
            question_text = f"{topic} (Preview Only)"
        else:
            available_topics = [t for t in topics if not used_flags.get(t, False)]
            if not available_topics:
                raise ValueError("Not enough unique topics to generate all sets.")
            topic = random.choice(available_topics)
            used_flags[topic] = True
            question_text = generate_question_from_topic(topic, marks)

        sec_name = f"Q{len(sections_out)+1}"

        # Apply rules
        if "OR" in sec_name and mark_index+1 < len(marks_list):
            next_marks = marks_list[mark_index+1]
            combined_marks = marks + next_marks
            topic2 = random.choice([t for t in topics if not used_flags.get(t, False)])
            used_flags[topic2] = True
            question_text = f"{question_text} OR {generate_question_from_topic(topic2, next_marks)}"
            sections_out.append({
                "name": sec_name,
                "questions": [{"text": question_text, "marks": combined_marks, "options": []}]
            })
            mark_index += 2
            continue

        elif "MCQ" in sec_name:
            q_text, options = generate_mcq_from_topic(topic)
            sections_out.append({
                "name": sec_name,
                "questions": [{"text": q_text, "marks": marks, "options": options}]
            })

        elif "Combine" in sec_name and marks == 10:
            topic2 = random.choice([t for t in topics if not used_flags.get(t, False)])
            used_flags[topic2] = True
            question_text = f"Combined Question: {topic} + {topic2}"
            sections_out.append({
                "name": sec_name,
                "questions": [{"text": question_text, "marks": marks, "options": []}]
            })

        else:
            sections_out.append({
                "name": sec_name,
                "questions": [{"text": question_text, "marks": marks, "options": []}]
            })

        mark_index += 1

    template["sections"] = sections_out
    template["total_marks"] = sum(marks_list)
    return template





# ---------------- Marks Distribution ----------------
def generate_marks_list(setup):
    total_marks = setup['total_marks']
    marks_mode = setup['marks_mode']
    marks_list = []

    if marks_mode == "fixed":
        marks_per_question = int(setup.get('marks_per_question', 0))
        if marks_per_question <= 0:
            raise ValueError("Marks per question must be greater than 0.")

        # ✅ Calculate how many questions fit exactly
        if total_marks % marks_per_question != 0:
            raise ValueError(f"Total marks {total_marks} not divisible by {marks_per_question}. "
                             "Please adjust total marks or marks per question.")

        num_questions = total_marks // marks_per_question

        # ✅ Fill marks_list strictly with fixed marks
        marks_list = [marks_per_question] * num_questions

    elif marks_mode == "alternate":
        # Apply alternate pattern across questions
        pattern = [int(x.strip()) for x in setup['alternate_pattern'].split(",")]
        current_sum = 0
        index = 0

        while current_sum < total_marks:
            mark = pattern[index % len(pattern)]
            if current_sum + mark > total_marks:
                remaining = total_marks - current_sum
                if remaining > 0:
                    marks_list.append(remaining)
                break
            marks_list.append(mark)
            current_sum += mark
            index += 1

    return marks_list




#---------------------------------------------------------------
def generate_question_from_topic(topic, marks):
    if marks <= 2:
        return f"Define {topic}."
    elif marks <= 5:
        return f"Explain {topic}."
    elif marks <= 8:
        return f"Explain {topic} with suitable example."
    elif marks <= 10:
        return f"Describe {topic} in detail."
    else:
        return f"Explain {topic} with diagram."

#-----------------route-----------------------
@app.route('/select_template')
def select_template():
    setup = session.get('paper_setup')
    if not setup:
        return redirect(url_for('paper_setup'))

    try:
        marks_list = generate_marks_list(setup)
    except ValueError as e:
        return str(e)

    # ✅ read syllabus topics
    with open(setup['filepath'], 'r', encoding='utf-8', errors='ignore') as f:
        topics = [line.strip() for line in f if line.strip()]

    # ✅ initialize flags
    used_flags = {t: False for t in topics}
    dummy_flags = {q: False for q in QUESTION_BANK}   # <-- NEW for preview

    generated_templates = []
    session_templates = []

    # ✅ generate templates in dummy preview mode
    for i, t in enumerate(TEMPLATES, start=1):
        gen = generate_template(
            t,
            marks_list,
            topics,
            used_flags,
            dummy_mode=True,          # <-- PREVIEW MODE
            dummy_flags=dummy_flags   # <-- ensures no repetition in preview
        )
        generated_templates.append(gen)

        session_templates.append({
            "id": f"Template {i}",
            "name": gen.get("name", f"Template {i}")
        })

    session['available_templates'] = session_templates

    return render_template(
        'select_template.html',
        templates=generated_templates,
        paper=setup
    )



#------------Generate 6 question sets--------------

@app.route('/generate_sets')
def generate_sets():
    setup = session.get('paper_setup')
    if not setup:
        return redirect(url_for('paper_setup'))

    # ✅ generate marks list
    try:
        marks_list = generate_marks_list(setup)
    except ValueError as e:
        return str(e)

    # ✅ read syllabus topics
    with open(setup['filepath'], 'r', encoding='utf-8', errors='ignore') as f:
        topics = [line.strip() for line in f if line.strip()]

    # ✅ check topic sufficiency based on marks_list length
    questions_per_set = len(marks_list)
    required = setup['total_sets'] * questions_per_set
    if len(topics) < required:
        return f"Not enough unique topics to generate {setup['total_sets']} sets. " \
               f"Need {required}, but only {len(topics)} provided."

    # ✅ get selected templates
    selected_templates = session.get('selected_sets', [])
    if not selected_templates:
        return redirect(url_for('select_template'))

    import random
    random.shuffle(selected_templates)

    # ---------------- Distribution Rule ----------------
    n = len(selected_templates)
    if n == 1:
        sets_per_template = 6
    elif n == 2:
        sets_per_template = 3
    elif n == 3:
        sets_per_template = 2
    else:
        return "Please select minimum 1 and maximum 3 templates."

    def template_index(template_id):
        return int(template_id.split()[-1]) - 1

    question_sets = {}
    set_no = 1

    # ✅ initialize flags for all topics (to avoid redundancy across sets)
    used_flags = {t: False for t in topics}

    for template_id in selected_templates:
        idx = template_index(template_id)
        if idx < 0 or idx >= len(TEMPLATES):
            continue

        base_template = TEMPLATES[idx]

        for _ in range(sets_per_template):
            generated = generate_template(base_template, marks_list, topics, used_flags)
            question_sets[f"Set {set_no} ({template_id})"] = generated["sections"]
            set_no += 1

    session['question_sets'] = question_sets
    return redirect(url_for("preview_paper"))




#--------------finalize route-----------
@app.route('/finalize_sets', methods=['POST'])
def finalize_sets():
    selected_sets = request.form.getlist('selected_sets')

    # Validation: teacher must select 1–3 templates
    if len(selected_sets) < 1 or len(selected_sets) > 3:
        return "Please select minimum 1 and maximum 3 templates."

    # Store selected templates in session
    session['selected_sets'] = selected_sets

    # ✅ NOW go to generate 6 sets
    return redirect(url_for('generate_sets'))


#-----------temporary preview route------------
@app.route('/preview_paper')
def preview_paper():
    setup = session.get('paper_setup')
    question_sets = session.get('question_sets')

    if not setup or not question_sets:
        return redirect(url_for('paper_setup'))

    return render_template(
        'preview_paper.html',
        setup=setup,
        final_questions=question_sets
    )

#----------------------answer key-------
import re
from flask import request, session, redirect, url_for, render_template
from ai_answer_generator import generate_ai_answer


def parse_question(question_text):
    """
    Extracts marks from a question string and returns
    the cleaned question text along with marks.
    Example: "Explain AI (10 Marks)" → ("Explain AI", 10)
    """
    marks_match = re.search(r"\((\d+)\s*Marks\)", question_text)
    marks = int(marks_match.group(1)) if marks_match else 2

    clean_question = re.sub(r"\(\d+\s*Marks\)", "", question_text).strip()
    return clean_question, marks


@app.route('/generate_answer_key')
def generate_answer_key():
    """
    Generates an AI-based answer key for the selected question set.
    Stores the answers in session['answer_keys'] and redirects
    to the preview page for teacher review.
    """
    set_name = request.args.get('set_name')
    question_sets = session.get('question_sets')

    if not question_sets:
        return "Questions are not generated yet"

    # Initialize or reuse existing answer_keys
    answer_keys = session.get('answer_keys', {})

    # Generate answer key only for the selected set
    if set_name and set_name in question_sets:
        sections = question_sets[set_name]
        answers = []

        for sec in sections:
            for idx, q in enumerate(sec["questions"], start=1):
                question_text = q["text"]
                marks = q["marks"]

                answer = generate_ai_answer(
                    question_text,
                    marks,
                    session['paper_setup']['subject']
                )

                answers.append({
                    "q_no": f"Q{idx}",
                    "question": question_text,
                    "marks": marks,
                    "answer": answer
                })

        # Save only this set’s answers
        answer_keys[set_name] = answers
        session['answer_keys'] = answer_keys

    # Redirect to preview page for this set
    return redirect(url_for('answer_key_preview', set_name=set_name))


@app.route('/answer_key_preview', endpoint='answer_key_preview')
def show_answer_key():
    """
    Displays the preview of the generated answer key.
    Teachers can review answers and download the PDF.
    """
    answer_keys = session.get('answer_keys')
    if not answer_keys:
        return "Answer keys are not generated yet"

    selected_set = request.args.get('set_name')

    # If no set_name provided, default to the first available
    if not selected_set or selected_set not in answer_keys:
        selected_set = list(answer_keys.keys())[0]

    return render_template(
        'answer_key_preview.html',
        answer_keys=answer_keys,
        selected_set=selected_set
    )







#----------------profile---------------------
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        subject = request.form['subject']
        institution = request.form['institution']
        preferred_style = request.form['preferred_style']
        total_sets = request.form['total_sets']

        cursor.execute("""
            UPDATE users
            SET subject=%s,
                institution=%s,
                preferred_style=%s,
                total_sets=%s
            WHERE id=%s
        """, (
            subject,
            institution,
            preferred_style,
            total_sets,
            session['user_id']
        ))
        db.commit()

        return redirect(url_for('upload'))

    cursor.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()

    return render_template("profile.html", user=user)
# ---------------- MY QUESTIONS ----------------
@app.route('/my_questions')
def my_questions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor.execute(
        """
        SELECT filename, set_no, question
        FROM questions
        WHERE user_id = %s
        ORDER BY filename, set_no
        """,
        (session['user_id'],)
    )
    questions = cursor.fetchall()

    return render_template("my_questions.html", questions=questions)

#------------pdf code---------------------------------
from flask import make_response, redirect, url_for
from weasyprint import HTML

@app.route('/download_pdf/<set_name>')
def download_pdf(set_name):
    setup = session.get('paper_setup')
    question_sets = session.get('question_sets')

    if not setup or not question_sets:
        return redirect(url_for('paper_setup'))

    if set_name not in question_sets:
        return "Invalid question set"

    # ✅ get structured sections directly
    sections = question_sets[set_name]   # already a list of section dicts

    # ✅ render HTML
    html = render_template(
        'preview_paper.html',
        setup=setup,
        set_name=set_name,
        sections=sections,
        pdf_mode=True   # IMPORTANT for hiding buttons
    )

    # ✅ generate PDF
    pdf = HTML(string=html).write_pdf()

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={set_name}.pdf'

    return response
#-------ans pdf----------------------------------------------
@app.route('/download_answer_pdf/<set_name>')
def download_answer_pdf(set_name):

    answer_keys = session.get('answer_keys')

    if not answer_keys or set_name not in answer_keys:
        return "Answer key not found"

    # Render HTML
    html_content = render_template(
        'answer_key_pdf.html',
        answers=answer_keys[set_name]
    )

    # Convert HTML → PDF using WeasyPrint
    pdf_file = HTML(string=html_content).write_pdf()

    response = make_response(pdf_file)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = (
        f'attachment; filename={set_name}_Answer_Key.pdf'
    )

    return response




# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)