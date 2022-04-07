'''This file is like the controller, it determines what the user sees, when they visit our app/routes'''
from ast import Break
import email, json, requests, random
from email.mime import application
from urllib import response
from xml.etree.ElementTree import Comment
from flask import make_response, render_template, request, abort, redirect, flash, session
from sqlalchemy import desc
from conferenceapp import app, db, Message, mail
from conferenceapp.mymodels import User, State, Skill, Breakout, user_sessions, Contactus, Posts, Comments, Myorder, OrderDetails, Payment
from conferenceapp.forms import LoginForm, ContactForm

@app.route('/',  methods=['POST','GET'])
def home():
    login = LoginForm()
    id = session.get('loggedin')
    userdeets = User.query.get(id)
    b = Breakout.query.all()
    contactus = ContactForm()

    #connect to api without authentication
    #response = requests.get('http://127.0.0.1:8082/api/v1.0/listall')

    #connect if api has authentication
    

    try:
        response = requests.get('http://127.0.0.1:8082/api/v1.0/listall', auth=('admin', '1234'))
        #retrieve the json in the request
        hostel_json = response.json() #json.loads(response.text)
        hostel_json = json.dumps(response)
        status = hostel_json.get('status') #to pick status
    except:
        hostel_json={}

    #pass it to the template as hostel_json=hostel_json

    return render_template('user/index.html', login=login, userdeets=userdeets, b=b, contactus=contactus, hostel_json=hostel_json)

@app.route('/send/message', methods=['POST'])
def send_msg():
    contactus = ContactForm()
    return render_template('user/layout.html', contactus=contactus)


@app.route('/submit/message', methods=['POST','GET'])
def sub_msg():
    contactus = ContactForm()
    # fullname = contactus.fullname.data
    # email = contactus.email.data
    # msg = contactus.message.data

    fullname = request.values.get('fullname')
    email = request.args.get('email')
    msg = request.values.get('message')
    
    #if contactus.validate_on_submit():
    c = Contactus(contact_fullname=fullname, contact_email=email, contact_msg=msg)
    db.session.add(c)
    db.session.commit()
    cid = c.contact_id

    if cid:
        return json.dumps({'id':cid, 'msg':'Message Sent'})
    else:
        return 'Message sent successfully'


@app.route('/user/login', methods=['POST']) 
def submit_login():
    contactus = ContactForm()
    login = LoginForm()
    '''We retrieve the form data'''
    username = request.form.get('username') #method1
    pwd = login.pwd.data #method 2
    #validate
    if login.validate_on_submit():
        #deets = User.query.filter(User.user_email==username).filter(User.user_pass==pwd).all()    OR
        deets = User.query.filter(User.user_email==username, User.user_pass==pwd).first()
        if deets:
            #retrieve user's id and then keep in session , we still use the same loggedin session we use below both are trying to log the user in
            id = deets.user_id
            session['loggedin']=id
            return redirect('/userhome')
        else:
            flash('Username or password incorrect')
            return redirect('/')
    else:
        return render_template('user/index.html', login=login, contactus=contactus)


@app.route('/register', methods=['POST','GET'])
def register():
    contactus = ContactForm()
    if request.method == 'GET':
        skills = db.session.query(Skill).all()
        states = db.session.query(State).all()
        return render_template('/user/register.html', skills=skills, states=states, contactus=contactus)
    else:
        #retrieve form data
        email = request.form.get('email')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        state = request.form.get('state')
        skill = request.form.get('skill')
        
        if email == '' or pwd1 == '' or fname == '' or lname == '' or state == '' or skill == '':
            flash('Please complete all fields')
            return redirect('/register')
        elif pwd1 != pwd2:
            flash('Please ensure the two passwords are the same')
            return redirect('/register')
        else:
            u = User(user_email=email,
                    user_pass=pwd1, 
                    user_fname=fname, 
                    user_lname=lname, 
                    user_stateid=state, 
                    user_skillid=skill)

            db.session.add(u)
            db.session.commit()
            id = u.user_id
            session['loggedin'] = id
            return redirect('/userhome')

@app.route('/userhome')
def userhome():
    contactus = ContactForm()
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect('/')
    else:
        userdeets = db.session.query(User).get(loggedin)
        return render_template('user/userhome.html', userdeets=userdeets, contactus=contactus)

@app.route('/logout')
def logout():
    session.pop('loggedin')
    return redirect('/')

@app.route('/breakout')
def user_breakout():
    contactus = ContactForm()
    id = session.get('loggedin')
    if id == None:
        return redirect('/')
    else:
        u = User.query.get(id)
        userskill = u.user_skillid
        breakouts = db.session.query(Breakout).filter(Breakout.break_skillid==userskill).all()
        return render_template('user/breakout.html', u=u, breakouts=breakouts, contactus=contactus)

