class Notification :
    def __init__(self, sender, receiver):
        self.sender = sender
        self.receiver = receiver

class LikeNotification(Notification):
    def __init__(self, sender, receiver, post):
        super().__init__(sender, receiver)
        self.type = "Like"
        self.post = post
        self.notification_message = f"{self.sender.username} liked your post: {self.post.post_id}."

    def send(self):
        self.receiver.notifications.append(self.notification_message)

class CommentNotification(Notification):
    def __init__(self, sender, receiver, post, comment):
        super().__init__(sender, receiver)
        self.type = "Comment"
        self.post = post
        self.comment = comment
        self.notification_message = f"{self.sender.username} commented on your post: {self.post.post_id}. Comment: {self.comment}"

    def send(self):
        self.receiver.notifications.append(self.notification_message)

class FollowRequestNotification(Notification):
    def __init__(self, sender, receiver):
        super().__init__(sender, receiver)
        self.type = "FollowRequest"
        self.notification_message = f"{self.sender.username} has sent you a follow request."

    def send_request(self):
        self.receiver.notifications.append(self.notification_message)
        self.receiver.pending_requests.append(self.sender)

    def answer_request(self, accepted):
        if accepted:
            #add follower and following
            self.sender.following.append(self.receiver)
            self.receiver.followers.append(self.sender)
            #remove the request from pending and notifications
            self.receiver.pending_requests.remove(self.sender)
            self.receiver.notifications.remove(self)
            #add notifications
            self.sender.notifications.append(f"You are now following {self.receiver.username}.")
            self.receiver.notifications.append(f"{self.sender.username} is now following you.")
        else:
            self.sender.notifications.append(f"{self.receiver.username} declined your follow request.")

class NewFollowerNotification(Notification):
    def __init__(self, sender, receiver):
        super().__init__(sender, receiver)
        self.type = "NewFollower"
        self.notification_message = f"{self.sender.username} is now following you."

    def send(self):
        if self.receiver.is_public :
            self.sender.followers.append(self.receiver)
            self.receiver.following.append(self.sender)
            self.receiver.notifications.append(self.notification_message)


