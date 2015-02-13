from flask import render_template, redirect, session
from app import app
from app.forms import LoginForm, ChooseProjectForm, UploadForm, FinalForm
from app import unfuddle
import io

@app.route('/')
@app.route('/step1', methods=['GET','POST'])
def step1():
    form = LoginForm()
    if form.validate_on_submit():
        session['domain'] = form.domain.data
        session['user'] = form.username.data
        session['pw'] = form.password.data
        projects = unfuddle.get_projects()
        if projects:
            session['projects'] = projects
            return redirect('/step2')
        else:
            session['pw'] = ''
    return render_template("step1.html", form=form)

@app.route('/step2', methods=['GET','POST'])
def step2():
    projects = session.get('projects')
    if not projects:
       return redirect('/step1')

    form = ChooseProjectForm()
    form.project.choices = projects
    if form.validate_on_submit():
        projectid = form.project.data
        session['project'] = next((p for p in projects if p[0]==projectid), None)
        if session['project']:
            session['severities'] = unfuddle.get_severities(projectid)
            session['components'] = unfuddle.get_components(projectid)
            session['people'] = unfuddle.get_people(projectid)
            session['milestones'] = unfuddle.get_milestones(projectid)
            return redirect('/step3')
    return render_template("step2.html", form=form)
 
@app.route('/step3', methods=['GET','POST'])
def step3():
    project = session.get('project')
    if not project:
       return redirect('/step2')
    form = UploadForm()
    if form.validate_on_submit():
        session['tickets'] = unfuddle.parse_tickets(io.StringIO(form.csvfile.data.read().decode()), project[0])
        return redirect('/step4')
    return render_template("step3.html", project=project[1], form=form)

@app.route('/step4', methods=['GET','POST'])
def step4():
    project = session.get('project')
    if not project:
       return redirect('/step2')
    tickets = session.get('tickets')
    if not tickets:
        return redirect('/step3')
    project = session.get('project')
    form = FinalForm()
    if form.validate_on_submit():
        unfuddle.post_tickets(project[0], tickets)
        return redirect('/done')
    return render_template("step4.html", project=project[1], columns=unfuddle.COLUMNS, tickets=tickets, howmany=len(tickets), form=form)

@app.route('/done', methods=['GET'])
def done():
    return render_template("done.html")
