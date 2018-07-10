# coding=utf-8

from flask import Flask, render_template, json, request,redirect,session
from flaskext.mysql import MySQL
import hashlib, time, random, base64, tempfile
import matplotlib 
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from io import StringIO, BytesIO

from github import Github
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)

mysql = MySQL()

# MySQL configurations
app.secret_key = "***"
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = '***********'
app.config['MYSQL_DATABASE_DB'] = 'HumanMatrix'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/saveProject', methods=['POST'])
def saveProject():
    try:
        _pmID = session['userID']
        _projectName = request.form['projectName']
        _description = request.form['description']
        _startDate = request.form['startDate']
        _phase = 'Conceptual'

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO projects (pmID, name, description, conceptual_date, phase) VALUES(%s,%s,%s,%s,%s)",(int(_pmID), _projectName, _description, _startDate, _phase))      
        conn.commit()
        
    except Exception as e:

        return json.dumps({'status':"error-alert",
                        'message': str(e),
                        'data':{}}) 

    return redirect('/')
   
@app.route("/")
def root():
    if 'userID' not in session:
        return redirect('/login')
    else:
        try:
            con = mysql.connect()

            #Read the user info
            dfUserInfo = pd.read_sql('SELECT * FROM users WHERE userID='+str(session['userID']), con=con)

            #Read the projects status
            df = pd.read_sql('SELECT * FROM projects WHERE pmID='+str(session['userID']), con=con)
            
            del df['projectID']
            del df['pmID']
            del df['name']
            df['Order'] = 0
            
            df = df.groupby(['phase']).count()
            
            if 'Conceptual' not in df.index.values:
                df.loc['Conceptual'] = 0
            df['Order'].loc['Conceptual'] = 0
            
            if 'Definition' not in df.index.values:
                df.loc['Definition'] = 0
            df['Order'].loc['Definition'] = 1 

            if 'Planning' not in df.index.values:
                df.loc['Planning'] = 0
            df['Order'].loc['Planning'] = 2
            
            if 'Execution' not in df.index.values:
                df.loc['Execution'] = 0
            df['Order'].loc['Execution'] = 3
            
            if 'Closing' not in df.index.values:
                df.loc['Closing'] = 0
            df['Order'].loc['Closing'] = 4
            
            if 'Evaluation' not in df.index.values:
                df.loc['Evaluation'] = 0
            df['Order'].loc['Evaluation'] = 5
            
            df.sort_values(by='Order', inplace=True)

            df.drop('Order', axis=1, inplace=True)
            
            img = BytesIO()
            barlist = plt.bar(df.index, height=df['description'], align='center')   
            barlist[0].set_color('#ffb22b')    
            barlist[1].set_color('#3399ff')   
            barlist[2].set_color('#745af2')    
            barlist[3].set_color('#06d79c')   
            barlist[4].set_color('#ef5350')    
            barlist[5].set_color('#d4f739')   

            plt.savefig(img, format='png')
            plt.clf()
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            htmlImage = '<img src="data:image/png;base64,{}" style="float:left">'.format(plot_url)

            return render_template('index.html', 
                                    image=htmlImage, 
                                    name=dfUserInfo['name'][0]+' '+dfUserInfo['surname'][0], 
                                    birthDate=dfUserInfo['birthDate'][0], 
                                    email=dfUserInfo['email'][0],
                                    opened=df.loc['Conceptual'][0] + df.loc['Definition'][0] + df.loc['Planning'][0] + df.loc['Execution'][0],
                                    closed=df.loc['Closing'][0],
                                    evaluation=df.loc['Evaluation'][0])
        except Exception as e:
            return render_template('error.html', message={'value': e})