#@app.route('/user/breakout/details/')

@app.route('/user/regbreakout', methods=['POST','GET'])
def reg_breakout():
    contactus = ContactForm()
    '''getlist() to retrieve multiple form elements with the same name'''
    bid = request.form.getlist('bid')
    loggedin = session.get('loggedin')
    user = User.query.get(loggedin)

    db.session.execute(f'DELETE FROM user_breakout WHERE user_id="{loggedin}"')
    db.session.commit()
    
    # for i in bid:
    #     user_break = user_sessions.insert().values(user_id=loggedin, breakout_id=i)
    #     db.session.execute(user_break)
    #     db.session.commit()
    #     return 'done'

    for i in bid:
        item = Breakout.query.get(i)
        user.mybreakouts.append(item)
        db.session.commit()

    return redirect('/breakout')

@app.route('/user/editprofile', methods=['POST','GET'])
def useredit_prof():
    contactus = ContactForm()
    loggedin = session.get('loggedin')
    useredits = User.query.get(loggedin)
    all_levels = Skill.query.all()
    all_states = State.query.all()
    return render_template('user/profile.html', useredits=useredits, all_levels=all_levels, all_states=all_states, contactus=contactus)

@app.route('/user/update/<id>', methods=['POST'])
def user_update(id):
    loggedin = session.get('loggedin')
    
    if loggedin == None:
        return redirect('/')
    else:
        #retrieve from data    
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        phone = request.form.get('phone')
        address = request.form.get('address')
        skill = request.form.get('skill')
        state = request.form.get('state')

        #get this instance of the user
        if int(loggedin) == int(id): 
            u = User.query.get(id)

            u.user_fname=fname
            u.user_lname=lname
            u.user_phone=phone
            u.user_address=address
            u.user_skillid=skill
            u.user_stateid=state

            db.session.commit()  

            flash('Details Updated')
            return redirect('/user/editprofile')
        # else:
        #     return 


@app.route('/demo/available')
def demo_available():
    return render_template('user/check_availability.html')

@app.route('/check/result')
def check_result():
    user = request.args.get('us')
    deets = db.session.query(User).filter(User.user_email==user).first()
    if deets == '':
        return 'Available'
    else:
        return 'Taken'


@app.route('/check/lga', methods=['POST','GET'])
def check_lga():
    #fetch the states that are available
    states = State.query.all()
    return render_template('user/load_lga.html', states=states)


@app.route('/demo/lga', methods=['POST'])
def show_lga():
    state = request.form.get('stateid')
    #TO DO: write a query that wll fetch from LGA table where state_id =state
    res = db.session.execute(f"SELECT * FROM lga WHERE state_id={state}")
    results = res.fetchmany(20)

    select_html = "<select>"
    for x,y,z in results:
        select_html = select_html + f"<option value='{x}'>{z}</option>"
    
    select_html = select_html + "</select>"

    return select_html

@app.route('/user/discussion')
def discussion():
    contactus = ContactForm()
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    
    if loggedin == None:
        return redirect('/')
    else:
        posts = Posts.query.all()
        return render_template('user/discussion.html', contactus=contactus, userdeets=userdeets, posts=posts)


@app.route('/post/details/<int:id>')
def post_details(id):
    contactus = ContactForm()
    loggedin = session.get('loggedin')
    userdeets = User.query.get(loggedin)
    
    if loggedin == None:
        return redirect('/')
    else:
        postdeets = Posts.query.get_or_404(id)
        commentdeets = db.session.query(Comments).filter(Comments.c_postid==id).order_by(desc(Comments.c_date)).all()
        return render_template('user/post_details.html', postdeets=postdeets, contactus=contactus, userdeets=userdeets, commentdeets=commentdeets)

@app.route('/post/comment', methods=['POST'])
def post_comment():
    #retrieve data
    loggedin = session.get('loggedin',0) #this zero here is the default value so if an invalid id(not on table) is entered  in route, instead of showing none, it defaults to zero
    postid = request.form.get('postid')
    comment = request.form.get('comment')
    #insert into association model

    #method1
    # c = Comments()
    # db.session.add(c)
    # c.c_userid=loggedin
    # c.c_postid=postid
    # c.c_comment=comment
    # db.session.commit()

    #method2
    # c = Comments(c_userid=loggedin,c_postid=postid,c_comment=comment)
    # db.session.add(c)
    # db.session.commit()

    # #method3
    user = User.query.get(loggedin)
    postid = Posts.query.get(postid)
    c = Comments()
    db.session.add(c)
    user.user_comments.append(c)
    postid.post_comments.append(c)
    c.c_comment=comment
    ddate = c.c_date
    return f'{comment} and {ddate}'


