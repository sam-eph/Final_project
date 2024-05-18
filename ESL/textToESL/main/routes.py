from flask import render_template, request, Blueprint, flash, redirect, url_for
from flask import Blueprint, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required
from textToESL.models import Dictionary
from textToESL.main.forms import DeleteForm
from textToESL.main.forms import NewWord
from flask_login import current_user
import secrets
from textToESL import db
import os

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')


@main.route("/about")
def about():
    return render_template('about.html', title='About')

@main.route("/translator")
def translator():
    return render_template('translator.html', title='Translator')

@main.route('/dictionary/new', methods=['GET', 'POST'])
def add_word():
    form = NewWord()
    if form.validate_on_submit():
        if form.sign_video.data:
            video_file = save_video(form.sign_video.data)
        new_word = Dictionary(word=form.word.data, sign_video=video_file)
        db.session.add(new_word)
        db.session.commit()
        flash('The word has been Added!', 'success')
        return redirect(url_for('main.dictionary'))
    return render_template('add_new_word.html', title='New_word', form=form)

@main.route("/dictionary/<int:word_id>")
def sign(word_id):
    words = Dictionary.query.get_or_404(word_id)
    video_file = url_for('static', filename='dict/' + words.sign_video)
    return render_template('sign.html', title=words.word, video_file=video_file)

@main.route('/dictionary')
def dictionary():
    words = Dictionary.query.all()
    form = DeleteForm()
    return render_template('dictionary.html', words=words, form=form)

@main.route('/delete/<int:word_id>', methods=['GET', 'POST'])
def delete_word(word_id):
    word = Dictionary.query.get_or_404(word_id)
    form = DeleteForm()
    if form.validate_on_submit():
        db.session.delete(word)
        db.session.commit()
        flash('Word deleted successfully', 'success')
        return redirect(url_for('main.dictionary'))
    return render_template('delete.html', word=word, form=form)

def save_video(form_video):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_video.filename)
    video_fn = random_hex + f_ext
    video_path = os.path.join(current_app.root_path, 'static/dict', video_fn)

    form_video.save(video_path)

    return video_fn