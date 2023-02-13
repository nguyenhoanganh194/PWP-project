# PWP-project
 The PWP project oulu course
## Project Database Instructions:

The dependencies of the project are provided in the file requirements.txt. 

The main database engine used in the project is SQLite, we interact with the database using the Flask SQLAlchemy toolkit.

the user can populate the database using the flask shell or the existing tests in the app.py file, using the shell as the following example:


```console
>>> from models import db, User
>>> User_John = User(user_name='john97', password='john1997')
>>> db.session.add(User_John)
>>> db.session.commit()
```
 a test is also included in app.py by default:
 
 ```python

 #Test
@app.route("/user/add/",methods=["POST"])
def add_user():
    try:
        user = models.User(
            id = 12,
            user_name = "12",
            password = "12"
        )
        models.db.session.add(user)
        models.db.session.commit()
        return "Successful",201
    except:
        return "User already exists",409


```
