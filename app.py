from flask import Flask,render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    #return "hello world"
    return render_template('index.html', app_name='BulkBois', description='For the GymBros')

if __name__ == '__main__':
    app.run()
