# streamlit-edgedb-fastapi-blog
A simple blog app built by [Streamlit](https://streamlit.io/) + [EdgeDB](https://www.edgedb.com/) + [FastAPI](https://fastapi.tiangolo.com/)

```
pip install -r requirements.txt

# EdgeDB
edgedb project init
edgedb migration create
edgedb migrate

# FastAPI
uvicorn app.main:api

# Streamlit
streamlit run stapp/01_blog.py

# pytest
edgedb instance create test01
edgedb -I test01 migrate
python -m pytest tests/
edgedb instance destroy -I test01 --force
```

## Blog
![blog-list](images/blog_list.png)
![blog-detail-show](images/blog_detail_show.png)
![blog-detail_edit](images/blog_detail_edit.png)

# Create Post
![create-post](images/create_post.png)

# Admin
![admin-create-user](images/admin_create_user.png)
![admin-view-users](images/admin_view_users.png)
![admin](images/admin.png)
