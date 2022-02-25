from __future__ import print_function

import datetime

from firebase_admin import messaging


def send_to_token(registration_token, data):
    # registration_token is a string
    # use this when sending to single token, which is very rare instead, opt to send_multicast below

    # [START send_to_token]
    # This registration token comes from the client FCM SDKs.

    # See documentation on defining a message payload.
    message = messaging.Message(
        data=data,
        token=registration_token,
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print("Successfully sent message:", response)
    # [END send_to_token]


def send_to_topic(topic, data):
    # [START send_to_topic]
    # The topic name can be optionally prefixed with "/topics/".

    # See documentation on defining a message payload.
    message = messaging.Message(
        data=data,
        topic=topic,
    )

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send(message)
    # Response is a message ID string.
    print("Successfully sent message:", response)
    # [END send_to_topic]


def send_to_condition(data):
    # [START send_to_condition]
    # Define a condition which will send to devices which are subscribed
    # to either the Google stock or the tech industry topics.
    condition = "'stock-GOOGLE' in topics || 'industry-tech' in topics"

    # See documentation on defining a message payload.
    message = messaging.Message(
        notification=messaging.Notification(data),
        condition=condition,
    )

    # Send a message to devices subscribed to the combination of topics
    # specified by the provided condition.
    response = messaging.send(message)
    # Response is a message ID string.
    print("Successfully sent message:", response)
    # [END send_to_condition]


def send_dry_run(token, data):
    message = messaging.Message(
        data=data,
        token=token,
    )

    # [START send_dry_run]
    # Send a message in the dry run mode.
    response = messaging.send(message, dry_run=True)
    # Response is a message ID string.
    print("Dry run successful:", response)
    # [END send_dry_run]


def android_message(topic, data, priority=None):
    """Send a notification to android devices subscribed to passed FCM topic.

    Args:
        topic: Name of the topic to send notification to.
        data: Dict of Notification args. {title, body, icon, color}
        priority: Priority of the message (optional). Must be one of ``high`` or ``normal``.

    Returns:
        sent message instance

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    message = messaging.Message(
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority="normal" if priority not in ["normal", "high"] else priority,
            notification=messaging.AndroidNotification(
                title=data.get("title", "NamasteNepal"),
                body=data.get("body", ""),
                icon=data.get("icon"),
                color=data.get("color", "red"),
            ),
        ),
        topic=topic,
    )
    # [END android_message]
    return message


def apns_message(topic, data, priority):
    """Send a notification to iOS devices subscribed to passed FCM topic.

    Args:
        topic: Name of the topic to send notification to.
        data: Dict of Notification args. {title, body}
        priority: Priority of the message (optional). Must be one of ``0`` or ``5`` or ``10`` defaults 10.

    Returns:
        sent message instance

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    message = messaging.Message(
        apns=messaging.APNSConfig(
            headers={"apns-priority": priority},
            payload=messaging.APNSPayload(
                aps=messaging.Aps(
                    alert=messaging.ApsAlert(
                        title=data.get("title", "Namaste Nepal"),
                        body=data.body("body"),
                    ),
                    badge=42,
                ),
            ),
        ),
        topic=topic,
    )
    # [END apns_message]
    return message


def webpush_message(topic, data):
    """Send a notification to web devices subscribed to passed FCM topic.

    Args:
        topic: Name of the topic to send notification to.
        data: Dict of Notification args. {title, body, icon}

    Returns:
        sent message instance

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    message = messaging.Message(
        webpush=messaging.WebpushConfig(
            notification=messaging.WebpushNotification(
                title=data.get("title", "NamasteNepal"),
                body=data.get("body", ""),
                icon=data.get("icon"),
            ),
        ),
        topic=topic,
    )
    # [END webpush_message]
    return message


def all_platforms_message(topic, data):
    """Send a notification to devices of all platforms subscribed to passed FCM topic.

    Args:
        topic: Name of the topic to send notification to.
        data: Dict of Notification args. {title, body, icon}

    Returns:
        sent message instance

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    # [START multi_platforms_message]
    message = messaging.Message(
        notification=messaging.Notification(
            title=data.get("title", "NamasteNepal"),
            body=data.get("body", ""),
        ),
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority="normal",
            notification=messaging.AndroidNotification(
                icon="stock_ticker_update", color="red"
            ),
        ),
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(badge=42),
            ),
        ),
        topic=topic,
    )
    # [END multi_platforms_message]
    return message


