from flask import Flask, render_template, flash, request, jsonify
from wtforms import Form, TextField, validators
from fastai.basic_train import load_learner
import praw
import re
import os

app = Flask(__name__)
DEBUG = False
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
port = int(os.environ.get("PORT", 5000))

reddit = praw.Reddit(client_id = "CE_CHBOiktT0mw",
					client_secret = "1_hli9su-rwvR2dv2_0jxuJNLqA",
					user_agent = "reddit_scraper",
					username = "yashagarwal23",
					password = "Hisar*123")

classifier = load_learner(".", 'reddit_flair_classifier')

def clean_text(text):
    text = text.lower()
    text = re.sub(r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?", "", text)
    text = re.sub(r"\d+", "", text).strip()
    return text

def predict(url):
    submission = reddit.submission(url = url)
    text = re.sub("\s\s+" , " ", submission.title + ". " + submission.selftext)
    text = clean_text(text)
    return str(classifier.predict(text)[0])


class ReusableForm(Form):
    name = TextField('Name:', validators=[validators.required()])

    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form)
        print(form.errors)
        if request.method == 'POST':
            url=request.form['name']
            prediction = predict(url)
            if form.validate():
            # Save the comment here.
                flash("Predicted Flair : " + prediction)
            else:
                flash('Error: URL required. ')
        return render_template('index.html', form=form)

@app.route('/automated_testing', methods=['POST', 'GET'])
def automated_testing():
    if request.method == 'GET':
        return "automated testing. post a text file under 'file' field with a reddit post url in each line for flair prediction"
    if 'file' not in request.files:
        return "send the file under 'file' field\n"
    file = request.files['file']
    urls = file.readlines()
    prediction = {url.decode("utf-8")[:-1]:predict(url.decode("utf-8")) for url in urls}
    return jsonify(prediction)

if __name__ == "__main__":
    app.run(debug=DEBUG, host='0.0.0.0', port=port)
