from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, current_app
from flask_login import current_user, login_required
from textToESL import db
from textToESL.models import User, Messages, Dictionary
from textToESL.admin.forms import NewWord, DeleteCustomerForm, DeleteMessageForm
import os
import secrets


admin = Blueprint('admin', __name__)

@admin.route("/admin")
@login_required
def admin_home():
    if not current_user.is_admin:  
        abort(403)
        
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    total_customers = User.query.count()  # Count total customers
    total_emails = Messages.query.count()    # Count total emails
    total_words = Dictionary.query.count()    # Count total words

    latest_messages = Messages.query.order_by(Messages.timestamp.desc()).limit(3).all()
    
    return render_template('admin.html', image_file=image_file, title='Admin',
                           total_customers=total_customers, total_emails=total_emails, 
                           total_words=total_words, latest_messages=latest_messages)


@admin.route('/admin/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if not current_user.is_admin:
        abort(403)
    
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    total_emails = Messages.query.count()
    form = DeleteCustomerForm() 
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '', type=str)
    
    if search_query:
        customers = User.query.filter(
            User.username.ilike(f'%{search_query}%') | 
            User.email.ilike(f'%{search_query}%')
        ).paginate(page=page, per_page=5)
    else:
        customers = User.query.paginate(page=page, per_page=5)
    
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        role = request.form.get('role')
        user = User.query.get(user_id)
        
        if user:
            if user.username == 'admin':
                flash('You cannot change the role of the super admin.', 'danger')
            else:
                if role == 'admin':
                    user.is_admin = True
                else:
                    user.is_admin = False
                db.session.commit()
                flash('User role updated successfully', 'success')
        return redirect(url_for('admin.customers', page=page, search=search_query))
    
    return render_template('customers.html', title='Customers', customers=customers, 
                           form=form, image_file=image_file, total_emails=total_emails, search_query=search_query)


@admin.route('/admin/customer/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    if not current_user.is_admin:
        abort(403)
    
    customer = User.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer has been deleted!', 'success')
    return redirect(url_for('admin.customers'))

@admin.route('/admin/mailbox')
@login_required
def mailbox():
    if not current_user.is_admin:
        abort(403)
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    total_emails = Messages.query.count()
    form = DeleteMessageForm()  
    page = request.args.get('page', 1, type=int) 
    messages = Messages.query.paginate(page=page, per_page=5)
    return render_template('mailbox.html', title='Mailbox', messages=messages, 
                           form=form, image_file=image_file, total_emails=total_emails)

@admin.route('/admin/message/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    if not current_user.is_admin:
        abort(403)

    message = Messages.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    flash('Message has been deleted!', 'success')
    return redirect(url_for('admin.mailbox'))

@admin.route('/admin/new', methods=['GET', 'POST'])
def add_word():
    if not current_user.is_admin:
        abort(403)
    form = NewWord()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    total_emails = Messages.query.count()
    if form.validate_on_submit():
        if form.sign_video.data:
            video_file = save_video(form.sign_video.data)
        new_word = Dictionary(word=form.word.data, sign_video=video_file)
        db.session.add(new_word)
        db.session.commit()
        flash('The word has been Added!', 'success')
        return redirect(url_for('admin.add_word'))
    return render_template('add_new_word.html', title='New_word' ,
                           form=form, image_file=image_file, total_emails=total_emails)


def save_video(form_video):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_video.filename)
    video_fn = random_hex + f_ext
    video_path = os.path.join(current_app.root_path, 'static/dict', video_fn)
    form_video.save(video_path)
    return video_fn




    