@app.route('/donate', methods=['POST', 'GET'])
def donate():
    contactus = ContactForm()

    if request.method == 'GET':
         return render_template('user/donation.html', contactus=contactus)
    else:
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        amt = request.form.get('amt')

        #generate a random number as a transaction ref
        ref = int(random.random() * 100000000)
        session['refno'] = ref #keep ref in session

        #insert into database
        db.session.execute(f"INSERT INTO donation SET fullname='{fullname}', email='{email}', amt='{amt}', status='pending', ref='{ref}'")
        db.session.commit()
        
        flash('Thank you for your donation, you have postively impacted more lives than you can imagine')
        return redirect('/confirmpay')


@app.route('/confirmpay')
def confirm_pay():
    contactus = ContactForm()
    refno = session.get('refno')

    qry = db.session.execute(f"SELECT * FROM donation WHERE ref='{refno}'")
    data = qry.fetchone()
    return render_template('user/confirmpay.html', data=data, contactus=contactus)


#The user submits selected breakouts to this route
@app.route("/user/sendbreakout", methods=['POST','GET'])
def send_breakout():
    loggedin = session.get('loggedin')
    if loggedin == None:
        return redirect("/")
    if request.method=='POST':
        #retrieve form data, breakout ids
        bid = request.form.getlist('bid')

        #insert new record into myorder,
        mo = Myorder(order_userid=loggedin)
        db.session.add(mo)
        db.session.commit()
        orderid = mo.order_id
        #generate a trans ref using random (save in session), insert into payment table
        ref = int(random.random() * 10000000)
        session['refno'] = ref
        #loop over the selected breakout ids and insert into
        #order_details, 
        totalamt = 0
        for b in bid:
            breakdeets = Breakout.query.get(b)
            break_amt = breakdeets.break_amt
            totalamt = totalamt + break_amt
            od = OrderDetails(det_orderid=orderid,det_breakid=b,det_breakamt=break_amt)
            db.session.add(od)

        db.session.commit()
        p = Payment(pay_userid=loggedin,pay_orderid=orderid,pay_ref=ref,pay_amt=totalamt)       
        db.session.add(p) 
        db.session.commit()
        return redirect("/user/confirm_breakout")    
    else:
        return redirect("/")

#This route will show all chosen sessions and connect to paystack
@app.route("/user/confirm_breakout", methods=['POST','GET'])
def confirm_break():
    loggedin = session.get('loggedin')
    ref = session.get('refno')
    if loggedin == None or ref == None:
        return redirect("/")
    userdeets = User.query.get(loggedin) 
    deets = Payment.query.filter(Payment.pay_ref==ref).first() 

    if request.method == 'GET':          
        contactus = ContactForm()                
        return render_template("user/show_breakout_confirm.html",deets = deets,userdeets=userdeets,contactus=contactus)
    else:
        url = "https://api.paystack.co/transaction/initialize"
        
        data = {"email":userdeets.user_email,"amount":deets.pay_amt}
        headers = {'Content-Type':'application/json','Authorization':'Bearer sk_test_cd05140387131fa0a4b595e1a7d8a2b1b9ae6b76'}

        response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, data=json.dumps(data))

        rspjson = json.loads(response.text) 
        if rspjson.get('status') == True:
            authurl = rspjson['data']['authorization_url']
            return redirect(authurl)
        else:
            return 'Please try again'

@app.route('/user/payverify')
def paystack():
    return 'JSON response from paystack will be sent here'

@app.route('/sendmail')
def sendmail():
    subject = 'Automated Email'
    sender = ['Kisses','aishatomoshood@gmail.com']
    recipient = ['aishatmoshood1@gmail.com']
    #instantiate an object of Message
    try:
        # msg = Message(subject=subject,sender=sender,recipients=recipient,body='<b>Love yah</b>')
        # mail.send(msg)
        # return 'Mail Sent'

        #method 2
        msg = Message()
        msg.subject = subject
        msg.sender = sender
        msg.body = 'Test Message again'
        msg.recipients=recipient

        #sending html
        htmlstr = '<h1>Thank you for registering</h1><h2>Signed Buffalo Clothings</h2> <img src="https://www.google.com/url?sa=i&url=https%3A%2F%2Fwww.facebook.com%2FBUFFALODESIGNS%2F&psig=AOvVaw20N2cDlVvkdE4gGSvG0BMe&ust=1649411264326000&source=images&cd=vfe&ved=0CAoQjRxqFwoTCODPoajXgfcCFQAAAAAdAAAAABAD">'
        msg.html = htmlstr

        with app.open_resource('nysc_certificate.pdf') as fp: #nysc_certificate.pdf is the name of the file directly in conference folder
            msg.attach('your_nysc_certificate.pdf','application/pdf', fp.read()) #application/pdf is the mimetype for pdf files 

        mail.send(msg)
        return 'Mail Sent'
    except:
        return 'Connection Refused'