@app.route("/projects")
def projects():
    try:
        con = mysql.connect()
        df = pd.read_sql("SELECT * FROM projects WHERE pmID="+str(session['userID'])+" ORDER BY phase", con=con)
        df.drop('pmID', axis=1, inplace=True)

        phases = ['Definition', 'Conceptual', 'Planning', 'Execution', 'Closing', 'Evaluation']
        table=['','','','','','']
        
        i = -1
        for phase in phases:
            i=i+1
            table[i] = '<table class="table vm no-th-brd no-wrap pro-of-month"><thead>'
 
            for column in df.columns.values:
                if column != 'projectID' and  column != 'phase' and column != 'phase':
                    if column.find("_date") != -1:
                        if column.capitalize().replace("_date",'') == phase:
                            table[i] = table[i]+'<th>'+column.capitalize().replace("_"," ")+'</th>' 
                    else:
                        table[i] = table[i]+'<th>'+column.capitalize().replace("_"," ")+'</th>'

            table[i] = table[i]+'<th>Action</th>'
            table[i] = table[i]+'</thead><tbody>'
            
            empty = True
            for _, row in df.iterrows():
                table[i] = table[i]+'<tr>'
                if row['phase'] == phase:
                    empty = False
                    for column in df.columns.values:
                        if column != 'projectID' and column != 'phase':
                            if column.find("_date") != -1:
                                if column.capitalize().replace("_date",'') == phase:
                                    table[i] = table[i]+'<td>'+str(row[column])+'</td>' 
                            else:
                                table[i] = table[i] + '<td>'+str(row[column])+'</td>'

                    table[i] = table[i]+'<td><a href="details?projectID='+str(row['projectID'])+'">Details</a></td></tr>'
            if empty:
                table[i] = '<center>0 projects are in this phase.</center>'
            else:
                table[i] = table[i] + '</tbody></table>'  

        return render_template('projects.html', tableDef=table[0], tableCon=table[1], tablePla= table[2], tableExe=table[3], tableClo=table[4], tableEva=table[5])
    except Exception as e:
        return render_template('error.html', message={'value': e})

@app.route("/tasks/csv/import", methods=['POST'])
def task_csv_import():

    _value = StringIO(request.form['value'])
    _projectID = request.form['projectID']
    df = pd.read_csv(_value, sep=";")
    
    schema = list(df.columns.values)

    if schema != ["Task Name", "Description"]:
        return json.dumps({'status':"error-alert",
                        'message': "CSV Schema not compatible!",
                        'data':{}})    
    elif df.isnull().values.any():
        return json.dumps({'status':"error-alert",
                        'message': "Missing values!",
                        'data':{}}) 
    else:
        try:
            conn = mysql.connect()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                cursor.execute("INSERT INTO tasks (projectID, name, description) VALUES(%s,%s,%s)", (int(_projectID), row[0], row[1]))      
                conn.commit()
            
        except Exception as e:
            return json.dumps({'status':"error-alert",
                        'message': str(e),
                        'data':{}}) 
        
        return json.dumps({'status':"success-alert",
                        'message': "Values Saved!",
                        'data':{}})  


@app.route("/github/addTeamMember", methods=['POST'])
def addTeamMember():
    try:

        _githubID = request.form['githubID']
        _projectID = request.form['projectID']

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO team (projectID, githubname) VALUES(%s,%s)",(int(_projectID), str(_githubID)))      
        conn.commit()

    except Exception as e:

        return json.dumps({'status':"error-alert",
                        'message':  str(e),
                        'data':{}}) 

    return json.dumps({'status':"success-alert",
                    'message':  "Added!",
                    'data':{}}) 
                    
