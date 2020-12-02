import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
#from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [element.format() for element in selection]
  current_questions = questions[start:end]
  return current_questions




def create_app(test_config=None):
  # create and configure the app

  app = Flask(__name__)
  setup_db(app)
  
  '''
  Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  
  @app.after_request
  def after_request(response):
   response.headers.add("Access-Control-Allow", "*")
   response.headers.add("Access-Control-Allow-Credentials" , "true")
   return response
  '''
 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def all_categories():
   category_all = Category.query.all()
   category_all = Category.query.order_by(Category.type).all()

   categories = [category.format() for category in category_all]

   if len(categories) == 0:
      abort(404)

  #Change the format to dictionary to pass Json format
   formatted_categories = {k:v for category in categories for k,v in category.items()}
   return jsonify({
          'success': True,
          'categories': formatted_categories         
   })

  '''
 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    questions = Question.query.all()
    formatted_questions = pagination(request, questions)
    category_all = Category.query.all()
    categories = [category.format() for category in category_all]

    if len(formatted_questions) == 0:
      abort(404)

    formatted_categories = {k:v for category in categories for k,v in category.items()}
    return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(questions),
          'category': "",
          'categories': formatted_categories
    })
  '''
  
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.filter(Question.id == id).one_or_none()
    if question is None:
      abort(404)
    
    try:
      Question.query.filter(Question.id == id).delete()
      questions = Question.query.all()
     
      formatted_questions = pagination(request, questions)
      if len(formatted_questions) == 0:
        abort(404)
      
      category_all = Category.query.all()
      categories = [category.format() for category in category_all]

      if len(categories) == 0:
        abort(404)
       
      formatted_categories = {k:v for category in categories for k,v in category.items()}
      
      db.session.commit()

      return jsonify({
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(questions),
        'categories': formatted_categories
      })
    except:
     abort(404)  
     db.session.rollback()
  '''

  
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def new_question():
    try:
      #get the new question data from json
      question = Question(
                  question = request.get_json()['question'],
                  answer = request.get_json()['answer'],
                  category = request.get_json()['category'],
                  difficulty = request.get_json()['difficulty']
                  )
      question.insert()
      
      db.session.commit()

      return jsonify({
        'success': True,
      })
    except:
      abort(422)
      db.session.rollback()

  '''
   
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    #get Search term from Json, and then search based on the search term
    #Return data to the format to json
    searchTerm = request.get_json()['searchTerm']
    data_searched=Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
    formatted_questions = pagination(request, data_searched)   
    category_all = Category.query.all()
    categories = [category.format() for category in category_all]
    formatted_categories = {k:v for category in categories for k,v in category.items()} 
    return jsonify({
      'success': True,
      'questions': formatted_questions,
      'total_questions_found': len(data_searched),
      'current_category': "",
      'categories': formatted_categories
    }) 

  '''
   
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''

  @app.route('/categories/<int:category_id>/questions')
  def get_category_question(category_id):
    questions_per_category = Question.query.filter(Question.category == category_id).all()
    if len(questions_per_category) == 0:
      abort(404)

    formatted_questions = pagination(request, questions_per_category)

    category_all = Category.query.all()
    categories = [category.format() for category in category_all]
    formatted_categories = {k:v for category in categories for k,v in category.items()} 

    print(category_id, questions_per_category, formatted_questions, len(questions_per_category))

    try:

      return jsonify({
          'success': True,
          'questions': formatted_questions,
          'total_questions': len(questions_per_category),
          'category': category_id,
          'categories': formatted_categories
      })
    except:
      abort(404)


  '''
  
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def quiz():
    response_quiz = request.get_json()
    previous_questions = response_quiz['previous_questions']
    category_id = response_quiz["quiz_category"]["id"]
    if category_id == 0:
      if previous_questions is None:
        questions = Question.query.all()        
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
        
    else:
      if previous_questions is None:
        questions = Question.query.filter(Question.category == category_id).all()
      else:
        questions = Question.query.filter(Question.id.notin_(previous_questions),
        Question.category == category_id).all()

    #add a check to avoid getting an error with the random.choice function.
    if len(questions) == 0:
        return jsonify({'question': None})

    next_question = random.choice(questions).format()
    print(next_question)
    if next_question is None:
      next_question = False

    return jsonify({
      'success': True,
      'question': next_question
    })

  '''
  
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(422)
  def unprocessable(error):
   return jsonify({
          "success": False,
          "error": 422,
          "message": "Unprocessable"
    }), 422  
      
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
          "success": False,
          "error": 404,
          "message": "Not found"
    }), 404
 

  return app

    