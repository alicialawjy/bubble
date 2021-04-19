# Bubble 
A twitter-like social network website! <br>
This project was done as part of the Harvard x EdX Course: CS50 Web Programming with Python and JavaScript.

## Project Setup
1. Download the zip file.
2. In your terminal, cd into the Bubble directory.
3. Run ```python manage.py runserver``` and visit <a>http://127.0.0.1:8000/</a>

## Functionality
* Note: user needs to be logged in to experience these functionalities.
1. <b>New Post</b>
- Users can make new post from the home page and following page.
- Alternatively, they can also do so with the 'New Bubble' button on the sidebar.
- Submit button is disabled if textarea is empty to prevent submission of an empty post.
<br>

2. <b>Edit</b>
- Users can edit a post via the 'Edit' button on each post, which will only be visible if the post is originated by the user (users are only allowed to edit their own posts).
- The content of that post will be preloaded into the textarea for the user to edit.
<br>

3. <b>Reply</b>
- Users can reply to a post by clicking on the reply icon at the bottom of each post.
- Once replied, this is recorded as a reply to the main post:
  - the main post's reply count increases, and
  - the reply will be visible in the individual post's view (can be viewed by clicking on the main post).
<br>

4. <b>Like</b>
- Users can like a post once by clicking on the heart icon at the bottom of each post.
- If the post has been liked, clicking on the button again will cause the user to un-like the post.
- Like count changes accordingly
<br>

5. <b>Follow</b>
- Users can follow/unfollow each other via the 'follow'/'unfollow' buttons on user profile pages.
- Users are not allowed to follow themselves.
<br>

6. <b>Search</b>
- Users can search for other users via the search bar.
- The search goes through the username database.
- If the query is an exact match with a username in the database, the user is redirected to the profile page of the person they were looking for.
- Else, the user is directed to a search result page with potential users which contain the query as a substring in their username. (eg. 'us' will show 'user1' as a search result).

## Page Views
1. <b>Profile Page</b>
- This can be accessed by clicking on a user's name on any post, or searching for a user via the search bar.
- Shows only posts made by the user, in reverse chronological order.
- If the profile belongs to the current user, the follow button will not be visible in the profile (user cannot follow themselves).
<br>

2. <b>Home</b>
- This shows all the posts by <b>every</b> user on the platform in reverse chronological order.
- Is visible even when users are not logged in.
<br>

3. <b>Following</b>
- This shows only posts by people that the current user follows.
<br>

4. <b>Individual posts</b>
- Clicking anywhere on a post will bring the user to the individual post view.
- Shows the post itself, as well as replies (if any).
<br>

5. <b>Search results page</b>
<br>

6. <b>Login</b>
<br>

7. <b>Register</b>

## Tech Stack
- Backend Framework: Django
- Database Modelling: SQLite
- Python
- HTML, CSS and Javascript