@app.route("/github/loadSuggestions", methods=['GET'])
def loadSuggestions():

    _filters = request.args.get('filters', '')
    _sort = request.args.get('sort', '').lower()
    _order = request.args.get('order', '')
    _showTop = int(request.args.get('showTop', ''))
    _projectID = int(request.args.get('projectID', ''))
    g = Github(session['git_user'], session['git_pass'])

    l = []
    x = 0
    for user in g.search_users(_filters, sort=_sort, order=_order):
        x = x + 1
        
        bio = ''
        if user.bio is not None:
            bio = user.bio

        hireable = None
        if user.hireable is not None:
            hireable = user.hireable

        name = ''
        if user.name is not None:
            name = user.name

        avatar_url = ''
        if user.avatar_url is not None:
            avatar_url = user.avatar_url

        email = ''
        if user.email is not None:
            email = user.email
        
        login = user.login
        
        l.append({
            'avatar_url':avatar_url,
            'login':login,
            'bio':bio,
            'name': name,
            'email': email,
            'hireable': hireable
        })

        if x == _showTop:
            break
    
    table = '<table class="table vm no-th-brd no-wrap pro-of-month"><thead>'
    table = table+'<th>#</th><th>Name</th><th>Available</th><th>Contacts</th><th>Add</th><th>Bio</th>'
    table = table+'</thead><tbody>'
    
    for candidate in l:
        table = table+'<tr>'
        table = table +'<td style="width:50px;"><span class="round"><img src="'+candidate['avatar_url']+'" alt="user" width="50"></span></td>'
        table = table +'<td>'+candidate['name']+'</td>'
        if candidate['hireable'] is None:
            table = table +'<td style="padding-left: 45px;"><i class="pull-right font-14 p-2 label label-rounded label-inverse"></i></td>'
        elif eval(str(candidate['hireable'])):
            table = table +'<td style="padding-left: 45px;"><i class="pull-right font-14 p-2 label label-rounded label-success"></i></td>'
        else:
            table = table +'<td style="padding-left: 45px;"><i class="pull-right font-14 p-2 label label-rounded label-warning"></i></td>'
        table = table +'<td>'+candidate['email']+'</td>'
        table = table +'<td><button class="pull-right btn btn-sm btn-rounded btn-primary" onclick="addToTeam(\''+str(candidate['login'])+'\', \''+str(_projectID)+'\')">Add to the Team</button></td>'
        table = table +'<td>'+candidate['bio']+'</td>'
        table = table+'</tr>'
            
    table = table + '</tbody></table>'  

    return json.dumps({'status':"success-alert",
                'message': str(len(l))+' found...',
                'data':{
                    'filters': _filters,
                    'users':l,
                    'table': table
                }})

@app.route("/loadProjects")
def loadProjects():
    try:
        _pmID = session['userID']

        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT phase FROM projects WHERE pmID= %s", (_pmID))
        data = cursor.fetchall()
        
        if len(data) > 0:
            return json.dumps({'status':"success-alert",
                            'message': str(len(data))+" projects found.",
                            'data':{
                                'projects': data
                            }})
        else:
            return json.dumps({'status':"success-alert",
                            'message': "0 projects found!",
                            'data':{}})

    except Exception as e:
        return json.dumps({'status':"error-alert",
                        'message': str(e),
                        'data':{}})

@app.route("/login")
def main():
    if 'userID' in session:
        return redirect('/')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('userID', None)
    return redirect('/login')

@app.route('/new-project')
def new_project():
    return render_template('new-project.html')

@app.route('/details', methods=['GET'])
def details():
    try:
        _projectID = request.args.get('projectID', '')
        con = mysql.connect()
        df = pd.read_sql('SELECT * FROM projects WHERE projectID='+_projectID, con=con)
        df.drop('projectID', axis=1, inplace=True)
        
        table = '<table class="table vm no-th-brd no-wrap pro-of-month"><thead>'
        for column in df.columns.values:
            table = table+'<th>'+column.capitalize()+'</th>'
            
        table = table+'</thead><tbody>'
        
        for _, row in df.iterrows():
            table = table+'<tr>'
            for column in df.columns.values:
                table = table + '<td>'+str(row[column])+'</td>'
            table = table+'</tr>'
              
        table = table + '</tbody></table>'  

        if df['conceptual_date'][0] is None:
            cValue = 'warning'
        else:
            cValue = 'success'

        if df['definition_date'][0] is None:
            dValue = 'warning'
        else:
            dValue = 'success'

        if df['planning_date'][0] is None:
            pValue = 'warning'
        else:
            pValue = 'success'

        if df['execution_date'][0] is None:
            eValue = 'warning'
        else:
            eValue = 'success'

        if df['closing_date'][0] is None:
            clValue = 'warning'
        else:
            clValue = 'success'

        if df['evaluation_date'][0] is None:
            evValue = 'warning'
        else:
            evValue = 'success'

        return render_template('details.html', cValue=cValue, dValue=dValue, eValue=eValue, pValue=pValue, clValue=clValue, evValue=evValue)
    except Exception as e:
        return render_template('error.html', message={'value': e})