def subscribe_to_topic(topic, tokens):
    """Send a notification to devices of all platforms subscribed to passed FCM topic.

    Args:
        topic: Name of the topic to subscribe to.
        tokens: List of tokens to subscribe

    Returns:
        TopicManagementResponse: instance of response

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    # Subscribe the devices corresponding to the registration tokens to the topic.
    response = messaging.subscribe_to_topic(tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(
        f"{response.success_count} of {len(tokens)} "
        f"provided tokens were subscribed successfully"
    )

    return response
    # [END subscribe]


def unsubscribe_from_topic(topic, tokens):
    """Send a notification to devices of all platforms subscribed to passed FCM topic.

    Args:
        topic: Name of the topic to subscribe to.
        tokens: List of tokens to subscribe

    Returns:
        ``TopicManagementResponse`` instance of response

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    # [START unsubscribe]
    # Unsubscribe the devices corresponding to the registration tokens from the topic.
    response = messaging.unsubscribe_from_topic(tokens, topic)
    # See the TopicManagementResponse reference documentation
    # for the contents of response.
    print(
        f"{response.success_count} of {len(tokens)} "
        f"provided tokens were unsubscribed successfully"
    )

    return response
    # [END unsubscribe]


def send_all(topics=None, tokens=None, data=None):
    """Send a notification to devices of all platforms subscribed to passed FCM topic.

    Args:
        topics: List of topics to send notification to.
        tokens: List of tokens to send notification to.
        data: Dict of Notification args. {title, body, icon}

    Returns:
        sent message instance

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    # [START send_all]
    # Create a list containing up to 500 messages.
    messages = []
    if topics:
        for topic in topics:
            messages.append(
                messaging.Message(
                    notification=messaging.Notification(
                        title=data.get("title", "Namaste Nepal"),
                        body=data.get("body"),
                        image=data.get("image"),
                    ),
                    topic=topic,
                )
            )
    if tokens:
        for token in tokens:
            messages.append(
                messaging.Message(
                    notification=messaging.Notification(
                        title=data.get("title", "Namaste Nepal"),
                        body=data.get("body"),
                        image=data.get("image"),
                    ),
                    token=token,
                )
            )

    response = messaging.send_all(messages)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print(f"{response.success_count} messages were sent successfully")

    return response
    # [END send_all]


def send_multicast(tokens, data):
    """Send a notification to devices of all platforms subscribed to passed FCM topic.

    Args:
        tokens: List of tokens to send notification to.
        data: Dict of Notification args. {title, body, icon}

    Returns:
        sent message instance

    Raises:
        FirebaseError: If an error occurs while communicating with instance ID service.
        ValueError: If the input arguments are invalid.
    """

    # [START send_multicast]
    # Create a list containing up to 500 registration tokens.
    # These registration tokens come from the client FCM SDKs.

    message = messaging.MulticastMessage(
        data=data,
        tokens=tokens,
    )
    response = messaging.send_multicast(message)
    # See the BatchResponse reference documentation
    # for the contents of response.
    print(f"{response.success_count} messages were sent successfully")

    return response
    # [END send_multicast]


def send_multicast_and_handle_errors(tokens):
    # [START send_multicast_error]
    # These registration tokens come from the client FCM SDKs.

    message = messaging.MulticastMessage(
        data={"score": "850", "time": "2:45"},
        tokens=tokens,
    )
    response = messaging.send_multicast(message)
    if response.failure_count > 0:
        responses = response.responses
        failed_tokens = []
        for idx, resp in enumerate(responses):
            if not resp.success:
                # The order of responses corresponds to the order of the registration tokens.
                failed_tokens.append(tokens[idx])
        print("List of tokens that caused failures: {0}".format(failed_tokens))
    # [END send_multicast_error]


# send_to_token(self)  # done
# subscribe_to_topic(self)  # done
# unsubscribe_from_topic(self)  # done
# send_to_topic(self)
# send_multicast(self)
# webpush_message(self)
# send_all(self)
# send_dry_run(self)
