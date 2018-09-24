from init import app, db, config
from flask import render_template, Markup, request, session
import hashlib
import utils
from mail import MailServer
from models import User, Token, Salt, EmailToken

@app.route('/')
def indexView(wmessage=None):
    e = session.get("email")
    if (session.get("email") is not None) and (session.get("email") is not None):
        if verifySessionData(session.get("email"), session.get("X-Auth-Token")):
            return render_template("dashboard_page.html")
        else:
            return logout()
    return render_template("index_page.html", warningMessage=wmessage)


@app.route('/login', methods=['GET'])
def loginView():
    if verifySessionData(session.get("email"), session.get("X-Auth-Token")):
        return render_template("dashboard_page.html")
    return render_template("login_page.html")


@app.route('/project')
def projectView():
    return render_template("project_page.html")


@app.route('/register', methods=['GET'])
def registerView():
    return render_template("register_page.html")


@app.route('/register', methods=['POST'])
def registerForm():
    # get form details
    email = Markup(unicode(request.form["inputEmail"])).striptags()
    password = Markup(unicode(request.form["inputPassword"])).striptags()
    # make salt and hash that password
    pwdhash = hashlib.sha512(password).hexdigest()
    salt = utils.generate_salt()
    # generate token
    token = unicode(utils.generate_token())
    # save in database
    try:
        newUser = User(email=email, pwdhash=pwdhash, salt=salt)
        db.session.add(newUser)

        newToken = Token(email=email)
        db.session.add(newToken)

        newSalt = Salt(email=email, salt=salt, id_user=newToken.id_user)
        db.session.add(newSalt)
        try:
            db.session.commit()
        except Exception as e:
            print e
        return indexView()
    except:
        return render_template("register_page.html", warningMessage="Something wrong happens!")


@app.route('/login', methods=['POST'])
def loginForm():
    # get form details
    email = Markup(unicode(request.form["inputEmail"])).striptags()
    password = Markup(unicode(request.form["inputPassword"])).striptags()
    # make salt and hash that password
    pwdhash = hashlib.sha512(password).hexdigest()
    # get user_id
    u = User.query.filter_by(email=email).first()
    if u is None:
        return render_template("login_page.html", warningMessage="Wrong credentials!")
    # get salt
    mySalt = Salt.query.filter_by(id_user=u.id).first()
    # pwdhash + salt
    pwd = pwdhash + mySalt.salt
    u = User.query.filter_by(email=email, pwdhash=pwd).first()
    if u is None:
        return render_template("login_page.html", warningMessage="Wrong credentials!")
    else:
        session["email"] = u.email
        token = Token.query.filter_by(id_user=u.id).first()
        session["X-Auth-Token"] = token.token
        return render_template("dashboard_page.html")


@app.route('/logout')
def logout():
    session.clear()
    return render_template("index_page.html")


@app.route('/recovery', methods=['GET'])
def recoveryView():
    return render_template("recovery_page.html")


@app.route('/recovery', methods=['POST'])
def recoveryForm():
    email = Markup(request.form.get("inputEmail")).striptags()
    # verify email
    u = User.query.filter_by(email=email).first()
    if u is None:
        return render_template("recovery_page.html", warningMessage="Wrong email address.")
    # get email token first
    et = EmailToken.query.filter_by(id_user=u.id, enable=False).first()
    if et is None:
        # create email token
        et = EmailToken(email)
        db.session.add(et)
        db.session.commit()
    urlToken = et.token
    lastUrl = "http://"+ config["ip"] +":"+ unicode(config["port"]) +"/rlink?url=" + urlToken
    template = render_template("email.html", pagetitle=config["page_title_email"], welcome="Hey!",
                               introduction="You forgot your password ?. Please verify this action.", btn=True,
                               btndescription="Continue", btnurl=lastUrl, site=True,
                               siteurl=config["site_url_email"],
                               sitename=config["site_name_email"], greetings="See you soon.",
                               footer="This is a automated message, please don't reply.")
    ms = MailServer([email,], mail=config["email_smtp"], password=config["pwd_smtp"])
    ms.message(subject=config["app_name"] + "- Confirm registration", body=template)
    ms.send_email()
    return indexView("Please, check your email.")


@app.route('/rlink', methods=['GET'])
def recoveryLink():
    token = request.args.get("url")
    line = EmailToken.query.filter_by(token=token, enable=False).first()
    if line is None:
        return indexView()
    line.enable = True
    db.session.commit()
    return render_template("reset_page.html", user=line.id_user)


@app.route('/reset', methods=['POST'])
def resetCredentials():
    password = Markup(request.form.get("inputPassword")).striptags()
    id_user = Markup(request.form.get("inputId")).striptags()
    pwdhash = hashlib.sha512(password).hexdigest()
    salt = utils.generate_salt()
    # save salt
    s = Salt.query.filter_by(id_user=id_user).first()
    if s is None:
        return indexView()
    s.salt = salt
    u = User.query.filter_by(id=id_user).first()
    if u is None:
        return indexView()
    u.pwdhash = pwdhash + salt
    db.session.commit()
    return indexView("Your password was successfully changed.")


def verifySessionData(email, token):
    u = User.query.filter_by(email=email).first()
    if u is None:
        return False
    t = Token.query.filter_by(id_user=u.id, token=token).first()
    if t is None:
        return False
    return True
