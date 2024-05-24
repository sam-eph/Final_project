from flask import render_template, request, jsonify, Blueprint, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from textToESL.models import Dictionary, TranslationHistory, User
from textToESL.main.forms import DeleteForm, NewWord
from textToESL import db
from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip, CompositeVideoClip
import secrets
import os
import json
from sqlalchemy.sql import or_

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
def home():
    return render_template('home.html')

@main.route("/about")
def about():
    return render_template('about.html', title='About')


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


@main.route('/translator')
def translator():
    return render_template('translator.html', title='Translator')

@main.route('/translate', methods=['POST'])
def translate():
    data = request.json
    text = data.get('text')
    try:
        video_urls = text_to_sign_language(text)
        
        # Save translation history
        if current_user.is_authenticated:
            save_translation_history(current_user.id, text, video_urls)
        
        return jsonify({'video_urls': video_urls})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

def text_to_sign_language(text):
    words = text.split()
    word_entries = Dictionary.query.filter(or_(*[Dictionary.word == word for word in words])).all()
    word_to_video = {entry.word: url_for('static', filename='dict/' + entry.sign_video) for entry in word_entries}

    video_urls = []
    for word in words:
        video_url = word_to_video.get(word)
        if video_url:
            video_urls.append(video_url)
        else:
            print(f"Warning: Word '{word}' not found in database")

    if not video_urls:
        raise ValueError("No valid videos found. Please check your dictionary and input text.")

    return video_urls

def save_translation_history(user_id, text, video_urls):
    history_entry = TranslationHistory(user_id=user_id, translated_text=text, video_urls=json.dumps(video_urls))
    db.session.add(history_entry)
    db.session.commit()

@main.route('/history')
@login_required
def history():
    user_history = TranslationHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('translation_history.html', title='Translation History', history=user_history)

# def sign_language_to_text(image_data):
#     image_data = image_data.split(",")[1]  # Remove the data URL prefix
#     image_bytes = base64.b64decode(image_data)
#     image = Image.open(io.BytesIO(image_bytes))

#     # Placeholder for actual sign language recognition logic
#     # Replace this with the actual logic to process the image and return the translated text
#     translated_text = "Recognized Sign Text"

#     return translated_text