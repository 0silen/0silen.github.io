import pymysql
import markdown
from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sirin'


def get_db_conn():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='db',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"数据库连接失败: {e}")
        return None


def fetch_single_record(query, params):
    conn = get_db_conn()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
        conn.close()
        return result
    return None


def fetch_multiple_records(query, params=None):
    conn = get_db_conn()
    if conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params) if params else cursor.execute(query)
            results = cursor.fetchall()
        conn.close()
        return results
    return []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts/<int:post_id>')
def post(post_id):
    post = fetch_single_record('SELECT * FROM posts WHERE id = %s', (post_id,))
    if post:
        post['content'] = markdown.markdown(post['content'])
        return render_template('post.html', post=post)
    else:
        flash('文章未找到', 'error')
        return redirect(url_for('index'))


@app.route('/blog')
def blog():
    posts = fetch_multiple_records('SELECT * FROM posts')
    for post in posts:
        post['content'] = markdown.markdown(post['content'])
    return render_template('blog.html', posts=posts)


@app.route('/category/<int:type_id>')
def category(type_id):
    posts = fetch_multiple_records('SELECT * FROM posts WHERE type_id = %s', (type_id,))
    return render_template('category.html', posts=posts, type_id=type_id)


@app.route('/posts/new', methods=('GET', 'POST'))
def new():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        type_id = request.form.get('type_id')

        if not title:
            flash('标题不能为空', 'error')
        elif not content:
            flash('内容不能为空', 'error')
        elif not type_id:
            flash('请选择一个分区', 'error')
        else:
            conn = get_db_conn()
            if conn:
                with conn.cursor() as cursor:
                    cursor.execute('INSERT INTO posts (title, content, type_id) VALUES (%s, %s, %s)',
                                   (title, content, type_id))
                    conn.commit()
                conn.close()
                flash('提交成功！', 'success')
                return redirect(url_for('new'))
            else:
                flash('提交失败，数据库连接错误', 'error')
    return render_template('new.html')


@app.route('/posts/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = fetch_single_record('SELECT * FROM posts WHERE id = %s', (id,))
    if post:
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            if not title:
                flash('标题不能为空', 'error')
            else:
                conn = get_db_conn()
                if conn:
                    with conn.cursor() as cursor:
                        cursor.execute('UPDATE posts SET title = %s, content = %s WHERE id = %s', (title, content, id))
                        conn.commit()
                    conn.close()
                    flash('更新成功！', 'success')
                    return redirect(url_for('post', post_id=id))
                else:
                    flash('更新失败，数据库连接错误', 'error')
        return render_template('edit.html', post=post)
    else:
        flash('文章未找到', 'error')
        return redirect(url_for('index'))


@app.route('/posts/<int:id>/delete', methods=('POST',))
def delete(id):
    post = fetch_single_record('select * from posts where id=%s', (id,))
    if post:
        conn = get_db_conn()
        if conn:
            with conn.cursor() as cursor:
                cursor.execute("delete from posts where id =%s", (id,))
                conn.commit()
            conn.close()
            flash(f'"{post["title"]}"删除成功！', 'successs')
        else:
            flash('删除失败，数据库连接失败', 'error')
    else:
        flash('文章未找到', 'error')
    return redirect(url_for('blog'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/experiments')
def experiments():
    return render_template('experiments.html')


if __name__ == '__main__':
    app.run(debug=True)
