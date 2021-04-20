# Bubble 
A twitter-like social network website! <br>
This project was done as part of the Harvard x EdX Course: CS50 Web Programming with Python and JavaScript.

## Project Setup
1. Download the zip file.
2. In your terminal, cd into the 'Bubble' directory.
3. Run ```python manage.py runserver``` and visit <a>http://127.0.0.1:8000/</a>

## Tech Stack
- Backend Framework: Django and Python
- Database Modelling: SQLite
- Front End Languages: HTML, CSS and Javascript
- Browser Testing: Selenium

## Functionality
!!! Note: user needs to be logged in to experience these functionalities.
#### 1. Make a New Post
- Via home page and following page.
- Alternatively, use the 'New Bubble' button on the sidebar.
- Submit button is disabled if textarea is empty to prevent submission of an empty post.

#### 2. Edit Post
- Via the 'Edit' button on each post, which will only be visible if the post is originated by the user (users are only allowed to edit their own posts).
- The content of that post will be preloaded into the textarea for the user to edit.

#### 3. Reply to Post
- Click the reply icon at the bottom of each post.
- Once replied, this is recorded as a reply to the main post:
  - the main post's reply count increases, and
  - the reply will be visible in the individual post's view (can be viewed by clicking on the main post).

#### 4. Like a Post
- Click the heart icon at the bottom of each post.
- If the post has been liked, clicking on the button again will cause the user to un-like the post.
- Like count changes accordingly

#### 5. Follow a User
- Users can follow/unfollow each other via the 'follow'/'unfollow' buttons on user profile pages.
- If the current user is on their own profile, the follow button will not be visible in their page (users cannot follow themselves).

#### 6. Search a User
- Users can search for other users via the search bar.
- The search goes through the username database.
- If the query is an exact match with a username in the database, the user is redirected to the profile page of the person they were looking for.
- Else, the user is directed to a search result page with potential users which contain the query as a substring in their username. (eg. 'us' will show 'user1' as a search result).

## Page Views
#### 1. Profile Page
- This can be accessed by clicking on a user's name on any post, or searching for a user via the search bar.
- Shows only posts made by the current user, in reverse chronological order.

#### 2. Home
- This shows all the posts by <b>every</b> user on the platform in reverse chronological order.
- Is visible even when users are not logged in.

#### 3. Following
- This shows only posts by people that the current user follows in reverse chronological order..

#### 4. Individual posts
- Clicking anywhere on a post will bring the user to the individual post view.
- Shows the post itself, as well as replies to the post (if any).

#### 5. Search results page

#### 6. Login

#### 7. Register

## Unit Testing
Unit tests have been implemented for Django/Client testing (testing the methods in views.py and model fields in models.py). Selenium has been used for browser testing (assessing JavaScript methods). 
These tests are saved under the test.py file in the network folder. <br>
To run the unit tests:
1. In your terminal, cd into the 'Bubble' directory.
2. Run ```python manage.py test``` 


