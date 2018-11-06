###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required, Length # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell # New
import requests
import json

# Configuring  base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

## App setup code
app = Flask(__name__)
app.debug = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
app.config["SQLALCHEMY_DATABASE_URI"] =  "postgres://postgres:snubbalo@localhost/midterm"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False



## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)


######################################
######## HELPER FXNS (If any) ########
######################################



##################
##### MODELS #####
##################

class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer,primary_key=True)
    uniquename = db.Column(db.String(64))
    name = db.Column(db.String(64))
    questions = db.relationship('Question', backref = 'stud_questions')
    #def __repr__(self):
     #   return "{} (ID: {})".format(self.name, self.id)

class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(500))
    student_id = db.Column(db.Integer, db.ForeignKey('students.id')) #one to many relationship with students on uniquename 
    answers = db.relationship('Answer', backref = 'questions')



class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.String(500))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id')) 
    
###################
###### FORMS ######
###################

class QuestionForm(FlaskForm):
    uniquename = StringField("Please enter your unique name",validators=[Required(), Length(1,64)])
    text = StringField("Please enter your question.",validators=[Required(), Length(1,500)])
    submit = SubmitField()

class StudentRegistration(FlaskForm):
    uniquename = StringField("Please enter your unique name.",validators=[Required(),  Length(1,64)])
    name = StringField("Please enter your first and last name",validators=[Required()])
    submit = SubmitField()

class AnswerForm(FlaskForm):
    question_id = StringField("Please enter the question ID",validators=[Required()])
    answer = StringField("Please enter the text to your answer",validators=[Required()])
    submit = SubmitField()

class DictForm(FlaskForm):
    word = StringField("Please enter a word you'd like to know the definition to",validators=[Required()])
    submit = SubmitField()

## Error handling routes - PROVIDED
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


#######################
###### VIEW FXNS ######
#######################
@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize the form
    form = QuestionForm()
    # Get the number of Tweets
    all_questions = Question.query.all()
    num_questions = len(all_questions)
    # If the form was posted to this route,
    ## Get the data from the form
    if form.validate_on_submit(): 
        text = form.text.data
        uniquename = form.uniquename.data
    ## Find out if there's already a student with the entered uniquename
        s = Student.query.filter_by(uniquename = uniquename).first()
        if s: 
            flash("Student exists", s.uniquename)
    #if there's not a student registered with the uniquename, add them to the database
        else: 
            print("Student is not registered")
            return redirect(url_for('student_registration'))

        quest = Question.query.filter_by(text = text, student_id = s.id).first()
        if quest: 
            print("question already exists")
            return redirect(url_for('see_all_questions'))
        else: 
            q = Question(text=text, student_id = s.id)
            db.session.add(q)
            db.session.commit()
            return redirect(url_for('index'))

    # If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('index.html', form = form, num_questions = num_questions) # TODO 364: Add more arguments to the render_template invocation to send data to index.html

@app.route('/answer_question', methods=['GET', 'POST'])
def answer_question():
    # Initialize the form
    form = AnswerForm()
    # Get the number of Tweets
    all_answers = Answer.query.all()
    num_answers = len(all_answers)
    if form.validate_on_submit(): 
        question_id = form.question_id.data
        answer = form.answer.data
        #if answer exists
        a = Answer.query.filter_by(text = answer).first()
        if a: 
            print("answer already exists", a.text)
            return redirect(url_for('answer_question'))
        else: 
            ans = Answer(text=answer, question_id=question_id)
            db.session.add(ans)
            db.session.commit()
            return redirect(url_for('answer_question'))

    # If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('answer_question.html', form = form, num_answers = num_answers) 

@app.route('/student_registration', methods=['GET', 'POST'])
def student_registration():
    # Initialize the form
    form = StudentRegistration()
    # Get the number of Tweets
    all_students = Student.query.all()
    num_students= len(all_students)
    # If the form was posted to this route,
    ## Get the data from the form
    if form.validate_on_submit(): 
        uniquename = form.uniquename.data
        name = form.name.data
    ## Find out if there's already a student with the entered uniquename
    ## If there is, save it in a variable: student

        s = Student.query.filter_by(uniquename = uniquename).first()
        if s: 
            print("User exists", s.uniquename)

    #if there's not a student registered with the uniquename, register the student in the database
        else: 
            print("Student is not yet registered")
            stu = Student(name = name, uniquename = uniquename)
            db.session.add(stu)
            db.session.commit()
            return redirect(url_for('index'))
    # If the form did NOT validate / was not submitted
    errors = [v for v in form.errors.values()]
    if len(errors) > 0:
        flash("!!!! ERRORS IN FORM SUBMISSION - " + str(errors))
    return render_template('student_registration.html', form = form, num_students=num_students) # TODO 364: Add more arguments to the render_template invocation to send data to index.html


@app.route('/all_questions')
def see_all_questions():   
    all_questions = []
    qs = Question.query.all()
    print(qs)
    for x in qs: 
        print(x)
        s = Student.query.filter_by(id = x.student_id).first()
        tup = (x.text, s.uniquename)
        all_questions.append(tup)
    return render_template('all_questions.html', all_questions = all_questions)

@app.route('/all_answers')
def see_all_answers():   
    q_a = []
    qs = Question.query.all()
    for q in qs: 
        ansaws = Answer.query.filter_by(question_id = q.id).all()
        s = Student.query.filter_by(id = q.student_id).first()
        answer_list = []
        for a in ansaws: 
            answer_list.append(a.text)
        qid = q.id
        qtext = q.text
        qunique = s.uniquename
        atup = (qid, qtext, qunique, answer_list)
        q_a.append(atup)
        #q_a.append(qid, qtext, qunique)
    return render_template('all_answers.html', all_answers = q_a)

@app.route('/dictform')
def dictform(): 
    form = DictForm()
    #if form.validate_on_submit(): 
     #   return redirect(url_for('/dictresults'))
    return render_template('dict_form.html', form = form)

@app.route('/dict_results', methods=['GET', 'POST'])
def dictresults(): 
    form = DictForm()
    if form.validate_on_submit(): 
        word = form.word.data
    if request.method == 'GET':
        word = request.args.get('word')
        language = 'en'
        word_id = word
        baseurl =   'https://od-api.oxforddictionaries.com/api/v1/search/' + language + '?q=' + word_id.lower() + '&prefix=false'
        app_id = '6327d7d6'
        app_key = '5f3dca3b78b4020fa6b7d7a701f3df50'

        params_dict = {} 
        params_dict["app_id"] = app_id
        params_dict["app_key"] = app_key
        params_dict["word_id"] = word
        resp = requests.get(baseurl, headers = params_dict)
        text = resp.text
        data = json.loads(text)
        x = data['results']

        return render_template('dict_results.html', dicty=x)
    return redirect(url_for('/dictform'))
## Code to run the application...

if __name__ == '__main__':
    db.create_all() # Will create any defined models when you run the application
    #app.run(use_reloader=True,debug=True) # The usual
    #manager.run()
    app.run(debug = True)