@app.route('/pages-error-404')
def page_404():
    return render_template('pages-error-404.html')

def getNameFromGithub(login):

    g = Github(session['git_user'], session['git_pass'])
    
    return g.get_user(login)

@app.route('/hm', methods=['GET'])
def hm():

    _projectID = request.args.get('projectID', '')

    con = mysql.connect()
    
    df = pd.read_sql('SELECT * FROM tasks WHERE projectID='+_projectID, con=con)
    df.drop('projectID', axis=1, inplace=True)
    #df.drop('tasksID', axis=1, inplace=True)

    df2 = pd.read_sql('SELECT * FROM team WHERE projectID='+_projectID, con=con)
    df2.drop('projectID', axis=1, inplace=True)

    table = '<table id="ramTable" class="table vm no-th-brd no-wrap pro-of-month"><thead>'
    for column in df.columns.values:
        if column != 'tasksID':
            table = table+'<th style="width:200px">'+column.capitalize()+'</th>'

    for _, row in df2.iterrows():
        for column in df2.columns.values:
            user = getNameFromGithub(row[column])
            table = table +'<th>\
                            <span class="round">\
                            <img src="'+user.avatar_url+'" alt="user" width="50"></span>\
                            '+user.name+'</th>'
        
    table = table+'</thead><tbody>'
    
    for _, row in df.iterrows():
        table = table+'<tr>'
        for column in df.columns.values:
            if column != 'tasksID':
                table = table + '<td onclick="addFilter(\''+str(row[column])+'\')" style="cursor:pointer">'+str(row[column])+'</td>'
        
        for _, row2 in df2.iterrows():
            for column in df2.columns.values:

                #read the role of the employee
                dftmp = pd.read_sql('SELECT roleID FROM ram WHERE projectID='+_projectID+' AND githubname="'+str(row2[column])+'" AND taskID='+str(row[0]), con=con)
                if len(dftmp) == 0:                    
                    table = table+'<td>\
                                    <select onchange="updateRole(\''+str(row2[column])+'\', \''+str(row[0])+'\', \''+str(_projectID)+'\', this)">\
                                    <option value="0"></option>'
                    
                    table = table + '<option value="responsible">Responsible</option>'
                    table = table + '<option value="accountable">Accountable</option>'      
                    table = table + '<option value="consulted">Consulted</option>'     
                    table = table + '<option value="informed">Informed</option>'     
                else:
                    table = table+'<td>\
                                    <select onchange="updateRole(\''+str(row2[column])+'\', \''+str(row[0])+'\', \''+str(_projectID)+'\', this)">'

                    if dftmp['roleID'][0] == 'responsible':
                        table = table + '<option value="responsible" selected>Responsible</option>'
                    else:
                        table = table + '<option value="responsible">Responsible</option>'

                    if dftmp['roleID'][0] == 'accountable':
                        table = table + '<option value="accountable" selected>Accountable</option>'
                    else:
                        table = table + '<option value="accountable">Accountable</option>'

                    if dftmp['roleID'][0] == 'consulted':
                        table = table + '<option value="consulted" selected>Consulted</option>'
                    else:
                        table = table + '<option value="consulted">Consulted</option>'

                    if dftmp['roleID'][0] == 'informed':
                        table = table + '<option value="informed" selected>Informed</option>'
                    else:
                        table = table + '<option value="informed">Informed</option>'

                table = table +'</select></td>'
        table = table+'</tr>'

    table = table + '</tbody></table>'  

    return render_template('hm.html', table=table)

