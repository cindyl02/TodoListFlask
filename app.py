from flask import Flask, render_template, request, redirect, url_for
import datetime

app = Flask(__name__)
todo_list = {}


@app.route('/')
def home():
    date = datetime.date.today()
    title = f"My todo-list {date}"
    global todo_list
    return render_template('home.html', title=title, todos=todo_list)


@app.route('/submit', methods=['POST'])
def submit():
    task = request.form.get('new-task')
    global todo_list
    if task not in todo_list:
        todo_list[task] = None
    return redirect(url_for('home'))


@app.route('/delete/<item>', methods=['GET'])
def delete(item):
    global todo_list
    print(todo_list)
    item = item.replace("%", " ")
    todo_list.pop(item, None)
    print(todo_list)
    return redirect(url_for('home'))


@app.route('/setdate/<item>', methods=['GET'])
def setdate(item):
    global todo_list
    todo_list[item] = request.args.get("date")
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
