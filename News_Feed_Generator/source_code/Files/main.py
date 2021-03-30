#!/usr/bin/env python
from .models import User, News
import time
import os
from Files.nb import NaiveBayes
from Files.rank_classifier import RankClassifier
from Files.knn import KNN
import random
from Files.document import Document
from Files.tfidf import Index
from Files.kmeans import KMeans
from Files.util import *
from collections import defaultdict, Counter
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from Files.scraping import getDailyNews
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from . import login_manager, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
option_count = 6
k_n = 5

news = Blueprint('news', __name__, template_folder='../templates')

# logout
@news.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return redirect('http://localhost:5000/')

# login Manager
@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

# login after submitting login details
@news.route("/login_post", methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        print("here")
        flash('Please check your login details and try again.')
        # if the user doesn't exist or password is wrong, reload the page
        return redirect('http://localhost:5000/')

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect('http://localhost:5000/main')

# login page
@news.route('/')
def login():
    return render_template('login.html')

# signup page
@news.route('/signup')
def signup():
    return render_template('signup.html')

# signup after submitting signup details
@news.route("/signup_post", methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    # if this returns a user, then the email already exists in database
    user = User.query.filter_by(email=email).first()

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return redirect('http://localhost:5000/signup')

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name,
                    password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()
    return redirect('http://localhost:5000/')


# recommend all mix news
@news.route("/recommend_top")
@login_required
def recommend():
    global user_docs, opt, ls
    ls = []
    test_docs = lst[1]
    user_docs = random.sample(test_docs, option_count)
    try:
        data = News.query.filter_by(
            user_id=current_user.id).order_by(News.id.desc()).first()
        fname = os.path.dirname(os.path.abspath(__file__))+"123.txt"

        files = open(fname, 'w')
        img = data.news_image
        ttl = data.news_title
        descp = data.news_text
        topic = data.news_topic
        art = str(img)+'\n'+str(ttl)+'\n'+str(descp)
        files.write(art)
        files.close()
        saved_docs = Document(fname, topic)
        saved_docs.vector = saved_docs.tf
        all_docs = lst[0]

        # pick random documents from test docs and provide titles to the user.

        classifier_list = lst[2]
        classifier_list = sorted(
            classifier_list, key=lambda cl: cl.stats['f_measure'], reverse=True)

        prediction_list = list()
        for classifier in classifier_list:
            prediction_list.append(classifier.classify([saved_docs])[0])

        prediction_count = Counter(prediction_list)
        top_prediction = prediction_count.most_common(1)

        if top_prediction[0][1] > 1:
            prediction = top_prediction[0][0]
        else:
            prediction = prediction_list[0]

        # print(all_docs[prediction])
        # create knn instance using documents of predicted topic. and find k closest documents.
        knn = KNN(all_docs[prediction])

        k_neighbours = knn.find_k_neighbours(saved_docs, k_n)
        ls = k_neighbours
    except:
        ls = []
    opt = "top"
    return redirect(url_for("news.onepage"))

# save liked news
@news.route("/like", methods=['POST', 'GET'])
def like():
    c = request.form
    choice = c['val']
    if choice == '11':
        user_choice = 0
        selected_doc = ls[user_choice]
    elif choice == '22':
        user_choice = 1
        selected_doc = ls[user_choice]
    elif choice == '33':
        user_choice = 2
        selected_doc = ls[user_choice]
    elif choice == '44':
        user_choice = 3
        selected_doc = ls[user_choice]
    elif choice == '55':
        user_choice = 4
        selected_doc = ls[user_choice]
    else:
        user_choice = int(choice)-1
        selected_doc = user_docs[user_choice]
    adding_news = News(news_image=selected_doc.img, news_title=selected_doc.title,
                       news_text=selected_doc.text, news_topic=selected_doc.topic, user_id=current_user.id)
    db.session.add(adding_news)
    db.session.commit()
    return redirect('http://localhost:5000/onepage')

# delete unliked news
@news.route("/unlike", methods=['POST', 'GET'])
def unlike():
    c = request.form
    choice = c['val']
    if choice == '11':
        user_choice = 0
        selected_doc = ls[user_choice]
    elif choice == '22':
        user_choice = 1
        selected_doc = ls[user_choice]
    elif choice == '33':
        user_choice = 2
        selected_doc = ls[user_choice]
    elif choice == '44':
        user_choice = 3
        selected_doc = ls[user_choice]
    elif choice == '55':
        user_choice = 4
        selected_doc = ls[user_choice]
    else:
        user_choice = int(choice)-1
        selected_doc = user_docs[user_choice]
    try:
        News.query.filter_by(news_text=selected_doc.text).delete()
        db.session.commit()
    except:
        None
    return redirect('http://localhost:5000/onepage')

# update with latest news calling scrapping function
@news.route("/update", methods=['POST', 'GET'])
@login_required
def update():
    getDailyNews()
    return redirect('http://localhost:5000/main')

# recommend business news
@news.route("/recommend_business")
@login_required
def recommend_business():
    global user_docs, opt
    user_docs = random.sample(lst[0]["business"], option_count)
    opt = "business"
    return redirect('http://localhost:5000/onepage')

# recommend entertainment news
@news.route("/recommend_entertainment")
@login_required
def recommend_entertainment():
    global user_docs, opt
    user_docs = random.sample(lst[0]["entertainment"], option_count)
    opt = "entertainment"
    return redirect('http://localhost:5000/onepage')

# recommend general news
@news.route("/recommend_general")
@login_required
def recommend_general():
    global user_docs, opt
    user_docs = random.sample(lst[0]["general"], option_count)
    opt = "general"
    return redirect('http://localhost:5000/onepage')

# recommend science news
@news.route("/recommend_science")
@login_required
def recommend_science():
    global user_docs, opt
    user_docs = random.sample(lst[0]["science"], option_count)
    opt = "science"
    return redirect('http://localhost:5000/onepage')

# recommend sports news
@news.route("/recommend_sports")
@login_required
def recommend_sports():
    global user_docs, opt
    user_docs = random.sample(lst[0]["sports"], option_count)
    opt = "sports"
    return redirect('http://localhost:5000/onepage')

# recommend technology news
@news.route("/recommend_technology")
@login_required
def recommend_technology():
    global user_docs, opt
    user_docs = random.sample(lst[0]["technology"], option_count)
    opt = "technology"
    return redirect('http://localhost:5000/onepage')

# display news
@news.route('/onepage', methods=['POST', 'GET'])
def onepage():
    user = user_docs
    recom = ls
    selection = opt
    return render_template('dashboard.html', user=user, selection=selection.capitalize(), name=current_user.name, recommend=recom)

# about
@news.route('/about')
@login_required
def about():
    return render_template('about.html', name=current_user.name)

# clear history
@news.route('/history_clear', methods=['POST'])
@login_required
def history_clear():
    News.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect('http://localhost:5000/history')

# show history
@news.route('/history')
@login_required
def history():
    data = News.query.filter_by(
        user_id=current_user.id).order_by(News.id.desc()).all()
    return render_template('history.html', data=data, name=current_user.name)

# display the news selected with recommendations on that
@news.route('/inside', methods=['POST', 'GET'])
@login_required
def inside():
    global ls, ms
    c = request.form
    choice = c['val']
    if choice == 'r':
        return redirect("http://localhost:5000/recommend_"+opt)
    else:
        if choice == '11':
            user_choice = 0
            selected_doc = ls[user_choice]
        elif choice == '22':
            user_choice = 1
            selected_doc = ls[user_choice]
        elif choice == '33':
            user_choice = 2
            selected_doc = ls[user_choice]
        elif choice == '44':
            user_choice = 3
            selected_doc = ls[user_choice]
        elif choice == '55':
            user_choice = 4
            selected_doc = ls[user_choice]
        else:
            user_choice = int(choice)-1
            selected_doc = user_docs[user_choice]

        ms = []
        # adding_news=News(news_image=selected_doc.img,news_title=selected_doc.title,news_text=selected_doc.text,news_topic=selected_doc.topic,user_id=current_user.id)
        # db.session.add(adding_news)
        # db.session.commit()
        all_docs = lst[0]
        classifier_list = lst[2]
        # classifiers are sorted according to their f_measure in decreasing order. It helps when all
        # three classifiers differ in their predictions.

        classifier_list = sorted(
            classifier_list, key=lambda cl: cl.stats['f_measure'], reverse=True)

        prediction_list = list()
        for classifier in classifier_list:
            prediction_list.append(classifier.classify([selected_doc])[0])

        prediction_count = Counter(prediction_list)
        top_prediction = prediction_count.most_common(1)

        if top_prediction[0][1] > 1:
            prediction = top_prediction[0][0]
        else:
            prediction = prediction_list[0]

        # create knn instance using documents of predicted topic. and find k closest documents.
        knn = KNN(all_docs[prediction])

        k_neighbours = knn.find_k_neighbours(selected_doc, k_n)
        ms.append(selected_doc)
        ms.append(k_neighbours)
        return render_template('scnd.html', ls=ms, name=current_user.name)

# running of algorithms and creating recommendations
@news.route("/main")
@login_required
def main():
    # getDailyNews()
    start_time = time.time()
    # Read documents, divide according to the topics and separate train and test data-set.
    t_path = os.path.dirname(os.path.abspath(__file__))+"/../../News_data/"
    all_docs = defaultdict(lambda: list())
    topic_list = list()
    for topic in os.listdir(t_path):
        d_path = t_path + topic + '/'
        if d_path == os.path.dirname(os.path.abspath(__file__))+"/../../News_data/._.DS_Store/":
            continue
        else:
            topic_list.append(topic)
            temp_docs = list()
            for f in os.listdir(d_path):
                f_path = d_path + f
                if f_path == os.path.dirname(os.path.abspath(__file__))+"/../../News_data/technology/.DS_Store":
                    continue
                else:
                    temp_docs.append(Document(f_path, topic))
        all_docs[topic] = temp_docs[:]
    fold_count = 10
    train_docs, test_docs = list(), list()
    for key, value in all_docs.items():
        random.shuffle(value)
        test_len = int(len(value)/fold_count)
        train_docs += value[:-test_len]
        # explanation
        #   lis = [1,2,3,4,5]
        # print(lis[:-4])
        # print(lis[-4:])
        test_docs += value[-test_len:]

    # Create tfidf and tfidfie index of training docs, and store into the docs.
    index = Index(train_docs)

    test_topics = [d.topic for d in test_docs]

    for doc in train_docs:
        doc.vector = doc.tfidfie

    for doc in test_docs:
        doc.vector = doc.tf

    # create classifier instances.
    nb = NaiveBayes()
    rc = RankClassifier()
    kmeans = KMeans(topic_list)

    classifier_list = [nb, rc, kmeans]

    for i in range(len(classifier_list)):

        classifier = classifier_list[i]

        classifier.confusion_matrix, c_dict = init_confusion_matrix(topic_list)

        classifier.train(train_docs)
        predictions = classifier.classify(test_docs)

        # Update the confusion matrix and statistics with updated values.
        classifier.confusion_matrix = update_confusion_matrix(test_topics, predictions, classifier.confusion_matrix,
                                                              c_dict)

        classifier.stats = cal_stats(classifier.confusion_matrix)

    global lst
    lst = []
    lst.append(all_docs)
    lst.append(test_docs)
    lst.append(classifier_list)
    return redirect('http://localhost:5000/recommend_top')
    # recommendation(all_docs, test_docs, classifier_list)
