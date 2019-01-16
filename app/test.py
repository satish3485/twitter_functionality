import os
import unittest
import main

app = main.app
db = main.db
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

class BasicTests(unittest.TestCase):

    ############################
    #### setup and teardown ####
    ############################

    # executed prior to each test
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.app = app.test_client()
        userdb = db["user"]
        tweetdb = db["tweet"]
        replydb = db["reply"]
        tweetdb.drop()
        userdb.drop()
        replydb.drop()
        userdb = db["user"]
        tweetdb = db["tweet"]
        replydb = db["reply"]


    # executed after each test
    def tearDown(self):
        pass

    ###############
    #### tests ####
    ###############
    # test main page
    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    ########################
    #### helper methods ####
    ########################
    def post_method(self, url, data):
        return self.app.post(
        url,
        data=data,
        follow_redirects=True
        )

    def get_method(self, url):
        return self.app.get(
        url,
        follow_redirects=True
        )


    # test user login without create user
    def test_logIn_without_user(self):
        data={'username':'kumar', 'password':1234}
        response = self.post_method('/login',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User Name or Password are incorrect, try again', response.data)

    # test user signUp
    def test_user_signup(self):
        data={'username':'kumar', 'password':1234}
        response = self.post_method('/signup',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are successfully signup', response.data)

    # test user signUp with missing parameter password
    def test_user_signup_missing_parameter_password(self):
        data={'username':'kumar'}
        response = self.post_method('/signup',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username or password', response.data)

    # test user signUp with missing parameter username
    def test_user_signup_missing_parameter_username(self):
        data={'password':1234}
        response = self.post_method('/signup',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username or password', response.data)

    # test user signUp with missing parameter username and password
    def test_user_signup_missing_parameter_signup(self):
        data={}
        response = self.post_method('/signup',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username or password', response.data)

        # test user signUp with same name again
    def test_user_signup_with_same_name(self):
        self.test_user_signup()
        data={'username':'kumar', 'password':1234}
        response = self.post_method('/signup',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User Name alredy taken', response.data)

    # test user signUp with new user name
    def test_user_signup_with_new_name(self):
        self.test_user_signup()
        data={'username':'kumars', 'password':1234}
        response = self.post_method('/signup',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are successfully signup', response.data)

    # test user signUp if user already login
    def test_user_signup_while_user_already_login(self):
        self.test_user_signup()
        data={'username':'kumar', 'password':1234}
        response = self.post_method('/signup',data)
        self.assertEqual(response.status_code, 200)

    # test user login
    def test_logIn_user(self):
        self.test_user_signup()
        data={'username':'kumar', 'password':1234}
        response = self.post_method('/login',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello, kumar', response.data)

    # test user login with missing parameter password
    def test_user_login_missing_parameter_password(self):
        data={'username':'kumar'}
        response = self.post_method('/login',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username or password', response.data)

    # test user login with missing parameter username
    def test_user_login_missing_parameter_username(self):
        data={'password':1234}
        response = self.post_method('/login',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username or password', response.data)

    # test user login with missing parameter username and password
    def test_user_signup_missing_parameter_login(self):
        data={}
        response = self.post_method('/login',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username or password', response.data)

    # test user logout
    def test_user_logout(self):
        self.test_logIn_user()
        response = self.get_method('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are successfully logout.', response.data)

    # test user log out without log in
    def test_user_logout_without_login(self):
        response = self.get_method('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are not Log In.', response.data)

    # test follow without log in
    def test_user_follow_without_login(self):
        data = {'username':'kumar'}
        response = self.post_method('/follow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are not Log In. You can not follow', response.data)

    # test user follow with missing parameter username
    def test_user_follow_missing_parameter_title(self):
        self.test_logIn_user()
        data={}
        response = self.post_method('/follow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username', response.data)

    # test follow user that does not exist
    def test_user_follow_user_not_exist(self):
        self.test_logIn_user()
        data = {'username':'kumarm'}
        response = self.post_method('/follow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No user with this User Name ', response.data)

    # test follow user ownself
    def test_user_follow_user_ownself(self):
        self.test_logIn_user()
        data = {'username':'kumar'}
        response = self.post_method('/follow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You can not follow yourself.', response.data)

    # test user follow another user
    def test_user_follow(self):
        data={'username':'kumars', 'password':1234}
        response = self.post_method('/signup',data)
        self.test_logIn_user()
        data = {'username':'kumars'}
        response = self.post_method('/follow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are successfully following', response.data)

    # test user follow already to user
    def test_user_follow_already_user(self):
        self.test_user_follow()
        data = {'username':'kumars'}
        response = self.post_method('/follow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are already follow kumars', response.data)

    # test unfollow user that does not exist
    def test_user_unfollow_user_not_exist(self):
        self.test_logIn_user()
        data = {'username':'kumarm'}
        response = self.post_method('/unfollow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No user with this User Name ', response.data)

    # test user unfollow with missing parameter username
    def test_user_unfollow_missing_parameter_title(self):
        self.test_logIn_user()
        data={}
        response = self.post_method('/unfollow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter username', response.data)

    # test unfollow user ownself
    def test_user_unfollow_user_ownself(self):
        self.test_logIn_user()
        data = {'username':'kumar'}
        response = self.post_method('/unfollow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You can not unfollow yourself.', response.data)

    # test user unfollow another user
    def test_user_unfollow(self):
        self.test_user_follow()
        data = {'username':'kumars'}
        response = self.post_method('/unfollow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are successfully unfollow', response.data)

    # test user follow already to user
    def test_user_unfollow_already_user(self):
        self.test_user_unfollow()
        data = {'username':'kumars'}
        response = self.post_method('/unfollow',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are not follow kumars', response.data)

    # test user create tweet
    def test_user_create_tweet(self):
        self.test_logIn_user()
        data = {'title':'hello', 'message':'Hello world !'}
        response = self.post_method('/create',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You tweet succesfully', response.data)

    # test user create tweet with missing parameter title
    def test_user_create_missing_parameter_title(self):
        self.test_logIn_user()
        data={'message':'Hello world !'}
        response = self.post_method('/create',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter title or message', response.data)

    # test user create tweet with missing parameter message
    def test_user_create_missing_parameter_title(self):
        self.test_logIn_user()
        data={'title':'hello'}
        response = self.post_method('/create',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter title or message', response.data)

    # test user create tweet with missing parameter message and title
    def test_user_create_missing_parameter_both(self):
        self.test_logIn_user()
        data={}
        response = self.post_method('/create',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter title or message', response.data)

    # test user create tweet without log in
    def test_user_create_tweet_without_logIn(self):
        data = {'title':'hello', 'message':'Hello world !'}
        response = self.post_method('/create',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are not Log In. You can not tweet', response.data)

    # test user create tweet with same title
    def test_user_create_tweet_with_duplicate_title(self):
        self.test_user_create_tweet()
        data = {'title':'hello', 'message':'Hello world !'}
        response = self.post_method('/create',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please change the title, because it is alrady used', response.data)

    # test read read tweet
    def test_user_read_tweet(self):
        self.test_user_create_tweet()
        data = {'title':'hello'}
        response = self.post_method('/read',data)
        self.assertEqual(response.status_code, 200)

    # test user read tweet with missing parameter title
    def test_user_read_missing_parameter_title(self):
        data={}
        response = self.post_method('/read',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter title', response.data)

    # test read tweet without login
    def test_user_read_tweet_without_login(self):
        data = {'title':'hello'}
        response = self.post_method('/read',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are not Log In. You can not read tweet', response.data)

    # test read tweet not found
    def test_user_read_tweet_not_found(self):
        self.test_logIn_user()
        data = {'title':'hello'}
        response = self.post_method('/read',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'There are not tweet with title hello', response.data)

    # test user delete tweet
    def test_user_delete_tweet(self):
        self.test_user_create_tweet()
        data = {'title':'hello'}
        response = self.post_method('/delete',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are successfully delete tweet', response.data)

    # test user delete tweet with missing parameter title
    def test_user_read_missing_parameter_title(self):
        self.test_logIn_user()
        data={}
        response = self.post_method('/delete',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You missed parameter title', response.data)

    # test user delete tweet without log in
    def test_user_delete_tweet_without_logIn(self):
        self.test_user_create_tweet()
        self.get_method('/logout')
        data = {'title':'hello'}
        response = self.post_method('/delete',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You are not Log In. You can not delete tweet', response.data)

    # test user delete tweet if login user not created
    def test_user_delete_tweet_authority(self):
        self.test_user_delete_tweet_without_logIn()
        data={'username':'kumars', 'password':1234}
        self.post_method('/signup',data)
        self.post_method('/login',data)
        data = {'title':'hello'}
        response = self.post_method('/delete',data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You do not have this tweet', response.data)




if __name__ == "__main__":
    unittest.main()