@app.route('/ram/update',methods=['POST'])
def ram_update():
    
    try:
        _githubname = request.form['githubname']
        _taskID = request.form['taskID']
        _roleID = request.form['roleID']
        _projectID = request.form['projectID']

        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()

        cursor.execute("SELECT * FROM ram WHERE taskID= %s AND projectID = %s AND githubname = %s", (int(_taskID), int(_projectID), _githubname))
        data = cursor.fetchall()

        if len(data) == 0:
            cursor.execute("INSERT INTO ram (taskID, projectID, githubname, roleID) VALUES(%s,%s,%s,%s)", (int(_taskID), int(_projectID), _githubname,  _roleID))     
        else:
            cursor.execute("UPDATE ram SET roleID=%s WHERE taskID= %s AND projectID = %s AND githubname = %s", (_roleID, int(_taskID), int(_projectID), _githubname))
        
        con.commit()

        return json.dumps({'status':"success-alert",
                        'message': 'saved!',
                        'data':request.form
                        }) 

    except Exception as e:
            return json.dumps({'status':"error-alert",
                            'message': str(e),
                            'data':{}}) 


@app.route('/ram/export',methods=['GET'])
def ram_export():
    
    try:
        _projectID = request.args.get('projectID', '')
        s = StringIO()
        
        # connect to mysql
        con = mysql.connect()
        df = pd.read_sql('SELECT * FROM tasks,ram WHERE tasks.projectID='+_projectID, con=con)
        df.drop('taskID', axis=1, inplace=True)
        df.drop('projectID', axis=1, inplace=True)
        df.to_csv(s, sep=";", index=False, line_terminator=',<br />')

        return render_template('csv.html', ram=s.getvalue())

    except Exception as e:
            return render_template('error.html', message={'value': e})


@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']
         
        # connect to mysql
        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT userID FROM users WHERE email= %s AND password = %s", (_username, _password))
        data = cursor.fetchall()

        if len(data) > 0:
            session['userID'] = data[0][0]
            return json.dumps({'status':"success-alert",
                            'message': 'Login Successful!',
                            'data':{}}) 
        else:
            return json.dumps({'status':"error-alert",
                            'message': 'Wrong Credentials!',
                            'data':{}}) 

    except Exception as e:
            return json.dumps({'status':"error-alert",
                            'message': str(e),
                            'data':{}}) 

@app.route('/validateGithubLogin',methods=['POST'])
def validateGithubLogin():
    try:
        _username = request.form['inputEmail']
        _password = request.form['inputPassword']

        # using username and password
        g = Github(_username, _password)
    
        x = False
        for _ in g.get_user().get_repos():
            x = True

        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute("SELECT userID FROM users WHERE githubname=%s", (_username))
        data = cursor.fetchall()

        if len(data) > 0:
            session['userID'] = data[0][0]
            session['git_user'] = _username
            session['git_pass'] = _password
            return json.dumps({'status':"success-alert",
                            'message': 'Login Successful!',
                            'data':{}}) 
        else:
            return json.dumps({'status':"error-alert",
                            'message': 'Wrong Credentials!',
                            'data':{}}) 
    except Exception as e:
        return json.dumps({'status':"error-alert",
                        'message': 'Wrong Credentials!',
                        'data':{}}) 

@app.route('/project/phase/update', methods=['POST'])
def updateDate():
    try:
        _projectID = request.form['projectID']
        _type = request.form['type']
        _date = request.form['date']

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET "+_type+"_date=%s WHERE projectID=%s", (_date, int(_projectID)))
        conn.commit()

        cursor.execute("UPDATE projects SET phase=%s WHERE projectID=%s", (_type.capitalize(), int(_projectID)))
        conn.commit()
        
        return json.dumps({'status':"success-alert",
                        'message': 'Project Status Updated',
                        'data':{}}) 

    except Exception as e:

        return json.dumps({'status':"error-alert",
                        'message': str(e),
                        'data':{}}) 
                      
if __name__ == "__main__":
    app.run()
