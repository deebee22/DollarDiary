from expense import app, db
from expense.models import Expenses, User, Budgets
from flask import render_template, redirect, url_for, flash, abort, request
from .forms import SignInForm, SignUpForm, ExpenseForm
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses():
    form = ExpenseForm()
    if form.validate_on_submit():
        amount = form.amount.data
        description = form.description.data
        category = form.category.data
        date = form.date.data
        expense = Expenses(amount=amount, description=description, category=category, date=date, owner=current_user.id)
        db.session.add(expense)
        db.session.commit()
        flash('Your expense has been logged successfully.', 'success')
        return redirect(url_for('my_expenses'))
    expense = Expenses.query.filter_by(owner=current_user.id).all()
    return render_template('expenses.html', form=form, expense=expense)

@app.route('/my_expenses', methods=['GET', 'POST'])
@login_required
def my_expenses():
    expenses = Expenses.query.filter_by(owner=current_user.id).order_by(Expenses.date.desc()).all()
    return render_template('display_expenses.html', expenses=expenses)

@app.route('/expenses/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_expense(id):
    expense = Expenses.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(expense)
        db.session.commit()
        flash('Your expense has been deleted successfully.', 'success')
        return redirect(url_for('expenses'))
    '''return render_template('delete_expense.html', expense=expense)'''

@app.route('/confirm_delete/<int:id>')
def confirm_delete(id):
    expense = Expenses.query.get_or_404(id)
    return render_template('delete_expense.html', expense=expense)

@app.route('/expenses/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_expense(id):
    expense = Expenses.query.get_or_404(id)
    form = ExpenseForm(obj=expense)
    if request.method == 'POST' and form.validate_on_submit():
        expense.amount = form.amount.data
        expense.description = form.description.data
        expense.category = form.category.data
        expense.date = form.date.data
        db.session.commit()
        flash('Your expense has been updated successfully.', 'success')
        return redirect(url_for('my_expenses'))
    return render_template('update_expense.html', form=form, expense=expense)


@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    if request.method == 'POST':
        amount = float(request.form['amount'])
        time = request.form['length']
        date = datetime.now()
       
        budget = Budgets(amount=amount, time=time, date=date, user_id=current_user.id)
        db.session.add(budget)
        db.session.commit()

        flash('Your budget has been set!', 'success')

    return render_template('budget.html')

def time_calc(period):
    user_budget = Budgets.query.filter_by(user_id=current_user.id).order_by(Budgets.id.desc()).first()
    start = user_budget.date
    
    if period == 'day':
        end_date = start + timedelta(days=1) 
    elif period == 'week':
        end_date = start + timedelta(days=7)
    elif period == 'month':
        next_month = start.replace(day=28) + timedelta(days=4) 
        end_date = next_month - timedelta(days=next_month.day)

    return end_date

@app.route('/reports')
@login_required
def reports():

    user_budget = Budgets.query.filter_by(user_id=current_user.id).order_by(Budgets.id.desc()).first() 
    date = user_budget.date #error here if user does not have a budget already set
    clean = date.strftime("%m-%d-%Y")
    
    if user_budget:
        date = user_budget.date
        clean = date.strftime("%m-%d-%Y")
        new = date.replace(hour=0, minute=0, second=0, microsecond=0) #adjusting budget date timeframe to include expenses logged the same day that budget is set
        end = time_calc(user_budget.time)
        clean2 = end.strftime("%m-%d-%Y")
      

        expenses = Expenses.query.filter(Expenses.owner == current_user.id,
                                         Expenses.date >= new, Expenses.date <= end).all()
        
        if expenses:
          
            spending = {}
            for expense in expenses:
                if expense.category in spending:
                    spending[expense.category] += expense.amount
                else:
                    spending[expense.category] = expense.amount

            max_spending= max(spending, key=spending.get)
            max_amount = spending[max_spending]
            
            total = sum(expense.amount for expense in expenses)
            
            
            remainder = user_budget.amount - total
            if remainder >= 0:
                status = 'within'
                left = remainder
                over = None
            else:
                status = 'exceed'
                over = abs(remainder)
                left = None

            return render_template('reports.html', user_budget=user_budget, clean=clean, clean2=clean2, max_spending=max_spending, max_amount=max_amount,total=total, status=status, left=left, over=over)
        else:
            flash('There were no expenses found for the specified time frame.', 'warning')
    else:
        flash('Set a budget using the Budget tab in order to view reports!', 'warning')

    return render_template('reports.html', user_budget=user_budget, clean=clean, clean2=clean2)
    

@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    form = SignUpForm()
    if form.validate_on_submit(): #only run when set validations are met
            create_user = User( username=form.username.data,
                           email_address=form.email_address.data,
                           password=form.password1.data)
            db.session.add(create_user)
            db.session.commit()
            login_user(create_user)
            flash(f'Account created successfully. You are now logged in as {create_user.username}', category='success')
            return redirect(url_for('budget'))
    if form.errors != {}: #if errors are present from validations
        for error_msg in form.errors.values():
            flash(f'There was an error with creating a user: {'\n'.join(error_msg)}', category='danger')
    
    return render_template('signup.html', form=form)

@app.route('/signin', methods=['GET', 'POST'])
def signin_page():
    form = SignInForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password(
            attempted_password=form.password.data
         ):
            login_user(attempted_user)
            flash(f'You are signed in, {attempted_user.username}', category='success')
            return redirect(url_for('expenses'))
        
        else:
            flash('Incorrect username and/or password. Please try again.', category='danger')

    return render_template('signin.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You are logged out", category= "info")
    return redirect(url_for('home'))
