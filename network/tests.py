from django.test import Client, TestCase
from .models import Post, User, Follow
from django.db.models import Max
from json import dumps,loads
from django.urls import reverse
import os, pathlib, unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait

class NetworkTestCase(TestCase):
    #Set up some instances for testing
    def setUp(self):
        # User
        user1=User.objects.create_user('user1','user1@gmail.com','user1password')
        user2=User.objects.create_user('user2','user2@gmail.com','user2password')
        user3=User.objects.create_user('user3','user3@gmail.com','user3password')
        user4=User.objects.create_user('user4','user4@gmail.com','user4password')
        # Follow relationships
        follow1=Follow.objects.create(from_user=user1, to_user=user2)
        follow2=Follow.objects.create(from_user=user1, to_user=user3)
        follow3=Follow.objects.create(from_user=user2, to_user=user3)
        # Posts
        post1=Post.objects.create(author=user1,content='Content 1')
        post2=Post.objects.create(author=user2,content='Content 2')
        post3=Post.objects.create(author=user3,content='Content 3')
        post4=Post.objects.create(author=user1,content='Content 4')
        # Replies
        post1.replies.add(post3)
        post1.replies.add(post2)
        post1.save() # post 1 has 2 replies - post 2 & 3
        # Likes
        post3.likes = 3
        post3.save() # post 3 has 3 likes 

    ################    Model Field Testing    ################
    # Check that model fields are working correctly
    # Test 1
    def test_following_count(self):
        '''Test 1: Check that the following relationship works'''
        curr_user = User.objects.get(username='user1')
        self.assertEqual(curr_user.following.count(),2) #User1 should be identified as following 2 people
    
    # Test 2
    def test_follower_count(self):
        '''Test 2: Check that the following relationship works'''
        curr_user = User.objects.get(username='user3')
        self.assertEqual(curr_user.follower.count(),2) #User3 should be identified to have 2 followers
    
    # Test 3
    def test_replies1(self): 
        '''Test 3: Check that the reply relationship works. 
        Test_replies1 accesses replies via the related name 'related_to'.'''
        user3=User.objects.get(username='user3')
        post3=Post.objects.get(author=user3,content='Content 3')
        self.assertEqual(post3.related_to.count(),1)

    # Test 4
    def test_replies2(self): #through the related name 'related_to'
        '''Test 4: Check that the reply relationship works. 
        Test_replies2 accesses replies via the model field 'replies'.'''
        user1=User.objects.get(username='user1')
        post1=Post.objects.get(author=user1,content='Content 1')
        self.assertEqual(post1.replies.count(),2)

    ################    Client Testing - GET Request    ################
    # Test 5: Index View
    def test_index(self):
        '''Test 5: Check the index view and its contexts.'''
        # Set up client to make requests
        c = Client () 
        # Send get request to index page and store response
        response = c.get('') 
        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)
        # Make sure there are 3 posts in the context
        self.assertEqual(response.context['posts'].count(), 4)

    # Test 6: Post View
    def test_post_page(self):
        '''Test 6: Check the post view for a post page that exists within the database (Status code = 200)'''
        # Get a post
        user1=User.objects.get(pk=1)
        post1=Post.objects.get(author=user1,content='Content 1')
        # Set up client to make requests
        c = Client () 
        # Send get request to the post
        response = c.get(f"/post/{post1.id}") 
        
        self.assertEqual(response.context['main_post'],post1)
        self.assertEqual(response.status_code, 200)

    # Test 7: User_profile View
    def test_user_profile(self):
        '''Test 7: Check the user_profile view and its contexts.'''
        # Get a user whose profile we will check
        user1=User.objects.get(pk=1)
        # Set up client to make requests
        c = Client () 
        # Send get request to index page and store response
        response = c.get(f'/user/{user1.username}') 
        
        # Make sure there are 2 posts and the correct profile owner selected in the context
        self.assertEqual(response.context['posts'].count(), 2)
        self.assertEqual(response.context['profile_owner'],user1)
        
        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)

    # Test 8: Following View
    def test_following(self):
        '''Test 8: Check the following page and its contexts.'''
        # Login user to access following page
        c = Client()
        login = c.login(username='user1', password='user1password')
        response = c.get(f'/following')
         # Make sure there are 2 following posts (one from user2 and one from user3) 
        self.assertEqual(len(response.context['posts']), 2)
        # Make sure status code is 200
        self.assertEqual(response.status_code, 200)


    ################    Client Testing - POST Requests   ################
    # Test 9: Exact Search 
    def test_search1(self):
        '''Test 9: Create an exact search for user1.
        Should be redirected (Status=302) to user1's profile'''
        
        c = Client()
        response = c.post('/search', {'search':'user1'})

        # Should return status code = 302 (redirect)
        self.assertEqual(response.status_code, 302)
        # and, redirect to user profile ('/user/user1')
        self.assertEqual(response['location'], '/user/user1')
    
    # Test 10: Blank Search 
    def test_search2(self):
        '''Test 10: Create a blank search.
        Should be redirected (Status=302) to the index/home page'''
        
        c = Client()
        response = c.post('/search', {'search':''})

        # Should return the index page (url = '')
        self.assertEqual(response['location'], '/')
        # and, status code = 302 (redirect)
        self.assertEqual(response.status_code, 302)
    
    # Test 11: Word Search 
    def test_search3(self):
        '''Test 11: Create a search with word 'user'.
        Should render the search result page showing 4 searches (user1-4)
        Status = 200'''
        
        c = Client()
        response = c.post('/search', {'search':'user'})
        
        # Should return 4 search results
        self.assertEqual(len(response.context['potential']), 4)
        # and, status code = 200
        self.assertEqual(response.status_code, 200)

    #Test 12: Create new post
    def test_new(self):
        '''Test 12: Create a new post from user4's account.'''
        
        content = 'Hello! What a beautiful day.'
        c = Client()
        #login into user 4's acc
        login = c.login(username='user4', password='user4password')
        response_json = c.post('/new', {'content':content}, content_type='application/json')
        response = response_json.content.decode('utf-8') #a string: {"id_created": 5, "message": "Post created successfully"}

        # Should return success message
        self.assertIn("Post created successfully", response)
        # and, status code = 201
        self.assertEqual(response_json.status_code, 201)
        # lastly, check the model field has added the post
        user4 = User.objects.get(username = 'user4')
        posts = Post.objects.filter(author = user4)
        self.assertEqual(posts.count(),1)

    ################    Client Testing - PUT Request    ################
    #Test 13: Follow a user
    def test_follow(self):
        '''Test 13: Follow user4 from user1's account'''
        
        c = Client()
        # Login into user 1's acc
        login = c.login(username='user1', password='user1password')
        # Follow user4
        response = c.put('/user/user1',{'follow':'user4'}, content_type='application/json')
        # Should return success message
        self.assertIn("followed user4 successfully.", response.content.decode('utf-8'))
        # and, status code = 201
        self.assertEqual(response.status_code, 201)
        # lastly, user4 should not be in user1's following field
        user1 = User.objects.get(username = 'user1')
        user4 = User.objects.get(username = 'user4')
        self.assertIn(user4, user1.relationship.all())

    #Test 14: Unfollow a user
    def test_unfollow(self):
        '''Test 14: Unfollow user3 from user1's account'''
        
        c = Client()
        # Login into user 1's acc
        login = c.login(username='user1', password='user1password')
        # Follow user4
        response = c.put('/user/user1',{'unfollow':'user3'}, content_type='application/json')
        # Should return success message
        self.assertIn("unfollowed user3 successfully.", response.content.decode('utf-8'))
        # and, status code = 201
        self.assertEqual(response.status_code, 201)
        # lastly, user3 should not be in user1's following field
        user1 = User.objects.get(username = 'user1')
        user3 = User.objects.get(username = 'user3')
        self.assertNotIn(user3, user1.relationship.all())
    
    #Test 15: Like a post
    def test_like(self):
        '''Test 15: Like post3 with user1's account'''
        c = Client()
        # Login into user 1's acc
        login = c.login(username='user1', password='user1password')
        # Like post 
        response = c.put('/post/3',{'like':True}, content_type='application/json')

        # Should return success message
        self.assertIn("post updated successfully.", response.content.decode('utf-8'))
        # and, status code = 201
        self.assertEqual(response.status_code, 201)
        # lastly, Post 3 should have 3+1=4 likes
        post3 = Post.objects.get(id=3)
        self.assertEqual(post3.likes,4)

    #Test 16: Unlike a post
    def test_unlike(self):
        '''Test 16: Unlike post3 with user1's account'''
        c = Client()
        # Login into user 1's acc
        login = c.login(username='user1', password='user1password')
        # Unlike post 
        response = c.put('/post/3',{'like':False}, content_type='application/json')

        # Should return success message
        self.assertIn("post updated successfully.", response.content.decode('utf-8'))
        # and, status code = 201
        self.assertEqual(response.status_code, 201)
        # lastly, Post 3 should have 3-1=2 likes
        post3 = Post.objects.get(id=3)
        self.assertEqual(post3.likes,2)
    
    #Test 17: Reply to a post
    def test_reply(self):
        '''Test 17: Assign post4 ({'reply' = 4}) as a reply to post1 using user1's account'''
        c = Client()
        # Login into user 1's acc
        login = c.login(username='user1', password='user1password')
        # Reply to post1
        response = c.put('/post/1',{'reply':4}, content_type='application/json')
        
        # Should return success message
        self.assertIn("post updated successfully.", response.content.decode('utf-8'))
        # and, status code = 201
        self.assertEqual(response.status_code, 201)
        # lastly, Post 1 should have 2(set-up)+1(test17) = 3 replies
        post1 = Post.objects.get(id=1)
        self.assertEqual(post1.replies.count(),3)

        
