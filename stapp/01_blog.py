import asyncio

import streamlit as st

from http_reqs import delete_post, get_user, get_user_names, patch_post
from utils import get_excerpt, get_sort_by_updated_on, to_tz

st.set_page_config('SEF Blog')
st.header('SEF Blog')
streamlit_ = f'[Streamlit](https://streamlit.io/)'
edgedb_ = f'[EdgeDB](https://www.edgedb.com/)'
fastapi_ = f'[FastAPI](https://fastapi.tiangolo.com/)'
st.markdown(
    f'This blog app is built by {streamlit_} + {edgedb_} + {fastapi_}', unsafe_allow_html=True)


async def main():
    with st.container():
        refresh_button = st.button('Refresh')
    if refresh_button:
        st.experimental_rerun()

    names = await get_user_names()
    with st.container():
        if names:
            selected_name = st.selectbox(
                'Select an author', names, key="selected_name")
            if selected_name:
                user = await get_user(selected_name)

                name = user['name']
                email = user['email']
                posts = sorted(
                    user['posts'],
                    key=get_sort_by_updated_on(),
                    reverse=True)
                st.title(f"Author: {name}")
                st.caption(f'Author Email: {email}')
                n_posts = len(posts)
                if n_posts == 1:
                    st.write(
                        f'Author "{name}" has posted {n_posts} article : ')
                else:
                    st.write(
                        f'Author "{name}" has posted {n_posts} articles : ')

                with st.container():
                    for p in posts:
                        pid = p['id']
                        title = p['title']
                        content = p['content']
                        post_updated_on = to_tz(p['updated_on'])

                        st.header(f"{title}")
                        col_11, col_12, *_ = st.columns([5, 3, 2])
                        with col_11:
                            st.caption(f"post id: {pid}")
                        with col_12:
                            st.caption(f'last_updated: {post_updated_on}')

                        with st.expander(f'Excerpt: {get_excerpt(content)} ...(continued)'):
                            content = p['content']
                            st.write(content)

                        with st.expander("Update Post"):
                            patch_post_form_name = f'update-post-form-{pid}'
                            with st.form(patch_post_form_name):
                                updated_title = st.text_input(
                                    'Title: ', title)
                                updated_content = st.text_area(
                                    'Content: ', content)
                                patch_post_form_name = st.form_submit_button(
                                    'Update confirm')
                                if patch_post_form_name:
                                    updated_payload = {
                                        'title': updated_title, 'content': updated_content}
                                    updated_post = await patch_post(pid, updated_payload)
                                    if updated_post:
                                        st.success('Post updated success')
                                    else:
                                        st.warning('Post updated failed')

                        with st.expander("Delete Post"):
                            delete_post_button_name = f'delete-button-{pid}'
                            delete_post_button = st.button(
                                'Delete', key=delete_post_button_name)
                            if delete_post_button:
                                deleted_post = await delete_post(pid)
                                if deleted_post:
                                    st.success('Post deleted success')
                                else:
                                    st.warning('Post deleted failed')

if __name__ == '__main__':
    asyncio.run(main())
