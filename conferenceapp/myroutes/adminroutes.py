'''This file is like the controller, it determines what the user sees, when they visit our app/routes'''
import math, random, os #imported at the top cos it's from python
from flask import make_response, render_template, request, abort, redirect, flash, session, url_for
from conferenceapp import app, db
from conferenceapp.mymodels import User, State, Skill, Breakout, Admin
from conferenceapp.forms import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash





@app.route('/admin/login', methods=['POST','GET'])
def adminlogin():
    return render_template('admin/login.html')

@app.route('/admin/submit/login', methods=['POST'])
def submit_adminlogin():
    username = request.form.get('username')
    pwd = request.form.get('pwd')

    if username == '' or pwd == '':
        flash('Please complete all fields')
        return redirect(url_for('adminlogin'))
    else:
        admindeets = Admin.query.filter(Admin.admin_username==username, Admin.admin_password==pwd).first()

        if admindeets:
            admin_id = admindeets.admin_id 
            session['admin_loggedin'] = admin_id

            flash('Login Successful')
            return redirect('/adminpage')
        else:
            flash('Invalid Credentials')   
            return redirect('/admin/login') 




@app.route('/adminpage')
def adminpage():
    return render_template('admin/index.html')

@app.route('/admin/upload', methods=['POST','GET'])
def admin_upload():
    if request.method == 'GET':
        return render_template('admin/test.html')
    else:
        file = request.files.get('image')
        original_name =file.filename
        #generate random string to be used as our filename
       
        fn = math.ceil(random.random() * 100000000)

         #method1:
        ext = original_name.split('.') #or then ext = ext[-1]

        #method2:
        ext = os.path.splitext(original_name)
        save_as = str(fn)+ext[1]

        allowed = ['.jpg', '.png', '.gif', '.svg', '.jpeg']

        if ext[1].lower() in allowed:
            file.save(f'conferenceapp/static/assets/img/{save_as}')
            return f'Submitted and saved as {save_as}'
        else:
            return 'File type not allowed' 


@app.route('/admin/breakout')
def admin_breakout():
    breakdeets = Breakout.query.all()
    return render_template('/admin/breakout.html', breakdeets=breakdeets)   

@app.route('/admin/addbreakout', methods=['GET','POST'])
def admin_addbreakout():
    if request.method =='GET':
        skills = Skill.query.all()
        return render_template('admin/addbreakout.html', skills=skills)
    else:
        #Retrieve form data (request.form....)
        title = request.form.get('title')
        level = request.form.get('level')
        amt = request.form.get('amt')
        #request file
        pic_object = request.files.get('img')
        original_file =  pic_object.filename
        if title =='' or level =='':
            flash("Title and Level cannot be empty")
            return('/admin/addbreakout')
        if original_file !='': #check if file is not empty
            extension = os.path.splitext(original_file)
            if extension[1].lower() in ['.jpg','.png']:
                fn = math.ceil(random.random() * 100000000)  
                save_as = str(fn)+extension[1] 
                pic_object.save(f"conferenceapp/static/assets/img/{save_as}")
                #insert other details into db
                b = Breakout(break_title=title,break_skillid=level,break_picture=save_as,break_amt=amt)
                db.session.add(b)
                db.session.commit()            
                return redirect("/admin/breakout")
            else:
                flash('File Not Allowed')
                return redirect("/admin/addbreakout")

        else:
            save_as =""
            b = Breakout(break_title=title,break_picture=save_as,break_skillid=level)
            db.session.add(b)
            db.session.commit() 
            return redirect("/admin/breakout")  


@app.route('/admin/breakout/delete/<breakid>')
def admin_deletebreakout(breakid):
    b = Breakout.query.get(breakid)
    db.session.delete(b)
    db.session.commit()
    flash(f'Breakout session {id} deleted')
    return redirect('/admin/breakout')

@app.route('/admin/logout')    
def admin_logout():
    session.pop('admin_loggedin')    
    return redirect('/admin/login')

@app.route('/admin/reg')
def registrations():
    #users = db.session.query(User,State,Skill).join(State).join(Skill).all()
    #users = User.query.join(State).join(Skill).add_columns(State,Skill).all()
    # users_skill1 = User.query.join(State).join(Skill).add_columns(State,Skill).filter(User.user_skillid==1).all()
    #users_skill1 = User.query.join(State).join(Skill).add_columns(State,Skill).filter(User.user_phone==None).all()
    users_skill1 = User.query.join(State,User.user_stateid==State.state_id).add_columns(State).all()

    return render_template('admin/allusers.html', users_skill1=users_skill1)



        
# @app.route('/admin/signup', methods=['POST','GET'])
# def admin_signup():
#     if request.method == 'GET':
#             return render_template('admin/signup.html')
#     else:
#         username = request.form.get('username')
#         pwd1 = request.form.get('pwd1')
#         pwd2 = request.form.get('pwd2')

#         if pwd1 == pwd2:
#             formatted = generate_password_hash(pwd1)
#             ad = Admin(admin_username=username, admin_password=formatted)
#             db.session.add(ad)
#             db.session.commit()
#             flash('New user signed up')
#             return redirect('/admin/login')
#         else:
#             flash('The two passwords do not match')
#             return redirect('/admin/signup')

# @app.route('/admin/submit/login', methods=['POST'])
# def submit_adminlogin():
#     username = request.form.get('username')
#     pwd = request.form.get('pwd')

#     if username == '' or pwd == '':
#         flash('Please complete all fields')
#         return redirect(url_for('adminlogin'))
#     else:
#         admindeets = Admin.query.filter(Admin.admin_username==username).first()
#         formated_pwd = admindeets.admin_password
#         chk = check_password_hash(formated_pwd,pwd)

#         if admindeets and chk:
#             admin_id = admindeets.admin_id 
#             session['admin_loggedin'] = admin_id

#             flash('Login Successful')
#             return redirect('/adminpage')
#         else:
#             flash('Invalid Credentials')   
#             return redirect('/admin/login') 
        

@app.route('/admin/signup', methods=['POST','GET'])
def admin_signup():
    if request.method == 'GET':
            return render_template('admin/signup.html')
            
    else:
        username = request.form.get('username')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')

        if pwd1 == pwd2:
            print('p')
            ad = Admin(admin_username=username, admin_password=pwd1)
            db.session.add(ad)
            db.session.commit()
            flash('New user signed up')
            return redirect('/admin/login')
        else:
            flash('The two passwords do not match')
            return redirect('/admin/signup')   
