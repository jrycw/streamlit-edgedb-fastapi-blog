import asyncio

import streamlit as st
from http_reqs import get_post, get_user, get_user_names, post_post

st.header('Create a New Post!')


async def main():
    names = await get_user_names()
    if names:
        with st.container():
            name = st.selectbox('Select an author', names, key="name")
            user = await get_user(name)
        with st.container():
            with st.form('post-post-form'):
                author_name = user['name']
                title = st.text_input('Title (*):')
                content = st.text_area('Content (*):')
                post_post_butoon = st.form_submit_button('Post')
                if post_post_butoon:
                    if title and content:
                        payload = {'title': title, 'content': content}
                        created_post = await post_post(payload, author_name)
                        if created_post:
                            st.success('Post created success')
                        else:
                            st.warning('Post created failed')
                    else:
                        st.warning('Please fill both title and content fields')

if __name__ == '__main__':
    asyncio.run(main())
