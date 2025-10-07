import datetime
from better_profanity import profanity

class Post:
    def __init__(self, content, poster_username):
        self.poster_username = poster_username
        self.content = self.automoderate(content)
        self.date = datetime.datetime.now()
        self.likes = 0
        self.comments = {}
        self.id_comment = 0

    def automoderate(self, content):
        filtered_content = profanity.censor(content)
        return filtered_content
    
    def display_post(self):
        print(f"Post by {self.poster_username} on {self.date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Content: {self.content}")
        print(f"Likes: {self.likes}")
        if self.comments:
            print("Comments:")
            for commenter, details in self.comments.items():
                comment_date = details['date'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"{self.id_comment}- {commenter} on {comment_date}: {details['comment']}")
        else:
            print("No comments yet.")

    def edit_post(self, new_content):
        self.content = self.automoderate(new_content)
        self.date = datetime.datetime.now()  # Update the date to the edit time

    def add_like(self):
        self.likes += 1

    def remove_like(self):
        if self.likes > 0:
            self.likes -= 1

    def add_comment(self, commenter_username, comment):
        self.id_comment += 1
        self.comments[self.id_comment] = {
            "username": commenter_username,
            "comment": self.automoderate(comment),
            "date": datetime.datetime.now()
        }

    def remove_comment(self, id_comment, deleter_username):
        if id_comment in self.comments and (self.comments[id_comment]['username'] == deleter_username or deleter_username == self.poster_username):
            del self.comments[id_comment]

    