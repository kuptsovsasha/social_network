# Social Network
Social Network is a web application built with Django that allows users to create accounts, connect with friends, and share posts and updates.

# Installation
1. Clone the repository: ```git clone``` https://github.com/your-username/social_network.git
2. Navigate to the project directory: ```cd social_network```
3. Create a virtual environment: ```python -m venv .env```
4. Activate the virtual environment: ```source .env/bin/activate``` (on Windows, use ```env\Scripts\activate```)
5. Install dependencies: ```pip install -r requirements.txt```
6. Create migrations: ```python manage.py makemigrations```
7. Create a database: ```python manage.py migrate```
8. Create superuser: ```python manage.py createsuperuser```
9. Run the server: ```python manage.py runserver```
10. The application should now be accessible at http://localhost:8000.
11. The application admin should now be accessible at http://localhost:8000/admin.

# Features
- user app handle: users can create accounts, log in, log out, change password
- user_profile app handle: users can view his profile, view friend profile, can edit/delete own profile, 
can send friend request to other user, can accept/decline friend request, can view friends list/remove friend from list,
can search other profiles and send friend request.
- post_app: users can create posts
- chat_app: users can create messages to friends, can view list with friends with whom they already have conversations