##################    Browser Testing - Selenium    #####################
def file_uri(filename):
    return pathlib.Path(os.path.abspath(f'network/templates/network/{filename}')).as_uri()

# Login to start testing
driver = webdriver.Chrome(executable_path='./network/chromedriver')
driver.get('http://127.0.0.1:8000/login')
username = driver.find_element_by_name("username")
username.send_keys('user1')
password = driver.find_element_by_name("password")
password.send_keys('user1password')
driver.find_element_by_class_name("login_button").click()

class WebpageTests(unittest.TestCase):
    # Run 'python manage.py runserver' in the terminal first 
    

    def test_NewBubble(self):
        ''' Test 1: Test the posting function via the 'New Bubble' button in the sidebar. '''
        # Click on New Bubble in the sidebar
        button = driver.find_element_by_id("new_bubble").click()

        # Make and submit new post
        textarea = driver.find_element_by_id("overlay_text")
        textarea.send_keys('New post from post bubble')
        driver.find_element_by_id("overlay_button").click()

        # Check that it was posted correctly (aka the latest post on the feed)
        latest_post = driver.find_element_by_xpath("//div[@id='post_view']/descendant::p[1]")
        self.assertEqual(latest_post.text,'New post from post bubble')

    def test_newpost_home(self):
        ''' Test 2: Test the posting function via the homepage. '''
        # Make and submit new post
        textarea = driver.find_element_by_id('textarea_new')
        textarea.send_keys('New post from home page.')
        driver.find_element_by_id("submit_new").click()

        # Check that it was posted correctly (aka the latest post on the feed)
        latest_post = driver.find_element_by_xpath("//div[@id='post_view']/descendant::p[1]")
        self.assertEqual(latest_post.text,'New post from home page.')

    def test_like_button(self):
        ''' Test 3: Test the like button. '''
        # Clicking once on the like button should increase the like count
        like = driver.find_elements_by_class_name('heart_icon')[0]
        ori_like_number = int(driver.find_elements_by_xpath("//span[contains(@id,'like_count')]")[0].text)
        # Clicking the like button will increase the post like by 1
        like.click()
        self.assertEqual(ori_like_number+1, int(driver.find_elements_by_xpath("//span[contains(@id,'like_count')]")[0].text))
        # Clicking it again will cause user1 to unlike the post, bringing like count back to original
        like.click()
        self.assertEqual(ori_like_number, int(driver.find_elements_by_xpath("//span[contains(@id,'like_count')]")[0].text))

    def test_mainpost(self):
        ''' Test 4: Test that clicking a post div will bring you to the main post page '''
        # Post id
        post = driver.find_elements_by_class_name('post')[0]
        post_id = post.get_attribute('data-post_id')
        post.click()
        self.assertEqual(driver.current_url,f'http://127.0.0.1:8000/post/{post_id}')

        driver.get('http://127.0.0.1:8000') # go back to home page

    def test_reply(self):
        ''' Test 5: Test the reply function. '''
        # Click on reply button in a post
        button = driver.find_elements_by_class_name('reply_icon')[0]
        button.click()
        # Post id
        post_id = button.get_attribute('data-post_id')
        # Number of replies
        ori_reply_count = int(driver.find_element_by_id(f'reply_count{post_id}').text)

        # Make and submit a reply
        textarea = driver.find_element_by_id("overlay_text")
        textarea.send_keys('This is a test reply.')
        driver.find_element_by_id("overlay_button").click()

        # Check that it was posted correctly (aka the latest post on the feed)
        latest_post = driver.find_element_by_xpath("//div[@id='post_view']/descendant::p[1]")
        self.assertEqual(latest_post.text,'This is a test reply.')

        # Reply count should increase by 1
        self.assertEqual(ori_reply_count+1, int(driver.find_element_by_id(f'reply_count{post_id}').text))

        # Check that it is posted as a reply in the main post
        driver.get(f'http://127.0.0.1:8000/post/{post_id}') # go to the main post
        latest_post = driver.find_element_by_xpath("//div[@id='post_view']/descendant::p[1]") # find the latest reply
        self.assertEqual(latest_post.text,'This is a test reply.')

        driver.get('http://127.0.0.1:8000') # go back to home page
    
    def test_follow(self):
        ''' Test 6: Test the follow function (and search function at sidebar). '''
        # Search for user2's account
        search = driver.find_element_by_id("search_user")
        search.send_keys("user2")
        search.send_keys(Keys.ENTER)
        # Should be directed to user2's profile page
        self.assertEqual(driver.current_url,f'http://127.0.0.1:8000/user/user2')

        # Click follow
        follow = driver.find_element_by_id('follow_button')
        ori_follow_count = int(driver.find_element_by_id('profile_follower').text)

        # Follow count should increase by 1
        follow.click()
        self.assertEqual(ori_follow_count+1, int(driver.find_element_by_id('profile_follower').text))

        # Click follow again will cause user1 to unfollow user 2
        follow.click()
        self.assertEqual(ori_follow_count, int(driver.find_element_by_id('profile_follower').text))    

        driver.get('http://127.0.0.1:8000') # go back to home page


# Code will only run if this file is run directly (the main)
if __name__ == "__main__":
    unittest.main()






        




    

