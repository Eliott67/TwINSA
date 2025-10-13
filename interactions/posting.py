import datetime
from better_profanity import profanity
from user import User
from users_db import UsersDatabase

class Post:
    def __init__(self, content, poster_username, database):
        self.poster_username = poster_username
        self.user = database.get_user(self.poster_username)
        self.content = self.automoderate(content)
        self.date = datetime.datetime.now()
        self.likes = []
        self.comments = {}
        self.id_comment = 0
        self.post_id = self.user.posts.__len__() + 1
        self.update_poster_list_posts()

    def update_poster_list_posts(self):
        if self not in self.user.posts:
            self.user.add_post(self)
        else:
            self.user.delete_post(self)
            self.user.add_post(self)

    def update_likes(self):
        self.user.likes[self.post_id] = len(self.likes)
        
    def automoderate(self, content):
        filtered_content = profanity.censor(content)
        return filtered_content
    
    def display_post(self):
        print(f"Post by {self.poster_username} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Content: {self.content}")
        print(f"Likes: {len(self.likes)}")
        if self.comments:
            print("Comments:")
            for id_comment, comment_info in self.comments.items():
                comment_date = comment_info['date'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"  [{id_comment}] {comment_info['username']} on {comment_date}: {comment_info['comment']}")
        else:
            print("No comments yet.")

    def edit_post(self, new_content):
        self.content = self.automoderate(new_content)
        self.date = datetime.datetime.now()  # Update the date to the edit time
        self.update_poster_list_posts()

    def add_like(self,username):
        #only one like per user
        if username not in self.likes:
            self.likes.append(username)
        self.update_likes()

    def remove_like(self, username):
        if username in self.likes:
            self.likes.remove(username)
        self.update_likes()

    def add_comment(self, commenter_username, comment):
        self.id_comment += 1
        self.comments[self.id_comment] = {
            "username": commenter_username,
            "comment": self.automoderate(comment),
            "date": datetime.datetime.now()
        }
        self.update_poster_list_posts()

    def remove_comment(self, id_comment, deleter_username):
        if id_comment in self.comments.keys() and (self.comments[id_comment]['username'] == deleter_username or deleter_username == self.poster_username):
            del self.comments[id_comment]
            self.update_poster_list_posts()

    def edit_comment(self, id_comment, new_comment, editor_username):
        if id_comment in self.comments.keys() and self.comments[id_comment]['username'] == editor_username:
            self.comments[id_comment]['comment'] = self.automoderate(new_comment)
            self.comments[id_comment]['date'] = datetime.datetime.now()  # Update the date to the edit time
            self.update_poster_list_posts()

