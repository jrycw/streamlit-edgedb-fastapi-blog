import asyncio

import streamlit as st
from http_reqs import (
    delete_user,
    delete_users,
    get_user,
    get_user_names,
    get_users,
    patch_user,
    post_user,
)

st.header('Admin Panel')


async def main():
    with st.container():
        refresh_button = st.button('Refresh')
        if refresh_button:
            st.experimental_rerun()

    with st.container():
        st.header('Create a New User')

        with st.form('post-user-form'):
            name = st.text_input('Name (*):')
            email = st.text_input('Email (*):')
            post_user_butoon = st.form_submit_button('Post')
            if post_user_butoon:
                if name and email:
                    payload = {'name': name, 'email': email}
                    created_user = await post_user(payload)
                    if created_user:
                        st.success('User created success')
                    else:
                        st.warning(f'User created failed.\
                            The name "{name}" or/and the email "{email}"\
                                might be occupied')
                else:
                    st.warning('Please fill both name and email fields')

    with st.container():
        st.header('Update User')
        names = await get_user_names()
        if names:
            selected_updated_name = st.selectbox(
                'Select an author', names, key="selected_updated_name")
            if selected_updated_name:
                user = await get_user(selected_updated_name)
                name = user['name']
                email = user['email']
                patch_user_form_name = f'update-post-form-{name}'
                with st.expander(f'Update User {name}({email})'):
                    with st.form(patch_user_form_name):
                        updated_email = st.text_input('Email: ', email)
                        patch_user_form_name = st.form_submit_button(
                            f'Update User {name}({email}) confirm')
                        if patch_user_form_name:
                            updated_payload = {'email': updated_email}
                            updated_user = await patch_user(name, updated_payload)
                            if updated_user:
                                st.success('User updated success')
                            else:
                                st.warning(f'User updated failed. This email "{updated_email}"\
                                     might be occupied.')
        else:
            st.write('No user exists')

    with st.container():
        st.header('Delete User')
        names = await get_user_names()
        if names:
            selected_deleted_name = st.selectbox(
                'Select an author', names, key="selected_deleted_name")
            if selected_deleted_name:
                user = await get_user(selected_deleted_name)
                name = user['name']
                email = user['email']
                with st.expander(f'Delete User {name}({email})'):
                    delete_user_button_name = f'delete-button-{name}'
                    delete_user_button = st.button(
                        f'Delete confirm', key=delete_user_button_name)
                    if delete_user_button:
                        deleted_post = await delete_user(name)
                        if deleted_post:
                            st.success('User delete success')
                        else:
                            st.warning(
                                'User delete failed. This should not be happened,\
                                     please contact support team')
        else:
            st.write('No user exists')

    with st.container():
        st.header('View ALL Users')
        users = await get_users()
        if not users:
            st.write('No user exsting')
        else:
            with st.expander("View ALL Users"):
                for user in users:
                    st.json(user)

    with st.container():
        st.header('Delete ALL Users')
        with st.expander("Delete ALL Users"):
            delete_users_button = st.button(
                f'WILL DELETE ALL USERS AND POSTS',
                key='delete_users_button')
            if delete_users_button:
                deleted_posts = await delete_users()
                if deleted_posts:
                    st.experimental_rerun()

if __name__ == '__main__':
    asyncio.run(main())
